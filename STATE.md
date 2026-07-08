# STATE.md, loop-state

**Iterasjon:** 34
**Sist oppdatert:** 2026-07-07
**Status:** Aktiv loop-køyring, fleire økter parallelt («køyr til tokena
er tomme», Ivers instruks 2026-07-06). All utvikling går direkte til
`main`. Loop-triggerar aktive kvar 4,5 time (Ivers instruks: «every 4 1/2
hours»). Sidan 4,5 t ikkje deler 24 t jamt, er kadensen sett med TO
komplementære triggerar som vekslar: «FORMLÆRE loop 4,5t (A)»
(trig_01DqhXRKkJof8qzmz8oHozmh, `7 1,10,19 * * *`) og «(B)»
(trig_016uSTYMzU7uty5h1LDs8o1v, `37 5,14,23 * * *`). Samla fyring UTC:
01:07, 05:37, 10:07, 14:37, 19:07, 23:37 (4,5 t mellom alle unnateke
natt-wrappen 23:37→01:07 = 1,5 t). Begge: ferskt miljø per køyring,
push-varsel.

**Gjeldande styring frå Iver:**
1. **Misjon (2026-07-07):** loopen er ein fullstendig iterativ design-
   idegenerator og designar, frå idé gjennom parametrisk og generativ-
   vekst-modellering heilt fram til produksjonsklare modellar. Ny
   design-pipeline (frø to vekst to prøve to slip to produksjonsmodell)
   og metode-meny i `LOOP.md`. «A fully iterative design idea generator
   and designer, all the way to production models.»
2. Konkrete designprosjekt fyrst: algoritmisk modellering for fysiske
   modellar Iver kan 3D-printe (Verkstad-tungt til ny beskjed).
3. Skrivekonvensjonar: ingen tankestrekar, ikon eller emojiar (CLAUDE.md).
4. Formretning: rotasjonsgrammatikken frå referansebileta er den
   estetiske hovudretninga (5 referansar no, tromme-linse lagt til
   2026-07-07: `verkstad/skavl/ref/ref-e-tromme-linse.png`).
5. Notion: hovudside som dashbord, kanban, kalender, tydelege databasar.

## Iterasjonshistorikk (denne økta)

| # | Kategori | Kva |
|---|---|---|
| 0 | Grunnlegging | Notion-prosjekt + repo + loop-protokoll |
| 1 | Research | Konkurransefristar: Salone 30/8, Greenhouse 15/9 → H0 komprimert |
| 2 | Verkstad | Designbrief Knagg #1 (aksar kvantifisert, testplan, EN-skildring) |
| 3 | Verkstad | Designbrief Skavl-lampe (generativ form, tre søsken) |
| 4 | Verkstad | Designbrief Reparasjonssett (kintsugi for plast) + trio-grunngjeving |
| 5 | Research | Norway Says → grammatikken er limet; exit-plan frå dag éin |
| 6 | Skriving | Søknadspakke Salone+Greenhouse: sjekklister, EN-presentasjon, standkonsept «Le-sida» |
| 7 | Skriving | Manifest v1.0 → Klar i Notion (git-committen vart tom; retta i it. 8) |
| 8 | Synk/Meta | Drift retta: STATE/BACKLOG à jour med it. 7; branch-referansar oppdaterte etter merge av PR #1 |
| 9 | Skriving | Case #1 «Leskuret som ikkje gjev le», fullt utkast, 9 kjelder, trykktabell, karusell-skisse; Fase Idé→Utkast |
| 10 | Research | AHO-miljøet kartlagt: Bjørnstad (formgjeving, fyrsteval), Abrahamsen (ph.d.), Killi (AM/instituttleiar), Nordby; kontaktrekkjefølgje inn i H0/H1 |
| 11 | Verkstad | Skavl-algoritme v0.1: kurve-stabel-arkitektur, pseudokode, 17 parametrar, metode-referansar; spegla på Verkstad-sida |
| 12 | Vegkart | Studieløpet inn i H0/H1: 4. år = einaste utvekslingsår; frist vårutveksling = 15. sep (= Greenhouse!); spenning Salone×utveksling flagga |
| 13 | Research | Brotmodus-taksonomi v0.1: 10 modusar frå ORA-data + snap-fit-litteratur; klips-protese opp som eiga delfamilie; PETG-tilråding |
| 14 | Research | Produsent #1 Vestre: motmodellen til Case #1 (varigheit i staden for reklame); Munch-serien kom frå open konkurranse; Snøhetta-kopling |
| 15 | Skriving | Case-idébank: 9 kandidatar + månadsplan sep-des (benk m/midtarmlene → Helsenorge → motcase); prinsipp for banken (parallelløkt) |
| 16 | Skriving | Case-idéliste Designopprøret: 10 kandidatar skåra mot 5 kriterium; tilrådd #2 = benken med midtarmlene (fiendtleg design), #3 = panteautomaten (motmodell); ny rad i Skriveprosjekt (Idé). NB: parallell med it. 15, same konklusjon om benken |
| 17 | Synk | Konsolidering: idébank (it. 15) + idéliste (it. 16) → éi kanonisk liste v0.2 (16 kandidatar, månadsplan sep-des, prinsipp); idebank-fila er peikar; Notion-rada oppdatert; motcase flytt til desember (flagga) |
| 18 | Research | Produsent #2 Eikund: arven som forretningsmodell; gullalder-diagnosen stadfesta empirisk; flagga spenning «grammatikk eller museum»; inngang = «det manglande møbelet»; Northern/Fjordfiesta står att |
| 19 | Skriving | Case #2 «Benken du ikkje kan liggje på», fullt utkast: 4 nivå, trykktabell, Bjørvika-empiri (namngjevne kritikarar + Lynnebakken-avvisinga), Camden/Savić, 9 kjelder, karusell-skisse; Skriveprosjekt-rad (Utkast, frist 1. okt) |
| 20 | Verkstad | Alle tre briefane rulla til v1.1 mot brotmodus-taksonomien: knagg (test per lastretning, krypmåling, PETG/designa svak sone), lampe (termikk-modus, PETG-vurdering, snap-rot), repsett (fem delfamiliar, hylse i to variantar, 50 N per modus); spegla til Verkstad-sidene |
| 21 | Research | Produsent #3 Northern: forlaget utan fabrikk; Northern Lighting Student Design Award (årleg, studentar!) = døra inn for Skavl-lampa; Morten & Jonas som referansebane; flagga spenning utflagga produksjon vs. materialnærleik |
| 22 | Vegkart | Produsentlandskapet inn i 05 (git + Notion): tre arketypar (Superfabrikken/Arven/Forlaget) med kvar si dør; månadsrytmen kopla til case-planen sep-des |
| 23 | Verkstad | Skavl v0.2: pseudokoden implementert (`verkstad/skavl/skavl.py`), tre vasstette 3MF-søsken (107-120 g, overheng maks 45 grader, bru 7,9 mm, blendfri ved konstruksjon), valideringsrapport + silhuett-SVG. Funn: bru-budsjettet avgrensar porøsitet til 6-8 prosent (mål 30) og v0.3 = avlange slissar |
| 24 | Research | Kjeldesveip (parallelløkt, committa som «it. 23»): K4 (handlevogn), K5 (sparkesykkel, no 13/15) og K14 (LED, no 14/15, delt topp) ankra; K7 fann ikkje kjelde. RETTING: Northern-prisen heiter Northern Lighting Student Design Award (årleg, est. 2013); britiske «Northern Design Awards» er urelatert |
| 25 | Verkstad | Knagg #1 v0.1: tre hypotesar som printbar kode (`verkstad/knagg/knagg.py`): kraftlinje (moment-følgjande gods, PETG, 28 g, SF 9,0), kanalisert (kontroll, 27 g, SF 5,9), medvite-svak (designa brotsone, PLA, 26 g, predikert brotlast 10 kg). Vasstette 3MF liggjande på sida, validering + profil-SVG. Nye skrivekonvensjonar frå Iver inn i CLAUDE.md |
| 26 | Meta/Synk | Notion-omstrukturering (Ivers instruks): ny Oppgåver-database (17 rader, status/prioritet/frist/eigar) med kanban-, kalender- og Treng Iver-views; hovudsida bygd om til dashbord (No-seksjon øvst, Oppgåver inline, systemtabell nedst, alt gamalt bevart); konvensjonssveip i git (30 md-filer, tankestrekar og emojiar ute, kodeblokker urørte); manifest.json + notion/STRUKTUR.md |
| 27 | Retningsendring | Ivers fire referansebilete (truleg Steven Edwards-porselen) analyserte til rotasjonsgrammatikken: éin profil × rotasjonsarray × stabling, glasuren som trykk-kart. Skavl får lamell-modus (generator B) som løyser blendingsaksen geometrisk; glasur-analog som materialeksperiment #1; Edwards i Biblioteket (Kjerne); keramikk-sporet attende (H1). Bilete i `reference/formretning-2026-07/`; analyse i `research/2026-07-06-formretning-rotasjonsgrammatikk.md` |
| 28 | Verkstad | Skavl v0.3 vase-greina (= generator B / lamell-modus frå it. 27, no bygd): ny generator `verkstad/skavl/skavl_vase.py` med ribbe/slisse-grammatikk i staden for utstansa vindauge. Tre vasstette printbare søsken (d-vridd 44 ribber/112° twist, e-drope vertikale ribber/dropemunning, f-timeglas timeglas/115°); 89-98 g; opningsgrad 24-31 % (v0.2 sat fast på 6-8 %); ribberelieff står proud. Alle printfysikk-portar passerer. Twist klemt ned til FDM-printbar ribbekant (<50°) sidan ref er keramikk (flagga). 3D-render + validering + ref/README. Konvergens med it. 27-planen (parallelløkt): deira analyse, denne implementasjonen |
| 29 | Verkstad | Skavl v0.3 fekk fjerde søsken `g-rotor` (referanse-d/flat rotor): 56 rette vertikale finner, relieff 7 mm, opning 30 %, ribbekant-drift 0° (mest printbare). Printbarheit-funn dokumentert: den flate rotorskåla har vassrette veggar = FDM-overheng, så den printbare kusinen er ei ståande finne-søyle (form følgjer fitness: FDM-landskapet ≠ keramikklandskapet). 4-opp render + ref/README-funn |
| 30 | Verkstad | Generator B, LAMPE-greina (`verkstad/skavl/skavl_b.py`): rotasjonsgrammatikken som N radiale dropeforma lameller, tromme-topologi (komplementær til it. 28 vase-greina og it. 29 rotor: vase = ribberelieff/lukka botn, lampe = blendfokus/open lampeskjerm med E27-ring). Tre vasstette 3MF-søsken (roleg 24 finnar / open 18 / rotor 30 m/16° vriding), 115-120 g, overheng maks 45° (fasa toppring), alle harde portar passerte. Ope funn: radiale finnar stengjer berre 13-16 % av blendbandet (målt ved strålecasting), v0.2-arbeid. Silhuett-SVG + validering-b-v0.1.md + requirements.txt |
| 31 | Verkstad | Skavl v0.4 lampe-hybrid (`verkstad/skavl/skavl_lampe.py`), komplementaer til it. 30 skavl_b: rib/slisse-grammatikken fraa vasane paa lampa med glare/termikk paa att. To vasstette soesken (roleg/open), blend=0 ved konstruksjon (kvar slisse i glare-bandet lukka, oevre sone tett, konveksjonsslissar i nedre halvdel), termisk klaring 74-79 mm, E27-sokkel, opning 15 %. Alle portar. To ulike geometriske svar paa blendaksen: skavl_b lukkar 13-16 % med radiale finnar, skavl_lampe lukkar 100 % ved aa fjerne slissar i bandet |
| 32 | Meta | Loop-reframe (Ivers instruks «fully iterative design idea generator and designer, all the way to production models»): `LOOP.md` skriven om til ein design-motor med fem-fasa pipeline (frø to vekst to prøve to slip to produksjonsmodell), metode-meny for generativ vekst (differential growth, reaction-diffusion, L-system, fyllotaksi, Voronoi, TPMS m.m.), utvida valideringsport. CLAUDE.md + STATE + BACKLOG oppdaterte. Ny referanse `ref-e-tromme-linse.png` (femte form) lagt til, ny familie `h-tromme` i backloggen. Trigger-prompt oppdatert til design-misjonen |
| 33 | Meta | Globalt galleri (Ivers instruks «all future renders to a new global gallery database as images»): ny Notion-database «Galleri, render og iterasjonar» (data_source 82c18616...); alle render hamnar der som bilete. Mekanisme: `verkstad/tools/png_to_notion_svg.py` gjer PNG om til liten JPEG-data-URI-SVG som lastast opp inline (repoet er privat, so ingen offentleg URL). LOOP.md §5.6 + CLAUDE.md sync-kontrakt + manifest.json oppdaterte. Backfill: vase-familien v0.3 og lampe v0.4 er inne med embedda render |
| 34 | Synk | Konvensjonssveip i Notion (renummerert fraa 27 ved rebase): hovudsida, 01-05, Søknadspakke, 06 og alle fem Verkstad-sidene svepte for tankestrekar; Verkstad-titlane og Vegkart-databasen namna om (kolon/bindestrek); forelda branch-referanse på 06-sida retta til main. Attstår: select-opsjonar med intervall-strek (H1-H3), radinnhald i Bibliotek/Prinsipp |

## Retning frå Iver (2026-07-06, kveld)

**«This is the stuff we want to focus on, full effort loop, non stop
improvement.»** Fire referansebilete (truleg Steven Edwards-porselen) i
`reference/formretning-2026-07/` (og `verkstad/skavl/ref/`).
Rotasjonsgrammatikken er no den estetiske hovudretninga for
verkstadserien. Kjernegrepet: éin profil, rotasjonsarray, vertikal
stabling/morfing, og glasuren (eller print-analogen) som trykk-kart som
gjer kurvaturen lesbar. Analyse:
`research/2026-07-06-formretning-rotasjonsgrammatikk.md`. Loopen køyrer
kontinuerleg i tillegg til den daglege triggeren.

## Neste handling

Iterasjon 35 (Verkstad-tungt). Tre generator-B-greiner finst no: vase
(`skavl_vase.py`), rotor (`g-rotor`), og TO lampe-tilnaerminger (it. 30
`skavl_b.py` radiale lameller / it. 31 `skavl_lampe.py` rib-slisse med
glare-band lukka). Neste:
(a) **lampe blendaksen heilt loyst**: skavl_b lukkar berre 13-16 % av
blendbandet med radiale finnar, skavl_lampe lukkar 100 % men mister opning
i augelinja, kombiner dei (indre diffusor eller projeksjons-overlapp), maal
til 100 % blend + hoegare opning;
(b) samle Verkstad-oversyn: ein README for `verkstad/skavl/` som bind vase-,
rotor- og dei to lampe-greinene;
(c) materialeksperiment #1 (glasur-analog i print: silk-PETG laglys /
to-farge kant-hoeglys);
(d) reparasjonssett klips-protese-generator.
Sekundaert: Fjordfiesta (#4);
Case #3 Helsenorge.

## Parallell branch: `claude/generative-design-finalize-wwmnl6` (PR #2)

Ei sideøkt køyrde samstundes på denne branchen (ikkje main) og gjorde eit
eige spor. Merga inn hit; iterasjonsnummer kolliderte med main sine 27-31,
så branch-arbeidet er lista her i staden for i hovudtabellen:

- **Renderpipeline** `verkstad/render.py`: eigen NumPy z-buffer-rasteriser
  (headless OSMesa gav berre spekulær). Produktbilete på kvit botn for knagg
  + skavl; seinare porselen-rig (mjuk trelys + grå gradient) for Ribbe.
- **Skavl v0.3 slissar** via `skavl.py --v03` (modifiserer generator A).
  NB: overlappar main sitt it. 28 `skavl_vase.py` (uavhengig v0.3-slisse-
  implementasjon). To parallelle svar på same porøsitets-funn.
- **Reparasjonssett** `verkstad/repsett/repsett.py`: skøytehylse-familie
  (bøying/torsjon), vasstett, kintsugi-render.
- **Turntables** (`render.py --turntable`) for alle modellar.
- **Ribbe** `verkstad/radial/`: etter Ivers celadon-referanse. To feilspor
  (skjel på kule) før rett tolking `lattice.py`: eit vove gitter av runda
  rør med augehol (motfase-ribber, spline-glatta, organisk variasjon,
  krone/fot). Tre søsken korall/rev/søyle. **Overlappar main sitt generator
  B-spor** (skavl_b/skavl_lampe): begge tolkar referansen som radial/vove
  lampeform, ulik geometri. Konsolidering treng Iver.
- **Lykt** `verkstad/lykt/` (2026-07-08): Ivers fem keramikk-referansar
  (smultring, kuppel, ball, krone, terning) som boolsk generator, fem
  grunnformer, eitt regelverk. Utforskinga som fann grammatikken.
- **Krone** `verkstad/krone/` (2026-07-08, Ivers styring «fully
  parametric, merge and smoothen breps, same parameters different
  values»): EITT implisitt felt (smin/smax, marching cubes) med tre
  verdisett (taarn, krans, skaal), vasstette 3MF. Og **Krone Studio**
  `verkstad/krone/studio/`: interaktivt web-grensesnitt i same formspråk
  som parametric.iverfinne.no (botnark, presets, slidere, shuffle,
  lampelys-modus, STL-eksport, delbar URL); JS-feltet paritetstesta mot
  python (maks avvik 0,04 mm).

## Blokkert / treng Iver, VIKTIGAST FYRST

0. **To parallelle lampe-tolkingar av referansen** (branch-Ribbe vove gitter
   vs main generator B rib/lamell): kva retning skal førast vidare, eller
   skal begge leve? Konsolidering flagga.
1. **Namneval** (Skavl/Fonn/Morene/Skare/Formlære), står i Salone-skjemaet.
2. **Start knaggen denne veka** (kortast printsyklus; kritisk sti til 20. aug).
3. **Stadfest formreferansen:** er bileta Steven Edwards? (attribusjon
   truleg, ikkje verifisert, sjå formretning-notatet). Trengst før ekstern bruk.
4. Innsending Salone (30. aug) og Greenhouse (15. sep).
