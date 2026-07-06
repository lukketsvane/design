# Skavl v0.2 — valideringsrapport (generert av `skavl.py`)

> Pseudokode-steg 6 i `briefs/skavl-algoritme.md`: måltala før print.
> Traktat 1.321: denne rapporten er projeksjonen som gjer flest
> seleksjonstrykk synlege — legg han ved kvar print.

| Måltal | Krav | a-roleg | b-open | c-asketisk |
|---|---|---|---|---|
| Frø | loggført | 11 | 23 | 37 |
| Vasstett solid | ja | True | True | True |
| Masse (PLA 1,24 g/cm³) | < 150 g | 120 g | 119 g | 107 g |
| Overheng, maks (skal) | < 50.0° | 45.0° | 45.0° | 45.0° |
| Overheng, p95 | — | 45.0° | 45.0° | 45.0° |
| Skalareal over budsjett | < 1 % | 0.00 % | 0.00 % | 0.00 % |
| Bru, maks vindaugsspenn | ≤ 8.0 mm | 7.9 mm | 7.9 mm | 7.9 mm |
| Vindauge i blendbandet | 0 | 0 | 0 | 0 |
| Vindauge (celler) | — | 1219 | 1480 | 1432 |
| Opningsareal | — | 3156 mm² | 3917 mm² | 3760 mm² |
| Opningsgrad lo-sida | ~30 % mål | 6 % | 8 % | 8 % |
| Største radius | ≤ 110.0 mm | 92.9 mm | 94.7 mm | 80.7 mm |
| Høgd | — | 240 mm | 240 mm | 240 mm |
| Fil | — | `print/skavl-a-roleg.3mf` | `print/skavl-b-open.3mf` | `print/skavl-c-asketisk.3mf` |

Blendfri ved konstruksjon: ingen vindaugscelle har siktline frå
LED-senteret (z = 130 mm) med elevasjon i bandet [-5°, 60°]. Konveksjon går
gjennom dei låge vindauga på lo-sida og ut toppopninga (skorstein).
