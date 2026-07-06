# LOOP.md — den autonome arbeidssyklusen

> Loop engineering-prinsippet: ikkje prompt agenten tur for tur — design
> loopen som promptar agenten. Kvar iterasjon har fem trekk:
> **discovery → handoff → verification → persistence → scheduling.**

Denne fila ER loop-prompten. Ein agent som får beskjeden «køyr loopen»
(via `/loop`, ein trigger, eller manuelt) skal følgje protokollen under,
utan å spørje om lov undervegs, til ein stoppvilkår er nådd.

## 0 · Invariantar (les før kvar iterasjon)

- Følg alle reglar i `CLAUDE.md` (nynorsk, branch, aldri slett, kjeldefest).
- Éin iterasjon = **éi avslutta arbeidseining** (45–90 min agentarbeid),
  ikkje «litt av alt».
- Alt arbeid skal ende i varige artefaktar: commit i git + rad i
  Notion-loggen. Arbeid som ikkje er persistert, har ikkje skjedd.

## 1 · Discovery — finn neste arbeid

1. Les `STATE.md`, `BACKLOG.md`, `LEARNINGS.md`, `git log --oneline -10`.
2. Vel **øvste udone oppgåve i BACKLOG.md** som ikkje er blokkert.
   Gjeldande styring frå Iver (2026-07-06): konkrete designprosjekt —
   algoritmisk modellering for 3D-printbare modellar — går føre
   balanseregelen i §4, til ny beskjed.
3. Om backloggen er tom eller alt er blokkert: generer nytt arbeid frå
   iterasjonsmenyen (§4) — vel det som gjev mest verdi for vegkartet no,
   og varier: aldri same menykategori tre gonger på rad.

## 2 · Handoff — gjer arbeidet

Gjer oppgåva heilskapleg. For research: søk, les, destiller til eit datert
notat i `research/` med kjelder. For skriving: fullstendige utkast, ikkje
disposisjonar. For Notion-arbeid: bygg ferdig, ikkje halvvegs.

## 3 · Verification — sjekk med friske auge

Før noko vert markert done, køyr desse portane:

- **Innhaldsport:** Les artefakten på nytt som om du var Iver utan
  øktkontekst. Er det forståeleg, kjeldefest, på nynorsk, kopla til tesen?
- **Traktatport:** Motseier innhaldet traktaten? Om ja: er det flagga som
  medviten spenning i loggen?
- **Teknisk port:** JSON gyldig, lenkjer heile, Notion-sider renderer
  (fetch attende), git-status rein etter commit.
- Om ein port feilar: fiks, eller rull attende og skriv kvifor i
  `LEARNINGS.md`. Ikkje marker done.

## 4 · Iterasjonsmeny (når backloggen treng påfyll)

| Kategori | Døme på arbeid |
|---|---|
| **Research** | Kartlegg éin konkurransearena, éin produsent, éi utlysing; djupdykk i éi teorikjelde frå Biblioteket; finn faktiske fristar/datoar |
| **Skriving** | Før eitt Skriveprosjekt éin fase vidare (idé→utkast→revisjon); utkast til Designopprør-case |
| **Verkstad** | Skriv full designbrief for eitt Verkstad-objekt: aksar, traktat-kopling, printstrategi, testplan |
| **Vegkart** | Rull vegkartet: er fristar realistiske? Nye høve dukka opp? Oppdater «Neste steg»-felt |
| **Synk** | Notion ↔ git-avvik? Spegl endringar begge vegar |
| **Meta** | Forbetre LOOP.md/CLAUDE.md sjølv, basert på LEARNINGS.md |

Balanseregel: over ti iterasjonar skal minst tre vere Research, to
Skriving, to Verkstad, éin Vegkart, éin Synk, maks éin Meta.

## 5 · Persistence — skriv state

1. Oppdater `STATE.md`: iterasjonsnummer +1, kva vart gjort, kva er neste.
2. Oppdater `BACKLOG.md`: kryss av utført, legg til nyoppdaga arbeid.
3. Ved feil/lærdom: éi line i `LEARNINGS.md`.
4. Commit med beskrivande melding; **verifiser at committen faktisk
   inneheld filendringar** (`git show --stat HEAD`) — ein tom commit er
   ein feila persistence-port. Push med `git push -u origin main`
   (Ivers instruks 2026-07-06; retry 2s/4s/8s/16s ved nettfeil).
5. Skriv éi rad i Notion-databasen «Logg · iterasjonar & funn»
   (Type=Agent-loop, dato, samandrag, neste handling).

## 6 · Scheduling — bestem neste vekking

- Køyrer du under `/loop` dynamisk modus: bruk ScheduleWakeup med
  1200–1800 s for vanleg takt; 3600 s om du nettopp har gjort tre
  iterasjonar på rad utan menneskeleg innspel.
- Køyrer du under ein cron-trigger: berre avslutt; triggeren vekkjer deg.
- Elles: avslutt økta reint — neste sesjon plukkar opp frå STATE.md.

## 7 · Stopp- og pausevilkår

**Stopp (avslutt loopen og varsle Iver):**
- Iver ber om stopp, eller stiller spørsmål som krev svar før vidare arbeid.
- Ein irreversibel eller utoverretta handling står i vegen (publisering,
  e-post til eksterne, søknadsinnsending): DET GJER LOOPEN ALDRI SJØLV.
  Legg det klart i backloggen merkt `[TRENG IVER]` og hald fram med anna.
- Tre iterasjonar på rad utan at nokon port i §3 passerer: noko er gale
  med sjølve loopen; skriv diagnose i LEARNINGS.md og stopp.

**Pause (hopp over iterasjon, ikkje stopp):**
- Notion eller GitHub utilgjengeleg → prøv att neste vekking.

## 8 · Kontrakt med mennesket

Loopen produserer; Iver bestemmer. Alt utoverretta (publisering, kontakt,
innsending, pengar) ligg alltid att som `[TRENG IVER]`-oppgåver. Loopen
sin jobb er at når Iver opnar Notion, ligg det alltid ferdig tenkt,
kjeldefest og gjennomarbeidd materiale og ventar — aldri halvtenkt slam.
