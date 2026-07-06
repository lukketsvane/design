# Referansebilete frå Iver (2026-07-06)

Fire generative, glaserte vasar (celadon-aktig overflate) sende av Iver
med beskjeden «this is the stuff we want to focus on, full effort loop
non stop improvement». Dette er formverda Skavl-grammatikken skal treffe.
Bileta er retning, ikkje fasit: me kopierer ingen former, me les ut
*grammatikken* deira og genererer våre eigne (jf. traktat 5.31).

**Kryssreferanse:** ei parallell loop-økt fekk eit komplementært sett
Edwards-referansar (chevron-krone, gitter-torus, kuppel, flat rotor) i
`reference/formretning-2026-07/`, med ei full traktatlesing i
`research/2026-07-06-formretning-rotasjonsgrammatikk.md`. Denne fila er
den print-tekniske dekomponeringa som generator B (`skavl_vase.py`) er
bygd på; det notatet er den estetiske/strategiske lesinga. Dei to
utfyller kvarandre. Attribusjon (truleg Steven Edwards) er `[TRENG IVER]`
å stadfeste før ekstern bruk.

## Formal dekomponering, bilete for bilete

| Fil | Kva me ser | Grammatikk-lesing | Generator-parameter |
|---|---|---|---|
| `ref-a-vridd-lamell.png` | Tett diagonal lamellstruktur, vridd kring eit volum med innsnøring; avrunda kvadratisk munning; slissane går nesten heile høgda | Ribber som primærstruktur, opningane er *mellomromma*, ikkje hol i eit skal; vriding gjev diagonal retning | Mange ribber (40+), twist 120-150 grader, m=4-harmonisk mot toppen, kontinuerlege slissar |
| `ref-b-trompet-drope.png` | Vertikale bølgjande ribber som møtest og skilst; dropeforma opningar; trompetutsving i toppen, lauk-basis | Ribbesenter med lågfrekvent vibrering; slisse-envelopen pulserer (klemmer att og opnar) = dropene | Ingen twist, rib-wobble av frøa støy, drope-envelope med vertikal bølgjelengd, flare i silhuetten |
| `ref-c-timeglas-slissar.png` | Vridde ribber, avlange linseforma slissar, timeglas-silhuett, trekanta munning | Som A men færre ribber og lengre pinch-rytme; m=3-harmonisk | Twist ~120 grader, slisse-pinch midt på, m=3 mot toppen |
| `ref-d-vertikale-finner.png` | Djupe frittståande radielle finner med ovale hol; nesten rett sylinder, kastellert topp | Radiell djupn utover skalet, eiga grein (krev finne-geometri, ikkje skal-celler) | Utsett til v0.4: finnemodus med radiell ekstrusjon |
| (femte fil) | Dublett av ref-b (same md5) | | |

## Kva dette endrar i Skavl

1. **Frå vindauge til slissar.** v0.2 stansa ut celler i eit skal og
   møtte bru-budsjettet som tak: 6-8 prosent opning mot 30 i mål.
   Referansane snur logikken: ribbene er strukturen, opningane er
   kontinuerlege slissar *langs* ribberetninga. Då er det einaste
   bru-spennet sjølve slissebreidda (4-8 mm), og opningsgraden kan gå
   til 30-50 prosent utan å bryte printfysikken.
2. **Vase-greina.** Bileta er vasar: inga lyskjelde, altså ingen blend-
   og termikk-klemmer. Same grammatikk, nytt seleksjonslandskap (5.31),
   det gjev tre nye søsken som Iver kan printe med ein gong, og
   lampe-versjonen (v0.4) arvar slisse-logikken med blendbandet på.
3. **Munning som harmonisk.** Avrunda kvadrat/trekant i munninga =
   låg-ordens cos(m*theta)-ledd som veks mot toppen og roterer med
   twisten.

Generator: `skavl_vase.py` (v0.3). Validering: `validering-vase-v0.3.md`.
