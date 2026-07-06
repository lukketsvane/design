# Skavl generator B v0.1, valideringsrapport (generert av `skavl_b.py`)

> Rotasjonsgrammatikken (retningsendring frå Iver, referansebileta).
> Same valideringsport som generator A, men blendinga er MÅLT ved
> strålecasting, ikkje garantert ved konstruksjon (sjå funn nedst).

| Måltal | Krav | lamell-roleg | lamell-open | lamell-rotor |
|---|---|---|---|---|
| Lamellar | - | 24 | 18 | 30 |
| Frø | loggført | 11 | 23 | 37 |
| Vasstett solid | ja | True | True | True |
| Masse (PLA 1,24 g/cm³) | < 150 g | 115 g | 115 g | 120 g |
| Masse (PETG 1,27 g/cm³) | < 150 g | 118 g | 118 g | 123 g |
| Overheng, maks | < 50.0° | 45.0° | 45.0° | 45.0° |
| Areal over overhengbudsjett | < 1 % | 0.00 % | 0.00 % | 0.00 % |
| Blendband stengt (målt) | mål 100 % | 13 % | 16 % | 16 % |
| Største radius | ≤ 108.0 mm | 93.5 mm | 100.7 mm | 91.2 mm |
| Høgd | - | 196 mm | 196 mm | 196 mm |
| Trekantar | - | 29024 | 23176 | 36354 |
| Fil | - | `print/skavl-lamell-roleg.3mf` | `print/skavl-lamell-open.3mf` | `print/skavl-lamell-rotor.3mf` |

## Funn v0.1

Radiale finnar kring ei punktkjelde stengjer ikkje heile blendbandet:
ein stråle som går rett ut i gapet mellom to finnar slepp ut. Målinga
over seier kor mykje kvart søsken faktisk stengjer. Dette er eit reelt
seleksjonstrykk aksen må svare på i v0.2: anten (a) ein tynn indre
diffusor-sylinder i blendbandet, (b) tettare/breiare lamellar med
overlapp i projeksjon, eller (c) å godta at lampa er ein *retnings*-
lampe (blendfri berre i visse azimut). Traktat 5.6: omhugen langs
blendaksen er no synleg og målt, ikkje gøymd.
