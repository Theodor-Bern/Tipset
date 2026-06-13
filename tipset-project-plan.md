# Tipset — Summer 2026 Project Plan

A live prediction-league platform for the 2026 World Cup, built and operated for real users (Bärbys VM-tips / Bingoberra), then generalized for the autumn club season. The goal is not the app — it's learning the full lifecycle of real software: shipping under deadline, operating in production, and evolving a system while people depend on it.

**Hard constraint:** the group stage is running *now*. Round of 16 starts ~June 28. Phase 1 must be live before then.

---

## 1. Guiding principles (the Bender/DORA layer)

These are non-negotiable and apply from commit one:

- **Trunk-based development, small batches.** One `main` branch, short-lived feature branches merged within a day, every commit small enough to review in 5 minutes. (DORA capabilities #4 and #5.)
- **CI gates every merge.** Lint, type-check, and tests must pass before anything lands on `main`. `main` is always deployable.
- **A written AI stance in the repo** (`AI_POLICY.md`): what Claude Code / agents may do autonomously (scaffolding, tests, refactors with passing tests), what requires your review (schema migrations, auth code, scoring logic, anything touching money/points), and the rule that *you* must be able to explain every line that ships. (DORA capability #1.)
- **Validation over trust.** The scoring engine and deadline logic get property-based tests, not just example tests. API ingests are validated before they touch the database.
- **Blameless postmortems.** Every production incident during the tournament gets a short write-up: what happened, why, what changed. These become portfolio gold.
- **Intellectual control check.** At the end of each phase, draw the architecture diagram from memory, then compare with reality.

---

## 2. The stack (state of the art, June 2026)

### Backend
| Choice | Version | Why |
|---|---|---|
| Python | 3.14 (via uv) | Current default stable; free-threading maturing |
| uv | latest (0.11.x) | Lockfiles, Python management, 10–100x faster than pip; industry standard now |
| FastAPI | 0.136.x | Async, Pydantic v2, auto OpenAPI docs |
| SQLAlchemy 2.x + asyncpg | latest | The serious ORM; async from day one |
| Alembic | latest | Migrations as code — every schema change reviewed and versioned |
| Pydantic v2 | latest | Validation at every boundary (API in, API out, ingest) |
| Ruff + ty | latest | Astral's linter/formatter + type checker (FastAPI itself migrated mypy → ty) |
| pytest + hypothesis | latest | Unit/integration tests + property-based testing for the scoring engine |

### Frontend
| Choice | Version | Why |
|---|---|---|
| Next.js | 16.2.x | Turbopack default, React Compiler stable, App Router |
| React | 19.2 | Comes with Next 16; View Transitions for slick leaderboard animations |
| TypeScript | latest | Non-negotiable in 2026 |
| Tailwind CSS | v4 | Speed; mobile-first by default |
| TanStack Query | v5 | Server-state management, polling for live scores |
| shadcn/ui | latest | Accessible components without design overhead |

### Data & infrastructure
| Choice | Version | Why |
|---|---|---|
| PostgreSQL | 17/18 (latest stable) | The database. Use real constraints, transactions, indexes |
| Redis (or Postgres LISTEN/NOTIFY first) | 7.x | Caching + pub/sub for live updates — add only when needed |
| Docker + Compose | latest | Identical dev/prod environments |
| Hetzner VPS (CX22, ~€4/mo) | Ubuntu 24.04 | Cheap, EU-hosted; you know your way around Linux from OpenStack |
| Caddy | 2.x | Reverse proxy with automatic HTTPS — simpler than nginx + certbot |
| GitHub Actions | — | CI/CD: test → build image → push → deploy via SSH |
| Sentry (free tier) + Uptime Kuma | — | Error tracking + uptime alerts to your phone |

### Match data
- Primary: **football-data.org** (free tier, covers World Cup) or **API-Football** (broader, generous free tier). Verify World Cup 2026 coverage on day one — this is your riskiest external dependency.
- Design the ingest behind an interface (`ResultProvider`) so you can swap providers, and keep **manual result entry as the fallback** (admin UI). Tournaments don't wait for rate limits.

### AI-assisted workflow
- **Claude Code** as your pair: scaffolding, test generation, refactors — governed by `AI_POLICY.md`.
- You review every diff. You are the tech lead; the agent is the fast junior.

---

## 3. Architecture (Phase 1 target)

```
┌─────────────┐     ┌──────────────────────────────┐
│  Next.js 16 │────▶│  FastAPI                     │
│  (Vercel or │     │  /auth /predictions /matches │
│   same VPS) │     │  /leaderboard /admin         │
└─────────────┘     └──────────┬───────────────────┘
                               │ SQLAlchemy (async)
                    ┌──────────▼──────────┐
                    │  PostgreSQL          │
                    └──────────▲──────────┘
                               │
                    ┌──────────┴──────────┐
                    │  Ingest worker       │  ← APScheduler job:
                    │  (ResultProvider)    │    poll fixtures/results,
                    └─────────────────────┘    validate, upsert
```

Monorepo layout:

```
tipset/
├── AI_POLICY.md
├── docker-compose.yml
├── .github/workflows/ci.yml, deploy.yml
├── backend/
│   ├── pyproject.toml          # uv-managed
│   ├── alembic/
│   ├── app/
│   │   ├── api/                # routers
│   │   ├── core/               # config, security, deps
│   │   ├── models/             # SQLAlchemy
│   │   ├── schemas/            # Pydantic
│   │   ├── services/           # scoring engine, deadline logic
│   │   └── ingest/             # ResultProvider implementations
│   └── tests/
│       ├── unit/               # scoring properties (hypothesis)
│       └── integration/        # API + db (testcontainers)
├── frontend/
│   └── (Next.js app)
└── docs/
    ├── architecture.md
    ├── decisions/              # ADRs: short "why" records
    └── postmortems/
```

## 4. Core data model (Phase 1)

- **users** — id, email, display_name, password_hash (argon2), role
- **pools** — id, name, invite_code, owner_id, scoring_rules (JSONB)
- **pool_members** — pool_id, user_id, joined_at
- **teams** — id, name, fifa_code, group
- **matches** — id, external_id, home_team, away_team, kickoff_utc, stage, status, home_score, away_score
- **predictions** — id, user_id, match_id, pool_id, home_score, away_score, created_at, updated_at — *unique (user, match, pool); writes rejected after kickoff_utc, enforced in the service layer AND by a db constraint*
- **special_predictions** — champion pick, top scorer (set before knockout deadline)
- **score_events** — append-only log of points awarded (auditability: when someone disputes their points at a grill party, you replay the log)

Two deliberate hard parts:
1. **Deadline locking** — server-authoritative time, tested at the boundary (prediction at kickoff−1s accepted, kickoff+1s rejected).
2. **Scoring as a pure function** — `score(prediction, result, rules) -> points`, no I/O, property-tested (e.g., exact score always ≥ correct outcome ≥ wrong outcome; total points invariant under replay).

---

## 5. Phases & timeline

### Phase 1 — "Embarrassing but live" (now → June 27, before Round of 16)
**Goal: friends are submitting real predictions on a real URL.**

Week 1 (June 12–18):
- Repo, CI skeleton, Docker Compose (Postgres + backend + frontend), deploy pipeline to VPS with HTTPS. *Deploy "hello world" to production on day 2 — the pipeline before the product.*
- Data model + migrations. Seed all World Cup fixtures (from API or one-time manual import).
- Auth: register/login (argon2 + JWT in httpOnly cookies), invite-code pool joining.

Week 2 (June 19–27):
- Prediction submission UI with deadline locking; matches grouped by date, mobile-first.
- Scoring engine (pure function + hypothesis tests) and admin result entry.
- Leaderboard (computed from score_events). 
- Ingest worker polling results — but ship manual entry first; automation is an upgrade, not a blocker.
- **Launch to Bingoberra. Collect complaints. They are your backlog.**

Cut from Phase 1 without mercy: notifications, bracket visualization, stats, ML, design polish.

### Phase 2 — Operate & harden (June 28 → final, July 19)
**Goal: survive the knockout stage with real traffic spikes (everyone checks at 90'+).**

- Automated result ingestion with validation, retries, idempotent upserts.
- Live-ish updates: poll with TanStack Query; consider SSE for the leaderboard.
- Knockout-stage predictions (different scoring weights), champion pick reveal.
- Email or Telegram-bot reminders ("3 matches close in 2 hours, you've tipped 0").
- Observability: Sentry wired in, structured logging, Uptime Kuma alerting your phone.
- **Self-pentest weekend:** attack your own deployment — IDOR on prediction endpoints (can you read others' tips before kickoff? that's the cardinal sin of tipset apps), JWT handling, rate limiting login, SQL injection, the OWASP top 10 you know from Juice Shop. Write up findings + fixes in `docs/security-review.md`.
- Postmortem every incident.

### Phase 3 — The refactor (July 20 → mid-August)
**Goal: from "World Cup app" to "any competition" — the classic real-world generalization.**

- Extract competition-specific assumptions (group → knockout) into a competition model that also fits a league season (Allsvenskan, Premier League).
- Scoring rules fully data-driven per pool.
- Write ADRs for every structural decision made under pressure that you now revisit — this *is* the Bender "practices vs principles" exercise, lived.
- Add integration tests you skipped under deadline; measure where CI time goes.
- Relaunch for PL/Allsvenskan 2026–27 with returning users → you now have a *retention* problem, like real products do.

### Phase 4 — The distinctive layer (mid-August → September)
**Goal: the part nobody else's tipset app has.**

- Match prediction model (your xG background): pre-match probabilities shown next to each fixture.
- "Pool game theory" analytics: how contrarian is each member's bracket vs. the pool, expected pool-winning probability — productizing exactly what you did by hand for Bärbys VM-tips.
- Optional, very on-brand: export the model to ONNX and run win-probability inference browser-side.
- Public write-up: architecture, the postmortems, what 10 weeks of operating software taught you. This document is your strongest interview artifact.

---

## 6. Definition of done, per phase

- **P1:** ≥5 real users submitted predictions before a real kickoff; zero ways to tip after deadline; CI green on main; one-command redeploy.
- **P2:** results flow in without you touching the server; you got at least one alert on your phone and resolved it; security review documented.
- **P3:** a second competition runs on the same codebase with zero code forks; ADR log exists; architecture diagram from memory matches reality.
- **P4:** model probabilities live in the UI; write-up published (blog/GitHub README); repo is the centerpiece of your CV.

---

## 7. Risks & honest warnings

1. **Perfectionism in June.** The deadline is the feature. Ship the ugly version.
2. **The data API disappoints.** Mitigation: provider interface + manual admin entry from day one.
3. **Scope creep from friends.** Their feature requests go in the backlog, not the sprint. (Saying "not yet" to users is also a real-world skill.)
4. **AI writes faster than you review.** When you notice yourself rubber-stamping Claude Code diffs, stop — that is the exact code-review failure mode from the Bender talk, happening to you at n=1. Slow down, shrink the batches.
5. **Auth is the one place not to improvise.** Use boring, established patterns (argon2, httpOnly cookies, CSRF protection); have Claude Code explain rather than just generate.
