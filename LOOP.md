# LOOP.md, den autonome arbeidssyklusen

> Loop engineering-prinsippet: ikkje prompt agenten tur for tur, design
> loopen som promptar agenten. Kvar iterasjon har fem trekk:
> **discovery → handoff → verification → persistence → scheduling.**

Denne fila ER loop-prompten. Ein agent som får beskjeden «køyr loopen»
(via `/loop`, ein trigger, eller manuelt) skal følgje protokollen under,
utan å spørje om lov undervegs, til ein stoppvilkår er nådd.

## Oppdraget til loopen (Ivers instruks 2026-07-06)

Loopen er ein **fullt iterativ design-generator og designar: frå idé, via
parametrisk/generativ modellering (vekst, rotasjonsgrammatikk, kraftlinjer),
heilt fram til produksjonsklare modellar Iver kan 3D-printe.** Dette er
hovudarbeidet. Kvar iterasjon skal flytte minst eitt fysisk objekt eitt
konkret steg vidare i pipelinen under. Strategi, research og skriving er
støttespor som tener objekta (dei gjev aksar, kjelder, produsentar,
forteljing), ikkje omvendt.

Traktaten er motoren: **form følgjer fitness.** Ein generator navigerer
eit felt av samtidige seleksjonstrykk (aksane), og forma fell ut av
navigasjonen. Kvar generativ eining må svare på minst eitt *målbart*
trykk (blending, termikk, styrke, materialminimum, grip), aldri rein
dekorasjon (jf. `research/2026-07-06-formretning-rotasjonsgrammatikk.md`).

**Formspråket (Ivers referansar, `reference/formretning-2026-07/`)** spenner
over to familiar, begge fair game for generatorane:
1. **Rotasjonsgrammatikken:** ribber/lameller/finnar i rotasjonsarray,
   vridne (twist), stabla mellom ringar, med linse-/auge-opningar og
   dropeføter (bilete 01-05). Alt bygd i `verkstad/skavl/`.
2. **Glatte minimalflater:** kontinuerlege saddel-/dryp-skal, mjuke blend,
   implicitte flater (SDF/marching cubes, gyroid/TPMS, metaballs),
   to-tona matt/blank (bilete 06-09). Ny familie, endå ikkje bygd, høg
   prioritet for eit nytt objekt.
Begge er «éin profil/felt navigert av trykk»; skilnaden er berre om
grammatikken er diskret (finnar) eller kontinuerleg (flate).

## Design-pipelinen (dei seks stega eit objekt går gjennom)

Kvart Verkstad-objekt lever på ein av desse stega. Éin iterasjon = flytt
eitt objekt eitt steg, eller forbetre det innan same steg (v0.1 → v0.2).

| Steg | Kva | Artefakt |
|---|---|---|
| **1 · Idé/seed** | Nytt objekt eller ny grein: definer seleksjonstrykka (aksane) med tal, og traktat-koplinga. | Rad i Verkstad + kort brief i `briefs/` |
| **2 · Generator** | Skriv/utvid ein parametrisk, generativ modell i `verkstad/<objekt>/` (Python + trimesh/numpy; vekst, rotasjonsarray, kraftliner). Deterministisk per frø. | `<objekt>.py`, familie av søsken |
| **3 · Validering** | Køyr dei harde portane som MÅLT kode, ikkje påstand: vasstett solid, masse, overheng (< budsjett), funksjonsspesifikke gate (blend, termikk, styrke). | `validering-*.md` generert av scriptet |
| **4 · Forbetring** | Lukk øvste opne funn frå valideringsrapporten (t.d. «radiale finnar stengjer berre 13-16 % av blendbandet»). Éin forbetring per pass. | Ny versjon + oppdatert rapport |
| **5 · Produksjonsmodell** | Når alle portar passerer: eksporter vasstett 3MF, skriv slicing-kort (materiale, perimeter, lag, støtte, orientering), render/silhuett. | `print/*.3mf` + slicing-notat |
| **6 · Familie/sverm** | Tre+ søsken, éin grammatikk (traktat 5.31): same generator, ulik trykkvekting. Vis at stilarten er ein sverm, ikkje ein påstand. | Søskensett + samanstilt render |

**Definisjon av «produksjonsklar»:** vasstett; alle harde portar grøne i
den genererte rapporten; 3MF ligg i `print/`; slicing-kortet fortel korleis
det skal printast; opne funn er anten lukka eller eksplisitt flagga i
rapporten som medviten avgrensing. Fysisk print er alltid `[TRENG IVER]`.

## 0 · Invariantar (les før kvar iterasjon)

- Følg alle reglar i `CLAUDE.md` (nynorsk, main-branch, aldri slett,
  kjeldefest, ingen tankestrekar/emoji).
- Éin iterasjon = **éi avslutta arbeidseining** som flyttar eitt objekt
  eitt pipeline-steg, ikkje «litt av alt».
- Alt arbeid skal ende i varige artefaktar: commit i git + rad i
  Notion-loggen. Arbeid som ikkje er persistert, har ikkje skjedd.
- Kode skal *køyre*: ein generator som ikkje produserer ein vasstett solid
  er ikkje ferdig. Køyr han, les rapporten, handter det han faktisk seier.

## 1 · Discovery, finn neste arbeid

1. Les `STATE.md`, `BACKLOG.md`, `LEARNINGS.md`, `git log --oneline -10`.
   **Fleire økter køyrer parallelt og racer på iterasjonsnummer:**
   `git fetch origin main` fyrst, les nye committar, sjekk for
   duplikatarbeid FØR du vel oppgåve.
2. Vel det som gjev mest framdrift i pipelinen: **øvste ublokkerte
   Verkstad-oppgåve i BACKLOG.md**, eller det objektet/steget med størst
   uforløyst verdi (eit opent valideringsfunn som ventar på steg 4, eit
   objekt klart for steg 5, ein grammatikk som manglar søsken).
3. Hopp over alt merkt `[TRENG IVER]`.
4. Om Verkstad-køen er tom: generer nytt arbeid frå menyen (§4), primært
   nye objekt eller nye greiner i pipelinen; sekundært eit støttespor.

## 2 · Handoff, gjer arbeidet

Gjer oppgåva heilskapleg og køyrande.

- **Generator (steg 2-4):** skriv/utvid koden, *køyr han*, les
  valideringsrapporten, iterer til portane passerer eller til du har eit
  ærleg dokumentert funn. Namespace alle output-filer så dei ikkje klabbar
  andre økter sine (jf. LEARNINGS: `skavl-lamell-*` vs `vase-*`).
- **Produksjonsmodell (steg 5):** eksporter 3MF, skriv slicing-kort,
  render silhuett/3D. Send gjerne rendering til Iver med SendUserFile.
- **Støttespor (research/skriving):** datert notat i `research/` med
  kjelder, eller fullstendige utkast, aldri disposisjonar. Desse skal
  peike tilbake på eit objekt (kva akse/produsent/forteljing dei tener).

## 3 · Verification, sjekk med friske auge

Før noko vert markert done, køyr desse portane:

- **Køyreport (Verkstad):** køyrde generatoren? Er solidane vasstette?
  Passerer dei harde gate i den *genererte* rapporten (ikkje di eiga
  påstand)? Eit falskt «pass» er verre enn eit ærleg funn.
- **Traktatport:** svarar kvar generativ eining på eit målbart trykk?
  Motseier forma traktaten? Om ja: flagga som medviten spenning i loggen?
- **Innhaldsport:** kan Iver lese artefakten utan øktkontekst? Nynorsk,
  kjeldefest, kopla til tesen?
- **Teknisk port:** JSON gyldig, lenkjer heile, `git show --stat HEAD`
  viser faktiske filendringar, git-status rein, Notion-sider renderer.
- Om ein port feilar: fiks, eller rull attende og skriv kvifor i
  `LEARNINGS.md`. Ikkje marker done.

## 4 · Iterasjonsmeny (når køen treng påfyll)

**Primær (design-pipeline, mesteparten av iterasjonane):**

| Kategori | Døme på arbeid |
|---|---|
| **Nytt objekt** | Definer eit nytt Verkstad-objekt: aksar kvantifiserte, traktat-kopling, fyrste generator-skisse (steg 1-2) |
| **Ny grein** | Ny generativ variant av eit objekt (t.d. lamell vs. ribbe vs. rotor for skavl), same familie |
| **Forbetring** | Lukk øvste opne valideringsfunn på eit eksisterande objekt (steg 4) |
| **Produksjon** | Før eit objekt som passerer portane til produksjonsmodell: 3MF + slicing-kort + render (steg 5) |
| **Familie** | Legg til / balanser søsken so grammatikken syner seg som sverm (steg 6) |
| **Metode** | Ny generativ teknikk inn i verktøykassa, demonstrert på eit objekt: differential growth, reaction-diffusion, kraftliner, L-system, og for den glatte familien implicitte flater (SDF + marching cubes, gyroid/TPMS, metaballs) |

**Sekundær (støttespor, tener objekta):**

| Kategori | Døme på arbeid |
|---|---|
| **Research** | Ein produsent/arena/utlysing; ei teorikjelde; brotmodus-/materialdata som matar ein generator |
| **Skriving** | Før eitt Skriveprosjekt éin fase vidare; Designopprør-case |
| **Vegkart/Synk/Meta** | Rull vegkartet; spegl Notion ↔ git; forbetre LOOP/CLAUDE frå LEARNINGS |

Balanseregel: over ti iterasjonar skal minst **seks** vere primær
(design-pipeline), resten støttespor, maks éin Meta. Aldri same underkategori
tre gonger på rad, så porteføljen ikkje let eitt trykk dominere (4.5).

## 5 · Persistence, skriv state

1. Oppdater `STATE.md`: iterasjonsnummer (max(remote)+1 ved race), kva vart
   gjort, kva pipeline-steg objektet står på no, kva er neste opne funn.
2. Oppdater `BACKLOG.md`: kryss av utført, legg til nyoppdaga arbeid
   (særleg opne valideringsfunn som eigne forbetrings-oppgåver).
3. Ved feil/lærdom: éi line i `LEARNINGS.md`.
4. Commit med beskrivande melding; **verifiser at committen faktisk
   inneheld filendringar** (`git show --stat HEAD`), ein tom commit er
   ein feila persistence-port. `git fetch origin main`, renummerer ved
   race, push med `git push -u origin main` (retry 2s/4s/8s/16s ved nettfeil).
5. Skriv éi rad i Notion-databasen «Logg · iterasjonar & funn»
   (Type=Agent-loop, dato, samandrag, neste handling). Spegl større
   objekt-framsteg til Verkstad-sida.

## 6 · Scheduling, bestem neste vekking

- Køyrer du under `/loop` dynamisk modus: bruk ScheduleWakeup med
  1200-1800 s for vanleg takt; 3600 s om du nettopp har gjort tre
  iterasjonar på rad utan menneskeleg innspel.
- Køyrer du under ein cron-trigger: berre avslutt; triggeren vekkjer deg
  att (kadens: kvar 4,5 time, sjå STATE.md).
- Elles: avslutt økta reint, neste sesjon plukkar opp frå STATE.md.

## 7 · Stopp- og pausevilkår

**Stopp (avslutt loopen og varsle Iver):**
- Iver ber om stopp, eller stiller spørsmål som krev svar før vidare arbeid.
- Ein irreversibel eller utoverretta handling står i vegen (publisering,
  e-post til eksterne, søknadsinnsending, bestilling): DET GJER LOOPEN
  ALDRI SJØLV. Legg det i backloggen merkt `[TRENG IVER]` og hald fram.
- Tre iterasjonar på rad utan at nokon port i §3 passerer: noko er gale
  med sjølve loopen; skriv diagnose i LEARNINGS.md og stopp.

**Pause (hopp over iterasjon, ikkje stopp):**
- Notion eller GitHub utilgjengeleg → prøv att neste vekking.

## 8 · Kontrakt med mennesket

Loopen produserer; Iver bestemmer. Alt utoverretta (publisering, kontakt,
innsending, pengar, fysisk print) ligg alltid att som `[TRENG IVER]`.
Loopen sin jobb er at når Iver opnar repoet, ligg det alltid eitt steg meir
ferdig design: ein generator som køyrer, ein rapport som er ærleg, ein 3MF
som er klar til skrivaren, aldri halvtenkt slam.
