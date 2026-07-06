# STATE.md, loop-state

**Iterasjon:** 28
**Sist oppdatert:** 2026-07-06
**Status:** Aktiv loop-køyring, fleire økter parallelt («køyr til tokena
er tomme», Ivers instruks 2026-07-06). All utvikling går direkte til
`main`. Dagleg trigger aktiv: «FORMLÆRE dagleg loop»
(trig_01DqhXRKkJof8qzmz8oHozmh, 05:00 UTC, ferskt miljø per køyring).

**Gjeldande styring frå Iver (2026-07-06):**
1. Konkrete designprosjekt fyrst: algoritmisk modellering for fysiske
   modellar Iver kan 3D-printe (Verkstad-tungt til ny beskjed).
2. Skrivekonvensjonar: ingen tankestrekar, ikon eller emojiar, i alt
   vidare arbeid (sjå CLAUDE.md).
3. Djup omstrukturering av Notion: hovudside som dashbord, kanban,
   kalender, tydelege databasar og lenkjer (neste store oppgåve).

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
| 21 | Research | Produsent #3 Northern: forlaget utan fabrikk; Northern Design Award (toårleg, studentar!) = døra inn for Skavl-lampa; Morten & Jonas som referansebane; flagga spenning utflagga produksjon vs. materialnærleik |
| 22 | Vegkart | Produsentlandskapet inn i 05 (git + Notion): tre arketypar (Superfabrikken/Arven/Forlaget) med kvar si dør; månadsrytmen kopla til case-planen sep-des |
| 23 | Verkstad | Skavl v0.2: pseudokoden implementert (`verkstad/skavl/skavl.py`), tre vasstette 3MF-søsken (107-120 g, overheng maks 45 grader, bru 7,9 mm, blendfri ved konstruksjon), valideringsrapport + silhuett-SVG. Funn: bru-budsjettet avgrensar porøsitet til 6-8 prosent (mål 30) og v0.3 = avlange slissar |
| 24 | Research | Kjeldesveip (parallelløkt, committa som «it. 23»): K4 (handlevogn), K5 (sparkesykkel, no 13/15) og K14 (LED, no 14/15, delt topp) ankra; K7 fann ikkje kjelde. RETTING: Northern-prisen heiter Northern Lighting Student Design Award (årleg, est. 2013); britiske «Northern Design Awards» er urelatert |
| 25 | Verkstad | Knagg #1 v0.1: tre hypotesar som printbar kode (`verkstad/knagg/knagg.py`): kraftlinje (moment-følgjande gods, PETG, 28 g, SF 9,0), kanalisert (kontroll, 27 g, SF 5,9), medvite-svak (designa brotsone, PLA, 26 g, predikert brotlast 10 kg). Vasstette 3MF liggjande på sida, validering + profil-SVG. Nye skrivekonvensjonar frå Iver inn i CLAUDE.md |
| 26 | Meta/Synk | Notion-omstrukturering (Ivers instruks): ny Oppgåver-database (17 rader, status/prioritet/frist/eigar) med kanban-, kalender- og Treng Iver-views; hovudsida bygd om til dashbord (No-seksjon øvst, Oppgåver inline, systemtabell nedst, alt gamalt bevart); konvensjonssveip i git (30 md-filer, tankestrekar og emojiar ute, kodeblokker urørte); manifest.json + notion/STRUKTUR.md |
| 27 | Verkstad | Renderpipeline ferdigstilt: `verkstad/render.py` (eigen NumPy z-buffer-rasteriser, sidan headless OSMesa berre gjev spekulær) lagar seks produktbilete på saumlaus kvit botn (to retningslys, ingen ambient, mjuk kontaktskugge). Lampa rendra tend (varmt innerskal, glødande vindauge); knaggen crease-medviten i bruksstilling. Bileta i `verkstad/renders/`, lagt til Notion Verkstad-sidene. NB: køyrer på tildelt branch `claude/generative-design-finalize-wwmnl6` (ikkje main), jf. sesjonsinstruks; PR opna. Følgt opp: familiebilete (tre søsken side om side, 27b), lampene på SS=4 med per-formål supersampling (27c) |
| 28 | Verkstad | Skavl v0.3: slissar i lagretninga (`skavl.py --v03`). Same kropp, ny vindaugsstrategi: lange tynne vertikale slissar, minimale web (3 mm). Opningsgrad opp frå 6-8 % (v0.2) til 10-18 % (v0.3, b-open 18 %). FUNN: den bindande skranken er ikkje print (bru) men optikk (blendbandet fjernar øvre halvdel av lo-sida), difor ikkje 30 %. Nye 3MF (`-v03`), validering-v0.3.md, tre nye renders + familiestripe. v0.2-filene bevart |

## Neste handling

Iterasjon 28: Skavl v0.3 (avlange slissar i lagretninga for meir opning),
og/eller reparasjonssett-generator. Renderpipelina kan gjenbrukast for
begge (`verkstad/render.py`, legg nye familiar til i `MODELS`). Vurder
turntable-bilete (`--turntable`) og ei lita galleri-side i Notion.
Framleis att: konvensjonssveip i Notion-undersidene (01-05, Søknadspakke).

## Blokkert / treng Iver, VIKTIGAST FYRST

1. **Namneval** (Skavl/Fonn/Morene/Skare/Formlære), står i Salone-skjemaet.
2. **Start knaggen denne veka** (kortast printsyklus; kritisk sti til 20. aug).
3. Innsending Salone (30. aug) og Greenhouse (15. sep).
