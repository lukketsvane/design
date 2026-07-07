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
| `ref-d-vertikale-finner.png` | Djupe frittståande radielle finner med ovale hol; nesten rett sylinder, kastellert topp | Radiell djupn utover skalet via ribberelieff; rette vertikale finner | Realisert som søsken `g-rotor` (v0.3): 56 finner, twist 0, relieff 7 mm, opning 30 %, ribbekant-drift 0 grader (mest printbar) |
| `ref-e-tromme-linse.png` (ny 2026-07-07) | Brei tromme/tønne, vertikale bølgjande lameller, store linse-/augeforma opningar mellom dei, kastellert topp og botn | Same ribbe/slisse-grammatikk som ref-b, men brei sylinder (h omtrent lik diameter) og sterk drope-envelope = store linser; djup ribberelieff | Ny familie `h-tromme` (v0.5): brei rett profil, 30-36 ribber, twist 0, kraftig drope_styrke for linsene, relieff 6-8 mm. Utstår til komande iterasjon |

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

## Printbarheit-funn (it. 29): den flate rotoren er ei keramikk-form

Referanse-d / den flate rotorskåla (jf. `reference/formretning-2026-07/
04-flat-rotor.jpeg`) har nesten vassrette veggar. Printa stråleorientert
(ståande) i FDM vert det store overheng utan støtte; forma er ei
omnbrend keramikk-form, ikkje ei stråle-form. Den *printbare* kusinen
til rotor-estetikken er ei ståande søyle med mange rette vertikale
finner og djupe slissar, difor er `g-rotor` høg og rett, ikkje flat.
Dette er «form følgjer fitness» i praksis: seleksjonslandskapet (FDM
stråle) tvingar ei anna form enn keramikklandskapet, sjølv med same
grammatikk (radial repetisjon). Ei ekte flat skål høyrer heime i
resin/SLA eller med støtte, eit eige spor om Iver vil.

Generator: `skavl_vase.py` (v0.3, fire søsken d/e/f/g).
Validering: `validering-vase-v0.3.md`. Render: `render-v0.3.png`.
