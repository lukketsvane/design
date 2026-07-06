# Skavl v0.2, frå pseudokode til printbar geometri

> Iterasjon 20 (2026-07-06). Implementerer `briefs/skavl-algoritme.md`
> (v0.1-pseudokoden) som køyrande kode. Tre søsken, éin grammatikk, 
> klare til slicing.

## Kva ligg her

| Fil | Kva |
|---|---|
| `skavl.py` | Generatoren: vekst → klemmer → vindauge → loft → validering |
| `print/skavl-a-roleg.3mf` | Søsken A «roleg», færre vindauge, glattare (frø 11) |
| `print/skavl-b-open.3mf` | Søsken B «open», mest porøs, mest vêr (frø 23) |
| `print/skavl-c-asketisk.3mf` | Søsken C «asketisk», slankast, 107 g (frø 37) |
| `validering-v0.2.md` | Måltala (generert av scriptet, pseudokode-steg 6) |
| `silhuett-v0.2.svg` | Sideoppriss av dei tre søskena med vindaugsprikkar |

Køyr på nytt: `python3 skavl.py` (treng `numpy` + `trimesh`; deterministisk
per frø, same frø gjev same form, det er reproduserbarheits-poenget).

## Arkitekturen (og kva som avvik frå v0.1-pseudokoden)

Kurve-stabelen er implementert som eit radiusfelt r(θ, z): kvar ring arvar
ringen under, veks med frøa støy vekta av vindfeltet (le = glatt/tett,
lo = porøs/open), og vert så projisert gjennom dei harde klemmene, 
overheng (45°-drift per ring, 5° margin mot 50°-budsjettet), termikk-golv
(70 mm i LED-bandet = pæreradius 30 + 40 klaring), format (35-110 mm).
Vindauga er celler fjerna frå gitteret på lo-sida, med bru- (≤ 8 mm) og
web-budsjett (≥ 3 mm) handheva ved konstruksjon, og deretter lofta til
vasstett solid med 1,0 mm vegg.

Tre medvitne avvik frå pseudokoden, alle grunngjevne:

1. **Stjerneforma ringar** (r som funksjon av θ): sjølvkryss vert umogleg
   ved konstruksjon, så fråstøytingsleddet (`F_fråstøyt`) fell bort.
   Foldane frå ekte differential growth kjem attende i v0.3 om me løftar
   restriksjonen (då trengst fråstøyt + rhino3dm-loft).
2. **Grunnprofil-ledd** (`W_PROFIL`): rein støyvekst under klemmer driv
   mot formatboksen; eit svakt drag mot ein teikna silhuett (krage →
   bul ved LED → innsving) gjev lampeproporsjonar. Støyen er vêret,
   profilen er terrenget.
3. **Blendfri ved konstruksjon, ikkje ved ettersjekk:** inga vindaugscelle
   får ha siktline frå LED-senteret med elevasjon i bandet −5° til 60°
   (sitjande til ståande auge i vanleg rom). Konveksjonen går difor
   gjennom dei låge vindauga og ut toppopninga, skorsteinsverknad, 
   i staden for opningar rett ved kjelda.

## Funn v0.2 (til neste iterasjon)

- **Bru-budsjettet er den bindande skranken på porøsitet.** Målet var
  ~30 % opning på lo-sida; budsjetta (bru ≤ 8 mm, web ≥ 3 mm, blendband,
  ingen diagonalkontakt) gjev 6-8 %. Vil ein ha meir lys ut, må vindauga
  bli avlange slissar i lagretninga (bru-spennet er per lag, høgda er
  gratis), v0.3-kandidat, og han styrkjer skuggeteikninga.
- **Klemmene ber forma:** p95-overhenget ligg nøyaktig på drift-klemma
  (45°). Store delar av skalet «rid» på budsjettet, seleksjonstrykket
  er synleg i geometrien, slik traktat 2.1 vil ha det.
- Diagonal vindaugskontakt gjev ikkje-manifold pinch-kantar (og
  spenningspunkt i print); regelen «ingen diagonalkontakt» er no del av
  grammatikken.

## Slicing (frå briefen + implementasjonsnotatet)

PrusaSlicer: 2 perimeter à 0,5 mm (= vegg 1,0 mm), 0 % infill (veggen er
alt), «detect bridging perimeters» på, ingen support. Samanlikn slicerens
overhengsvarsel med histogramtala i valideringsrapporten, avvik tyder
feil i klemma. Print-timelapse frå fyrste testprint (lag = snøfall) er
dokumentasjonskravet frå briefen.

**Mål før print:** E27-kragen er sett til r = 22,3 mm (22 + 0,3 toleranse)
og pæresenteret til z = 130 mm, mål den faktiske fatninga og pæra, og
juster `R_SOKKEL`/`Z_LED` før fyrste print.

## Traktat-kopling

- **5.31:** `SIBLINGS`-tabellen er tre trajektoriar gjennom same
  grammatikk; frøa er loggførte i valideringsrapporten.
- **2.1:** klemme-stega er projeksjonar, aldri straffeledd, sjå
  `grow()`, steg 3.
- **1.321:** `validering-v0.2.md` er projeksjonen som gjer flest trykk
  synlege; han vert generert på nytt ved kvar køyring.
- **3.4/3.41:** om printane konvergerer mot sastrugi/trabekel utan at me
  teikna det: loggfør likskapen (uavhengig konvergens).

---

## Generator B: rotasjonsgrammatikken (v0.1, iterasjon 28)

> Retningsendring frå Iver (referansebileta i `reference/formretning-2026-07/`,
> analyse i `research/2026-07-06-formretning-rotasjonsgrammatikk.md`). Der
> generator A veks eit kontinuerleg skal, byggjer generator B lampa av N
> radiale, dropeforma lameller: éin profil kopiert kring aksen. Tromme-
> topologi (som referanse 01, 02, 04), ikkje lukka kuppel: det er den lette,
> print-vennlege forma.

| Fil | Kva |
|---|---|
| `skavl_b.py` | Generator B: profil → rotasjonsarray → ringar → union → validering |
| `print/skavl-lamell-roleg.3mf` | 24 finnar, roleg buk (frø 11), 115 g |
| `print/skavl-lamell-open.3mf` | 18 finnar, opnast, feitast buk (frø 23), 115 g |
| `print/skavl-lamell-rotor.3mf` | 30 finnar, 16° vriding (rotor, frø 37), 120 g |
| `validering-b-v0.1.md` | Måltala, generert av scriptet |
| `silhuett-b-v0.1.svg` | Éin lamell-profil kopiert kring aksen |

Køyr: `python3 skavl_b.py` (treng `numpy`, `trimesh`, `shapely`,
`manifold3d`, `rtree`; deterministisk per frø).

### Kva passerer, og kva er ope funn

Harde portar (alle tre søsken): vasstett solid, masse 115-120 g (< 150),
overheng maks 45° (< 50, 0 % areal over budsjett). Rotasjonsarrayen gjev
vertikale finneflankar (null overheng); den einaste overheng-kjelda,
den flytande toppringen, har fasa underside på 45°.

**Ope funn (blendaksen):** radiale finnar kring ei punktkjelde stengjer
berre 13-16 % av blendbandet, ein stråle rett ut i gapet mellom to
finnar slepp forbi. Målt ved strålecasting, ikkje gøymd. v0.2 må svare:
(a) tynn indre diffusor-sylinder i blendbandet, (b) breiare/tettare
lamellar med projeksjons-overlapp, eller (c) medviten retningslampe.
Dette er generator B sitt v0.1-funn, parallellen til generator A sitt
funn om at bru-budsjettet avgrensar porøsiteten.

### Materialeksperiment #1 (glasur-analogen), ventar

Referansens glasur poolar i dalane og tynnast på eggane, kurvatur vert
farge. Print-analogen (silk-PETG laglys / to-farge kant-høglys / polert
egg mot matt dal) er ikkje geometri men overflate, og høyrer til
testprint-fasen `[TRENG IVER]`.
