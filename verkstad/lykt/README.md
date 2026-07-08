# Lykt v0.1, fem grunnformer, eitt regelverk

> Iterasjon paa Ivers referansebilete 2026-07-08 (fem keramikk-lykter:
> smultring, kuppel, ball, krone, terning). Fyrste svar var dette
> boolske settet; Iver styrte deretter mot EI form fullt parametrisert
> med mjuke overgangar, det ligg i `../krone/`. Dette settet staar att
> som utforskinga som fann grammatikken.

Grammatikken: tjukt skal paa ein grunnform, store ovale utskjeringar
borra radielt, naalehol-klynger (diamant, rosett, trekant), perler paa
saumpunkta, krone-piggar og finialar. Alt bygd med harde boolske
operasjonar (manifold3d), so overgangane er skarpe, ikkje smelta; det
var den synlege skilnaden fraa referansane som foerte til feltbygginga
i `../krone/`.

| variant | grunnform | boks (mm) |
|---|---|---|
| kuppel | sfaerisk kuppel med stroppar og gap | 191 x 183 x 97 |
| ball | trunkert ikosaeder, pentagonhol, heksagon-rosettar | 168 x 166 x 160 |
| krone | sylinder med buk, ovale vindauge, skulpturert kronekant | 141 x 142 x 187 |
| smultring | torus med tre holringar og nabbar | 193 x 194 x 65 |
| terning | superellipse-prisme, vesica-vindauge | 108 x 108 x 101 |

Koeyr: `python3 lykt.py` (numpy, trimesh, shapely, manifold3d).
Render: `python3 ../render.py --lykt --ss 1` (raske kontrollbilete).
Maaltal i `validering-v01.md`.
