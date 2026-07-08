# Krone, ein fullt parametrisert lampeskjerm

> Ivers styring 2026-07-08: «really make it parametric, make interface
> similar to parametric.iverfinne.no, should merge and smoothen breps,
> fully possible to make with the same parameters but with different
> values». Dette er svaret: EITT parametersett, tre verdisett, og eit
> interaktivt studio.

## Konstruksjonsprinsippet

Forma er ikkje bygd av harde boolske kutt men som eit **implisitt felt**
(signert distanse-aktig), der kvar detalj er ein mjuk union eller mjuk
subtraksjon (polynomisk smin/smax). Overgangane smeltar difor saman med
kontrollert radius, det er «merge and smoothen» som konstruksjonsprinsipp,
ikkje etterarbeid. Feltet er n-periodisk kring aksen: heile lykta er
definert av eitt segment.

Parametrane (same namn i alle tre implementasjonane):

| gruppe | parametrar | kva |
|---|---|---|
| form | n, H, R_b, R_t, bulge, t | omdreiingsvegg, buk, gods |
| krone | crown_h1/w1/split, crown_h2/w2, crown_k | toppkanten som mjuk funksjon av vinkelen: hornpar paa saumane, nabb paa midten, smelteradius |
| vindauge | hole_zf/r0/r1/len/k | ujamn kapsel per segment: oval, egg eller draape |
| naalehol | pins[] (moenster, posisjon, storleik) | punktklynger som slepp lys ut |
| perler | beads[] | kuler smelta inn paa saumane |
| panel | pillow, groove_d/w, band_z | putebulging per panel, saumriller, horisontalt band |
| liner | liner (gap, t, top, hole) | indre skal med eige mindre vindauge |

Tre verdisett, same kode:

| sysken | les | referanse |
|---|---|---|
| taarn | hoeg sylinder, tvillinghorn, hoege ovalar, liner | ref-bilete 1 (krone-lykta) |
| krans | flat 45-graders ring, mjuke toppar, eggformer | ref-bilete 2 (krone-ringen) |
| skaal | utoverflara kjegle, eitt horn per saum | fritt, prov paa generalitet |

## Filene

| fil | kva |
|---|---|
| `krone.py` | produksjonsvegen: feltet paa 0,8 mm voxelgitter, marching cubes, taubin-glatting, desimering, pinch-reparasjon, vasstett 3MF |
| `print/krone-*.3mf` | dei tre syskena, klare til slicing |
| `validering-v01.md` | maaltal, generert av scriptet |
| `studio/` | **Krone Studio**: interaktivt web-grensesnitt i same formspraak som parametric.iverfinne.no |

## Krone Studio (`studio/`)

Statisk web-app utan byggjesteg: `index.html` + `worker.js` + vendored
three.js. Feltet er porta 1:1 til JavaScript (paritetstesta mot krone.py,
maks avvik 0,04 mm) og polygonisert live med naive SurfaceNets i ein Web
Worker.

- botnark med preset-segment (Taarn, Krans, Skaal), pause, lampelys,
  shuffle, STL-nedlasting og kollaps, som parametric.iverfinne.no
- alle parametrane som slidere i grupper (form, krone, vindauge, detalj)
- lampelys-modus: varmt punktlys inne i skjermen, so ein ser lysbiletet
- parametrane ligg alltid i URL-en (delbar lenkje)
- nedlasting byggjer STL-en paa nytt i hoeg opploeysing (res 320)

Koeyr lokalt: `python3 -m http.server` i `studio/` og opna localhost.
Naalehol under voxelstorleiken vert klemde opp til pitchen i
foerehandsvisinga (eksakte i eksporten), elles gjev dei berre stoey.

## Kjende avgrensingar

- SurfaceNets-STL-en fraa studioet kan ha nokre faa pinch-kantar
  (sjoelvtangerande flater); slicerar reparerer dei stille. Den
  garantert vasstette vegen er `krone.py`.
- Studio-liner er forenkla (fast gods 4 mm, fast topp).

## Traktat-kopling

- **5.31:** tre trajektoriar gjennom same grammatikk, verdisett i
  `VARIANTS`/`PRESETS`.
- **2.1:** klemmene (crest, golv, vindaugsbudsjett) er projeksjonar i
  feltet, aldri straffeledd.
- **1.321:** valideringsrapporten og paritetstesten er projeksjonane som
  gjer trykka synlege.
