# STATE.md — loop-state

**Iterasjon:** 23
**Sist oppdatert:** 2026-07-06
**Status:** Aktiv loop-køyring, fjerde økt («køyr til tokena er tomme»,
Ivers instruks 2026-07-06). All utvikling går direkte til `main`.
Dagleg trigger aktiv: «FORMLÆRE dagleg loop»
(trig_01DqhXRKkJof8qzmz8oHozmh, 05:00 UTC, ferskt miljø per køyring).

**Gjeldande styring frå Iver (2026-07-06, fjerde økt):** prioriter
konkrete designprosjekt — algoritmisk modellering o.l. for fysiske
modellar Iver kan 3D-printe. Verkstad-tungt til ny beskjed; balanse-
regelen i LOOP.md §4 vik for denne styringa.

## Iterasjonshistorikk (denne økta)

| # | Kategori | Kva |
|---|---|---|
| 0 | Grunnlegging | Notion-prosjekt + repo + loop-protokoll |
| 1 | Research | Konkurransefristar: 🔴 Salone 30/8, 🔴 Greenhouse 15/9 → H0 komprimert |
| 2 | Verkstad | Designbrief Knagg #1 (aksar kvantifisert, testplan, EN-skildring) |
| 3 | Verkstad | Designbrief Skavl-lampe (generativ form, tre søsken) |
| 4 | Verkstad | Designbrief Reparasjonssett (kintsugi for plast) + trio-grunngjeving |
| 5 | Research | Norway Says → grammatikken er limet; exit-plan frå dag éin |
| 6 | Skriving | Søknadspakke Salone+Greenhouse: sjekklister, EN-presentasjon, standkonsept «Le-sida» |
| 7 | Skriving | Manifest v1.0 → Klar i Notion (git-committen vart tom; retta i it. 8) |
| 8 | Synk/Meta | Drift retta: STATE/BACKLOG à jour med it. 7; branch-referansar oppdaterte etter merge av PR #1 |
| 9 | Skriving | Case #1 «Leskuret som ikkje gjev le» — fullt utkast, 9 kjelder, trykktabell, karusell-skisse; Fase Idé→Utkast |
| 10 | Research | AHO-miljøet kartlagt: Bjørnstad (formgjeving) ⭐, Abrahamsen (ph.d.), Killi (AM/instituttleiar), Nordby; kontaktrekkjefølgje inn i H0/H1 |
| 11 | Verkstad | Skavl-algoritme v0.1: kurve-stabel-arkitektur, pseudokode, 17 parametrar, metode-referansar; spegla på Verkstad-sida |
| 12 | Vegkart | Studieløpet inn i H0/H1: 4. år = einaste utvekslingsår; frist vårutveksling = 15. sep (= Greenhouse!); spenning Salone×utveksling flagga |
| 13 | Research | Brotmodus-taksonomi v0.1: 10 modusar frå ORA-data + snap-fit-litteratur; klips-protese opp som eiga delfamilie; PETG-tilråding |
| 14 | Research | Produsent #1 Vestre: motmodellen til Case #1 (varigheit i staden for reklame); Munch-serien kom frå open konkurranse; Snøhetta-kopling |
| 15 | Skriving | Case-idébank: 9 kandidatar + månadsplan sep–des (benk m/midtarmlene → Helsenorge → motcase); prinsipp for banken (parallelløkt) |
| 16 | Skriving | Case-idéliste Designopprøret: 10 kandidatar skåra mot 5 kriterium; tilrådd #2 = benken med midtarmlene (fiendtleg design), #3 = panteautomaten (motmodell); ny rad i Skriveprosjekt (Idé). NB: parallell med it. 15 — same konklusjon om benken |
| 17 | Synk | Konsolidering: idébank (it. 15) + idéliste (it. 16) → éi kanonisk liste v0.2 (16 kandidatar, månadsplan sep–des, prinsipp); idebank-fila er peikar; Notion-rada oppdatert; motcase flytt til desember (flagga) |
| 18 | Research | Produsent #2 Eikund: arven som forretningsmodell; gullalder-diagnosen stadfesta empirisk; flagga spenning «grammatikk eller museum»; inngang = «det manglande møbelet»; Northern/Fjordfiesta står att |
| 19 | Skriving | Case #2 «Benken du ikkje kan liggje på» — fullt utkast: 4 nivå, trykktabell, Bjørvika-empiri (namngjevne kritikarar + Lynnebakken-avvisinga), Camden/Savić, 9 kjelder, karusell-skisse; Skriveprosjekt-rad (Utkast, frist 1. okt) |
| 20 | Verkstad | Alle tre briefane rulla til v1.1 mot brotmodus-taksonomien: knagg (test per lastretning, krypmåling, PETG/designa svak sone), lampe (termikk-modus, PETG-vurdering, snap-rot), repsett (fem delfamiliar, hylse i to variantar, 50 N per modus); spegla til Verkstad-sidene |
| 21 | Research | Produsent #3 Northern: forlaget utan fabrikk; Northern Design Award (toårleg, studentar!) = døra inn for Skavl-lampa; Morten & Jonas som referansebane; flagga spenning utflagga produksjon vs. materialnærleik |
| 22 | Vegkart | Produsentlandskapet inn i 05 (git + Notion): tre arketypar (Superfabrikken/Arven/Forlaget) med kvar si dør; månadsrytmen kopla til case-planen sep–des |
| 23 | Verkstad | Skavl v0.2: pseudokoden implementert (`verkstad/skavl/skavl.py`) — tre vasstette 3MF-søsken (107–120 g, overheng ≤ 45°, bru ≤ 7,9 mm, blendfri ved konstruksjon), valideringsrapport + silhuett-SVG; funn: bru-budsjettet avgrensar porøsitet til 6–8 % (mål 30 %) → v0.3 = avlange slissar. Parallelløkt-kollisjon på iterasjonsnummer løyst ved rebase (20→23) |

## Neste handling

Iterasjon 24 (Verkstad-styring frå Iver): Knagg #1 som parametrisk,
printbar modell (kortast printsyklus, kritisk sti til 20. aug) ELLER
Skavl v0.3 (avlange slissar → porøsitet mot 30 %). Deretter:
reparasjonssettet som klips-protese-generator kopla til
brotmodus-taksonomien. NB: parallelløkt kan vere aktiv — fetch før
persistence (LEARNINGS).

## Blokkert / treng Iver — VIKTIGAST FYRST

1. **Namneval** (Skavl/Fonn/Morene/Skare/Formlære) — står i Salone-skjemaet.
2. **Start knaggen denne veka** (kortast printsyklus; kritisk sti til 20. aug).
3. Innsending Salone (30. aug) og Greenhouse (15. sep).
