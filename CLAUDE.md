# CLAUDE.md, harness for FORMLÆRE-programmet

Du arbeider i eit langsiktig strategiprosjekt for Iver Raknes Finne
(industridesignstudent, AHO): å gjere for norsk industridesign det Snøhetta
gjorde for norsk arkitektur. Prosjektet lever i to system som skal haldast
i synk:

1. **Notion**, menneskegrensesnittet. Sider, databasar, kanban. ID-ar i
   `notion/manifest.json`.
2. **Dette repoet**, agentgrensesnittet. State, backlog, speglar, logg.

**Misjon for loopen (Ivers styring 2026-07-07):** repoet skal drive ein
fullstendig iterativ design-idegenerator og designar, frå idé gjennom
parametrisk og generativ-vekst-modellering heilt fram til
produksjonsklare modellar. Design-pipelinen og metode-menyen ligg i
`LOOP.md` (frø to vekst to prøve to slip to produksjonsmodell). Verkstad/
design går føre programme-sporet (strategi/research/skriving) til ny
beskjed.

## Faste reglar

- **Språk:** nynorsk i alt innhald (Ivers eigen målform). Kode/filnamn på engelsk er ok.
- **Skrivekonvensjonar (Ivers instruks 2026-07-06):** ingen tankestrekar
  (em-dash/en-dash), ingen ikon og ingen emojiar, korkje i git, Notion,
  commit-meldingar eller genererte rapportar. Bruk komma, kolon, punktum
  eller vanleg bindestrek i staden. Talområde med bindestrek (60-80 mm).
  Notion-sider skal ikkje ha emoji-ikon.
- **Branch:** all utvikling direkte på `main` (Ivers instruks 2026-07-06:
  «push main direkte no og framover»). Ingen feature-branchar/PR-ar utan
  at Iver ber om det.
- **Aldri slett** innhald i Notion; arkiver/flytt heller. Ved tvil: legg til, ikkje erstatt.
- **Kvalitet over volum:** eitt grundig research-notat slår ti tynne. Alt du skriv skal kunne lesast av Iver utan kontekst frå økta.
- **Kjeldefest alt:** research-notat skal ha URL-ar; strategipåstandar skal peike på traktaten (proposisjonsnummer) eller ei ekstern kjelde.
- **Traktaten er grunnlova.** Ved konflikt mellom ein idé og traktatens rammeverk: flagg konflikten i loggen i staden for å jamne han ut. Falsifiseringsvilkåra (traktaten, notata) er ein feature, bruk dei.
- **Omhug i praksis:** kvar produktidé i Verkstad skal ha felta «Seleksjonstrykk (aksane)» og «Traktat-kopling» utfylte før fasen kan passere Skisse.

## Oppstart av ei økt (fyrste kontekstvindauge)

1. Les `STATE.md` → kvar stoppa siste iterasjon?
2. Les `BACKLOG.md` → kva er øvste prioriterte oppgåve?
3. Les `LEARNINGS.md` → kva reglar er lærte?
4. Køyr `git log --oneline -10` → kva skjedde nyleg?
5. Følg deretter `LOOP.md`.

## Synk-kontrakt (Notion ↔ git)

- Strategisider: `strategy/*.md` speglar Notion-sidene 00-05. Endrar du
  éin stad, oppdater den andre i same iterasjon.
- Databasar: git speglar ikkje radene (Notion er master for databasar);
  men større funn frå databasane kan destillerast inn i `strategy/` og
  `research/`.
- Loggen: kvar loop-iterasjon skriv (a) éi rad i Notion-databasen
  «Logg · iterasjonar & funn» med Type=Agent-loop, og (b) oppdaterer
  `STATE.md` + committar. Git-commit-meldinga og Notion-loggraden skal
  fortelje same historie.
- Galleri: kvart render/kvar generert form skal òg inn i Notion-databasen
  «Galleri, render og iterasjonar» som eit bilete (sjå LOOP.md §5.6 og
  `verkstad/tools/png_to_notion_svg.py`). Alle framtidige render hamnar
  der, som eit levande galleri av heile iterasjonshistoria.

## Verifikasjon før commit/push

- Nye Notion-sider: hent sida att (fetch) og sjå at ho renderer utan feil.
- Markdown: ingen brotne interne lenkjer; manifest.json er gyldig JSON.
- Aldri rapporter noko som gjort utan at det faktisk er gjort.
