# Skavl v0.4 lampe-hybrid, valideringsrapport (`skavl_lampe.py`)

> Ribbe/slisse-grammatikken fraa vase-v0.3 paa lampa, med glare- og
> termikk-klemmene paa att. Blendfri ved konstruksjon: ingen slisse
> i glare-bandet; konveksjon gjennom dei laage slissane, ut toppen.

| Maaltal | Krav | lampe-roleg | lampe-open |
|---|---|---|---|
| Fro | loggfort | 511 | 622 |
| Ribber | - | 40 | 44 |
| Twist | - | 70 grader | 95 grader |
| Vasstett solid | ja | True | True |
| Masse (PLA) | < 150 g | 111 g | 117 g |
| Masse (PETG) | < 150 g | 113 g | 119 g |
| Sokkelradius (E27 + tol) | ~22.3 mm | 22.3 mm | 22.3 mm |
| Termisk klaring (LED-band) | >= 70 mm | 73.6 mm | 79.5 mm |
| Vindauge i glare-bandet | 0 | 0 | 0 |
| Overheng maks (skal) | < 50.0 grader | 45.0 grader | 45.0 grader |
| Skalareal over budsjett | < 1 % | 0.00 % | 0.00 % |
| Ribbekant-drift | < 50.0 grader | 37.3 grader | 49.3 grader |
| Bru, maks slissespenn | <= 8.0 mm | 6.3 mm | 6.5 mm |
| Opningsgrad heile flata | - | 15 % | 15 % |
| Fil | - | `print/lampe-roleg.3mf` | `print/lampe-open.3mf` |

Glare-bandet [-5, 60] grader elevasjon fraa LED (z = 130 mm)
er heilt lukka, augehoegd ser aldri den nakne paera gjennom ein slisse.
Dei laage slissane (under LED) er opne som konveksjonsinntak.
