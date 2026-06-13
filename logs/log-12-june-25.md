Dag 1 – Fredag 12 juni

Idag har jag satt upp ett GitHub-repo som heter Tipset. Jag har också kopplat mitt lokala projekt till GitHub och börjat förstå hur Git, commits, remote repositories och SSH fungerar i praktiken.

Jag har på riktigt börjat förstå hur man utvecklar en webbserver med FastAPI och Uvicorn. Uvicorn är själva servern som lyssnar på en port och tar emot HTTP-requests från exempelvis webbläsaren eller curl. FastAPI är ramverket där jag definierar appens routes/endpoints och bestämmer vilken Python-funktion som ska köras när en viss URL anropas.

Jag har också lärt mig skillnaden mellan olika delar i en enkel backend. En endpoint som /health används för att kontrollera att servern fungerar, medan en endpoint som POST /notes kan ta emot JSON-data från klienten. Genom Pydantic kan FastAPI automatiskt validera att datan som skickas in har rätt struktur, till exempel att både title och content finns med.

Först sparade jag data i en vanlig Python-lista. Det gjorde att jag kunde förstå grundidén med att skapa och hämta objekt via API, men jag såg också begränsningen: när servern startades om försvann all data. Därefter började jag använda SQLite tillsammans med SQLAlchemy. Då sparas datan i en databasfil i stället för bara i programmets minne.

Jag har även börjat förstå vad ett ORM är. SQLAlchemy fungerar som ett lager mellan Python-koden och databasen. I stället för att skriva SQL direkt kan jag skapa Python-klasser, till exempel en Note-klass, som motsvarar en tabell i databasen. När jag skapar ett Note-objekt och kör db.add() och db.commit() översätter SQLAlchemy det till SQL och sparar raden i databasen.

En viktig insikt från idag är att en backend består av flera lager som samarbetar: Uvicorn tar emot requesten, FastAPI matchar requesten mot rätt endpoint, Pydantic validerar datan och SQLAlchemy hanterar kommunikationen med databasen. Det känns som att jag har börjat förstå vad som faktiskt händer bakom en enkel webbtjänst, inte bara hur man kopierar kod som fungerar.
