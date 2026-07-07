# LOOP.md — den autonome design- og arbeidssyklusen

> Loop engineering-prinsippet: ikkje prompt agenten tur for tur — design
> loopen som promptar agenten. Kvar iterasjon: **discovery → handoff →
> verification → persistence → scheduling.**
>
> **Kjernen i denne loopen er ein generativ designmotor.** Målet er ikkje
> berre strategi og dokument, men *faktiske former* — frå idé gjennom
> parametrisk/generativ vekst til produksjonsklare modellar (STL/OBJ).
> Dokumentarbeidet (strategi, kritikk, research) tener designen.

Denne fila ER loop-prompten. Ein agent som får «køyr loopen» følgjer
protokollen under til eit stoppvilkår er nådd.

## 0 · Invariantar

- Følg alle reglar i `CLAUDE.md` (nynorsk, branch, aldri slett, kjeldefest).
- Éin iterasjon = **éi avslutta arbeidseining** som endar i varige
  artefaktar: commit i git + rad i Notion-loggen. Arbeid som ikkje er
  persistert, har ikkje skjedd.
- **Kvar generativ iterasjon skal produsere geometri du kan sjå og printe**
  — ikkje berre snakk om form.

## 1 · Den generative pipelinen (motoren)

`generator/grow.py` er v1 av motoren. Pipeline:

1. **Idé/seed** — vel eit formmål (vase, skjerm, krukke, objekt) og kva
   referanse i `assets/formsprak/` det siktar mot.
2. **Genom** — set seleksjonstrykk-vektene (symmetri, vertikal/radial bias,
   knopp-tal, falloff, blend). Genomet ER posisjonen i formrommet (1.3).
   Kvar parameter er eit seleksjonstrykk (2.1).
3. **Vekst** — sfære-aggregasjon under trykka → signert distansefelt
   (smooth-union / metaball) → marching cubes → mesh. Forma fell ut av
   navigasjonen (5.13).
4. **Iterasjon/seleksjon** — generer ein **sverm av søsken** (3.3), vurder
   dei mot formgrammatikken (07 · Formspråk) og mot traktat-aksane:
   materialminimum, printbarheit, «ser det grodd ut?».
5. **Produksjonsmodell** — eksporter vasstett STL/OBJ; rapporter volum,
   mål, vasstett-status i `genomes.json`. Dette er den printbare/støypbare
   modellen.

Køyr motoren:
```
python3 generator/grow.py --n 6 --seed <N> --out generator/out
```

**Å forbetre motoren er sjølv ei gyldig iterasjon.** Døme på utvidingar
(legg i BACKLOG): ribbe/differential-growth-modus (kråkebolle/lamell,
ikkje berre bulbøs); radial hòl (vase/skjerm-topologi); veggtjukn-offset
for keramikk-print; overheng-/krymp-sjekk mot wet-clay-budsjettet
(sjå `briefs/krakebolle-skjerm.md`); glasur-dal-analyse; automatisk
utval av «beste» søsken mot ein omhugs-score.

## 2 · Discovery — finn neste arbeid

1. Les `STATE.md`, `BACKLOG.md`, `LEARNINGS.md`, `git log --oneline -10`.
2. Vel øvste ublokkerte oppgåve i `BACKLOG.md` (hopp over `[TRENG IVER]`).
3. Tom backlog → generer arbeid frå menyen (§4); prioriter **generativt**
   arbeid; varier (ikkje same menykategori tre gonger på rad).

## 3 · Handoff — gjer arbeidet

Fullfør heilskapleg. Generativt: køyr motoren, sjå på kontaktarket,
vel/iterer, eksporter. Research/skriving: fullstendige, kjeldefeste
leveransar. Aldri halvvegs.

## 4 · Verification — sjekk med friske auge

- **Design-port (generativt):** er søskena vasstette (`is_watertight`)?
  Ser dei ut som formspråket (grodd, ikkje komponert)? Er dei printbare
  i storleik/overheng? Legg kontaktark + STL i `generator/out/…`.
- **Innhaldsport:** forståeleg for Iver utan øktkontekst, nynorsk, kjeldefest.
- **Traktatport:** motseier det traktaten? Flagg i loggen om ja.
- **Teknisk port:** JSON gyldig, lenkjer heile, Notion renderer, git rein.

## 5 · Iterasjonsmeny

| Kategori | Arbeid |
|---|---|
| **Generativt (kjerne)** | Køyr/forbetre `grow.py`; ny formfamilie; ny vekstmodus; produksjonseksport; utval av beste søsken |
| **Verkstad** | Kople eit generert objekt til ein designbrief (aksar, print, test) |
| **Research** | Teknikk (keramikk-print, celadon, algoritmar); arenaer/fristar; teori |
| **Skriving** | Essay/kritikk/case eitt steg vidare |
| **Strategi/Vegkart** | Rull vegkartet; nye høve; oppdater «neste steg» |
| **Synk** | Notion ↔ git-avvik begge vegar |
| **Meta** | Forbetre LOOP.md/CLAUDE.md frå LEARNINGS.md |

Balanse over ti iterasjonar: minst **fire generative**, to research, to
skriving/verkstad, éin vegkart, éin synk, maks éin meta.

## 6 · Persistence

1. Oppdater `STATE.md` (iterasjon +1, gjort, neste) og `BACKLOG.md`.
2. Nye artefaktar (STL, kontaktark, genomes.json, kode) committast.
3. Feil/lærdom → éi line i `LEARNINGS.md`.
4. Commit + `git push -u origin claude/norsk-design-strategy-plan-zgwmkm`
   (retry 2s/4s/8s/16s ved nettfeil).
5. Éi rad i Notion-loggen «Logg · iterasjonar & funn» (Type=Agent-loop);
   for generative iterasjonar: last opp/omtal kontaktarket og ev. legg
   objektet i Verkstad-databasen.

## 7 · Scheduling

- `/loop` dynamisk: ScheduleWakeup 1200–1800 s (3600 s etter fleire
  iterasjonar utan menneske).
- Cron/Routine-firing: berre avslutt; triggeren vekkjer deg.
- Elles: avslutt reint — neste økt les `STATE.md`.

## 8 · Stopp / pause / menneskekontrakt

**Stopp og varsle Iver** når: Iver ber om det; ei utoverretta handling
står i vegen (sjå under); tre iterasjonar på rad utan at nokon port i §4
passerer.

**Loopen gjer ALDRI sjølv:** publisering, e-post, søknadsinnsending,
bestilling av print/keramikk hjå tredjepart, pengebruk. Slikt vert
liggjande som `[TRENG IVER]` i backloggen.

**Pause (hopp over, ikkje stopp):** Notion/GitHub nede → prøv att neste firing.

Loopen produserer former og materiale; Iver vel, brenner og publiserer.
Når Iver opnar repoet/Notion skal det alltid liggje ferdige, vasstette
modellar og gjennomarbeidd materiale og vente — aldri halvtenkt slam.
