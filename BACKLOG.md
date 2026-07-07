# BACKLOG.md, prioritert arbeidskø

Loopen konsumerer ovanfrå. `[TRENG IVER]` = berre mennesket.

**Misjon (Iver, 2026-07-07):** loopen er ein fullstendig iterativ
design-idegenerator og designar, frå idé gjennom parametrisk og
generativ-vekst-modellering heilt fram til produksjonsklare modellar.
Design-pipeline (frø to vekst to prøve to slip to produksjonsmodell) og
metode-meny i `LOOP.md`. Verkstad/design fyrst; programme-sporet
sekundært. Skrivekonvensjonar (CLAUDE.md): ingen tankestrekar, ikon eller
emojiar. Estetisk hovudretning: rotasjonsgrammatikken frå referansebileta
(5 no, tromme-linse lagt til), sjå
`research/2026-07-06-formretning-rotasjonsgrammatikk.md`.

## Kø, Verkstad og meta (prioritert av Iver)

Loop-oppdraget er no ein full design-pipeline (idé → parametrisk/generativ
modell → validering → produksjonsmodell), sjå LOOP.md. Formspråket spenner
over to familiar: rotasjonsgrammatikk (bygd) og glatte minimalflater (ny).

A. [ ] **Nytt objekt (RETNING, glatt familie):** implicit-flate-generator
   for den glatte minimalflate-familien (referanse 06-09: saddel-/dryp-skal,
   to-tona matt/blank). Teknikk: SDF + marching cubes (skimage/trimesh),
   gyroid/TPMS eller metaball-blend. Fyrste objekt: ei skål eller eit fat
   der forma navigerer reelle trykk (volum, stabilitet, veggtjukn,
   printfysikk utan støtte). Vasstett 3MF + validering + render. Legg i
   `verkstad/glattflate/` med namespaced output.
0. [x] **Meta/Synk:** Notion-omstrukturering + konvensjonssveip git (it. 26)
   og Notion-undersidene (it. 34). Attstår (lågt prioritert): select-
   opsjonar med intervall-strek (Horisont H1-H3), radinnhald i
   Bibliotek/Prinsipp.
1. [x] **Verkstad (RETNING):** Generator B bygd i tre komplementære greiner:
   vase (`skavl_vase.py`, ribbe/slisse, opningsgrad 24-31 %, it. 28),
   rotor (`g-rotor`, vertikale finner, it. 29) og lampe (`skavl_b.py`,
   lamell/blend, E27-ring, it. 30). Alle vasstette og printbare. Funn
   (rotor): den flate skåla har vassrette veggar = FDM-overheng, den
   printbare kusinen er ei ståande finne-søyle (ekte flat skål = resin/SLA).
2. [ ] **Verkstad (RETNING):** Lampe-greina v0.2, løys blendaksen (opent
   funn it. 30: radiale finnar stengjer berre 13-16 % av blendbandet).
   Kandidatar: tynn indre diffusor-sylinder i blendbandet, breiare/tettare
   lamellar med projeksjons-overlapp, eller medviten retningslampe. Re-mål
   strålecasting til mål 100 %. Sjå `verkstad/skavl/README.md`.
3. [ ] **Verkstad (RETNING):** Materialeksperiment #1, glasur-analogen i
   print (silk-PETG laglys / to-farge kant-høglys / polert egg mot matt dal),
   testprotokoll for Knagg/Skavl-printane.
4. [x] **Verkstad:** Skavl-lampe-hybrid → it. 30 (`skavl_b.py`, radiale
   lameller, blend-funn 13-16 %) + it. 31 (`skavl_lampe.py`, rib/slisse med
   glare-band lukka, blend=0, termisk klaring 74-79 mm, E27-sokkel, opning
   15 %). To komplementaere geometriske svar paa blendaksen. Attstaar:
   kombiner dei to til 100 % blend + hoegare opning (lagt i Neste handling).
5. [ ] **Design (RETNING):** Ny familie `h-tromme` (v0.5) frå
   referanse-e (`ref-e-tromme-linse.png`): brei tromme/tønne med vertikale
   bølgjande lameller og store linse-/augeforma opningar. Bygg på
   `skavl_vase.py`-kjernen: brei rett profil (h omtrent lik diameter),
   30-36 ribber, twist 0, kraftig drope_styrke for linsene, relieff 6-8 mm.
   Full pipeline til produksjonsmodell (§2 i LOOP.md).
6. [ ] **Design (RETNING):** Kombiner dei to lampe-svara (skavl_b radial +
   skavl_lampe rib/slisse) til 100 % blend + høgare opning; louver/indre
   diffusor. Full validering (blend=0, termikk, print).
7. [ ] **Design (metode):** Prøv ein ny generativ-vekst-metode frå
   metode-menyen (LOOP.md §3) på eit objekt: reaction-diffusion-relieff
   eller Voronoi-skalgitter på ein vase, eller TPMS-infill i knaggen.
8. [ ] **Verkstad:** Reparasjonssett: parametrisk klips-protese-generator
   kopla til brotmodus-taksonomien (`research/2026-07-06-brotmodus-taksonomi.md`),
   PETG, start med modus «snap-fit-hake av».
6. [ ] `[TRENG IVER]` Slice og testprint Skavl-søskena og knaggane
   (`verkstad/skavl/print/*.3mf`, `verkstad/knagg/print/*.3mf`; sjå
   slicing-notat i README-ane). For lampa: mål E27-fatninga og pæra
   fyrst (R_SOKKEL/Z_LED). Timelapse frå fyrste print!

## Kø, elles

1. [ ] `[TRENG IVER]` Vel arbeidsnamn, trengst i Salone-skjemaet.
2. [ ] `[TRENG IVER]` Start Knagg #1-printinga denne veka (kritisk sti).
3. [ ] `[TRENG IVER]` Fotografer eit konkret leskur (med adresse, helst i
   regn/vind), trengst før Case #1 kan publiserast.
4. [ ] `[TRENG IVER]` AHO-kontakt steg 1: meld deg som informant hjå
   Trym Abrahamsen (Applied Formgiving-ph.d.), sjå
   `research/2026-07-06-aho-miljoet.md`.
5. [ ] `[TRENG IVER]` Stadfest formreferansen: er bileta Steven Edwards?
   (attribusjon truleg, ikkje verifisert), trengst før ekstern bruk.
6. [ ] `[TRENG IVER]` Utvekslingsavgjerd før 15. sep 2026 (intern frist
   vårutveksling 2027 = same dag som Greenhouse): vår 2027 kolliderer med
   Salone; haust 2027 er tryggare, sjå «Studieløpet som ramme» i 05-sida.
7. [ ] `[TRENG IVER]` Foto 16:9 av prototypane innan ~20. aug.
8. [ ] `[TRENG IVER]` Send Salone-skjema innan 30. aug; Greenhouse innan 15. sep.
9. [ ] `[TRENG IVER]` Foto: benk med midtarmlene + lenebenk
   (Bjørvika/Oslo S), til Case #2, sjå
   `writing/case-ideliste-designopproret.md`.
10. [ ] **Synk:** Spegl eventuelle Notion-endringar → git (løpande).
11. [ ] **Research:** Produsentkartlegging #4: Fjordfiesta (Molde,
    Scandia-arven), samanlikn med Eikund; deretter destiller
    produsent-landskapskartet inn i `strategy/04-posisjonering.md`.
12. [ ] **Research:** Finn neste utlysing/frist for Northern Lighting
    Student Design Award (årleg, est. 2013; stadfest at prisen framleis finst),
    kandidat-arena for Skavl-lampa etter Salone/Greenhouse.
13. [ ] **Research:** Verifiser attståande kjeldespor i idélista:
    K7 (søppelkasse, fann ikkje kjelde i it. 23), K11 (rekkverk),
    K12/K13/K15/K16, K4/K5/K14 er ankra.
14. [ ] **Research:** Steven Edwards / rotasjons-keramikk djupare: metode
    (repetition, compression, cut), utstillingar, kva print-grammatikken
    kan lære; inn i Biblioteket og evt. keramikk-spor H1.
15. [ ] **Vegkart:** Overvak Vestre/DOGA for opne designkonkurransar
    (Munch-modellen), sjekk kvartalsvis.

## Gjort

- [x] It. 0: Grunnlegging (2026-07-06)
- [x] It. 1: Konkurransefristar → `research/2026-07-06-konkurransefristar.md`
- [x] It. 2: Brief Knagg #1 → `briefs/knagg-01.md`
- [x] It. 3: Brief Skavl-lampe → `briefs/skavl-lampe.md`
- [x] It. 4: Brief Reparasjonssett → `briefs/reparasjonssett.md`
- [x] It. 5: Norway Says → `research/2026-07-06-norway-says.md`
- [x] It. 6: Søknadspakke → `briefs/soknadspakke-2026.md` + Notion-side
- [x] It. 7: Manifest v1.0 Revisjon→Klar (i Notion; git-committen vart tom)
- [x] It. 8: Synk/Meta, drift retta, branch-referansar oppdaterte etter PR #1
- [x] It. 9: Case #1 «Leskuret som ikkje gjev le» → `writing/case-01-leskuret.md` + Notion (Fase: Utkast)
- [x] It. 10: AHO-miljøet → `research/2026-07-06-aho-miljoet.md`
- [x] It. 11: Skavl-algoritme v0.1 → `briefs/skavl-algoritme.md` + Verkstad-sida
- [x] It. 12: Studieløpet inn i vegkartet → `strategy/05-vegkart.md` + 05-sida i Notion
- [x] It. 13: Brotmodus-taksonomi v0.1 → `research/2026-07-06-brotmodus-taksonomi.md` + Verkstad-sida
- [x] It. 14: Produsent #1 Vestre → `research/2026-07-06-produsent-vestre.md`
- [x] It. 15: Case-idébank → `writing/case-idebank.md`
- [x] It. 16: Case-idéliste Designopprøret → `writing/case-ideliste-designopproret.md` + Skriveprosjekt-rad (Idé)
- [x] It. 17: Konsolidering idébank+idéliste → v0.2 kanonisk (`writing/case-ideliste-designopproret.md`)
- [x] It. 18: Produsent #2 Eikund → `research/2026-07-06-produsent-eikund.md`
- [x] It. 19: Case #2 «Benken» fullt utkast → `writing/case-02-benken.md` + Skriveprosjekt-rad (Utkast)
- [x] It. 20: Briefane rulla til v1.1 mot brotmodus-taksonomien → `briefs/*.md` + Verkstad-sidene
- [x] It. 21: Produsent #3 Northern → `research/2026-07-06-produsent-northern.md`
- [x] It. 22: Produsentlandskapet inn i vegkartet → `strategy/05-vegkart.md` + 05-sida
- [x] It. 23: Skavl v0.2 implementert og validert → `verkstad/skavl/` (3 x 3MF + rapport + silhuett)
- [x] It. 24: Kjeldesveip idélista (K4/K5/K14 ankra) + Northern-pris-retting (parallelløkt, committa som «it. 23»)
- [x] It. 25: Knagg #1 v0.1, tre hypotesar som printbare solidar → `verkstad/knagg/`
- [x] It. 26: Notion-omstrukturering + konvensjonssveip git → dashbord, Oppgåver-database, `notion/STRUKTUR.md`
- [x] It. 27: Retningsendring, rotasjonsgrammatikken → `research/2026-07-06-formretning-rotasjonsgrammatikk.md` + lamell-modus i `briefs/skavl-algoritme.md` + referansebilete + Edwards i Bibliotek
- [x] It. 28: Skavl v0.3 vase-greina (generator B, ribbe/slisse) → `verkstad/skavl/skavl_vase.py` + 3 vasstette 3MF + render + validering + ref/README
- [x] It. 29: Skavl `g-rotor` fjerde søsken + flat-rotor printbarheit-funn → `verkstad/skavl/` (4 vasstette 3MF)
- [x] It. 30: Generator B lampe-greina (lamell/blend) → `verkstad/skavl/skavl_b.py` (3 vasstette 3MF, 115-120 g, blend-funn 13-16 %) + README + requirements.txt
- [x] It. 31: Skavl v0.4 lampe-hybrid (rib/slisse, glare-band lukka, blend=0) → `verkstad/skavl/skavl_lampe.py` + 2 vasstette lampe-3MF + render
- [x] It. 34: Konvensjonssveip Notion (hovudside, 01-05, Søknadspakke, 06, Verkstad-sidene)
