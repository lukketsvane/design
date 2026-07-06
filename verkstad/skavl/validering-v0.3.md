# Skavl v0.3, valideringsrapport (generert av `skavl.py`)

> Pseudokode-steg 6 i `briefs/skavl-algoritme.md`: måltala før print.
> Traktat 1.321: denne rapporten er projeksjonen som gjer flest
> seleksjonstrykk synlege, legg han ved kvar print.

| Måltal | Krav | a-roleg | b-open | c-asketisk |
|---|---|---|---|---|
| Frø | loggført | 11 | 23 | 37 |
| Vasstett solid | ja | True | True | True |
| Masse (PLA 1,24 g/cm³) | < 150 g | 118 g | 113 g | 105 g |
| Masse (PETG 1,27 g/cm³, jf. brief v1.1) | < 150 g | 121 g | 116 g | 107 g |
| Overheng, maks (skal) | < 50.0° | 45.0° | 45.0° | 45.0° |
| Overheng, p95 | - | 45.0° | 45.0° | 45.0° |
| Skalareal over budsjett | < 1 % | 0.00 % | 0.00 % | 0.00 % |
| Bru, maks vindaugsspenn | ≤ 8.0 mm | 8.0 mm | 8.0 mm | 7.9 mm |
| Vindauge i blendbandet | 0 | 0 | 0 | 0 |
| Vindauge (celler) | - | 1886 | 3259 | 2229 |
| Opningsareal | - | 4976 mm² | 8817 mm² | 5809 mm² |
| Opningsgrad lo-sida | ~30 % mål | 10 % | 18 % | 13 % |
| Største radius | ≤ 110.0 mm | 92.9 mm | 94.7 mm | 80.7 mm |
| Høgd | - | 240 mm | 240 mm | 240 mm |
| Fil | - | `print/skavl-a-roleg-v03.3mf` | `print/skavl-b-open-v03.3mf` | `print/skavl-c-asketisk-v03.3mf` |

Blendfri ved konstruksjon: ingen vindaugscelle har siktline frå
LED-senteret (z = 130 mm) med elevasjon i bandet [-5°, 60°]. Konveksjon går
gjennom dei låge vindauga på lo-sida og ut toppopninga (skorstein).
