# Skavl-lampe: Algoritmespesifikasjon (v1, 2026-07-06)

Implementasjonsspesifikasjon for vekstalgoritmen i `skavl-lampe.md`.
Målgruppe: Iver (grunnleggjande Grasshopper/Python). Alt her skal kunne
byggjast med Rhino 7/8 + Grasshopper + plugin-ane Anemone, Kangaroo2 og
Weaverbird, pluss GhPython-komponentar på ~100–300 linjer kvar. Prosa på
nynorsk; all pseudokode og alle parameternamn på engelsk.

---

## 1. Val av vekstprinsipp

Tre kandidatar vart vurderte mot dei seks aksane i briefen:

| Kriterium | Differential growth (mesh) | Space colonization | Reaction-diffusion |
|---|---|---|---|
| Output-type | Flate (skal) — **er** skjermen direkte | Greinskjelett (linjer) — må «pipast» til solid etterpå | Skalarfelt/tekstur — må leggjast **på** ei ferdig teikna flate |
| «Grown, not drawn» | Ja: heile forma fell ut av veksten | Delvis: attraktorpunkta må plasserast (dvs. teiknast) | Nei: grunnforma må teiknast først; berre mønsteret veks |
| Veggtjukkleik 0,8–1,2 mm | Trivielt: offset av vekstflata | Vanskeleg: røyr-tjukkleik ≠ veggtjukkleik; boolske operasjonar skjøre | Trivielt (men flata er teikna) |
| Blendfri (okklusjon) | Kontrollerbart: porøsitet per flate-region | Vanskeleg: lys lek mellom greiner; okklusjon vert emergent og ustyrbar | Kontrollerbart |
| Overheng < 50° | Handhevbart per vertex/face kvar iterasjon (hard clamp) | Handhevbart per grein, men grein-kryss gjev lokale tak > 50° | Avheng av grunnforma, ikkje algoritmen |
| Skugge teiknar lagstruktur | Ja: iterasjon = lag; anisotrop splitting gjev horisontale ryggar | Skuggen teiknar greiner, ikkje lag | Ja, men mønster ≠ lag |
| Snø/skavl-metaforen | Direkte: kvar iterasjon legg «materiale» der trykka tillèt det | Svakare | Svakare |
| Etablerte GH-oppsett | Mange (Anemone+K2, Long Nguyen MeshGrow) | Nokre | Nokre (mest som tekstur) |
| Kompleksitet for student | Middels | Middels–høg (skjelett→solid er den harde delen) | Låg–middels, men løyser feil problem |

**Val: differential growth på eit ope trekant-mesh** («differential mesh
growth»), med constrainta bakte inn som ei blanding av harde
projeksjonar og mjuke kostnadsfelt.

Grunngjeving i tre punkt:

1. **Outputen er printobjektet.** Vekstflata er sjølve skalet; offset
   ±0,45 mm gjev veggen. Materialbudsjett (<150 g) kan reknast levande
   kvar iterasjon som `area × wall_t × rho_PLA`, og veksten kan stoppast
   hardt når budsjettet er brukt. Ingen av dei andre prinsippa gjev så
   direkte kopling mellom algoritmesteg og gram.
2. **Constrainta er flate-constraint.** Overheng, veggtjukkleik,
   okklusjon og skuggeanisotropi er alle eigenskapar ved ei flate, ikkje
   ved eit greinnett eller eit teksturfelt. Differential growth let oss
   handheve dei *der dei bur*: per face-normal, per kant, per pore.
3. **Iterasjon = snøfall = printlag.** Metaforen i briefen («kvar
   iterasjon er eit snøfall; ferdig form er fonna») er bokstavleg i
   differential growth: kvar loop-runde legg til vertexar langs
   vekstfronten. Med anisotrop kantsplitting (sjå §4.4) vert
   foldene/ryggane horisontale, slik at både printlaga og skuggen
   teiknar den same stratigrafien. Det er 1.321 i briefen («beste
   projeksjon gjer flest trykk synlege») løyst i geometrien.

Space colonization vert forkasta primært fordi le-sida skal vere
*lystett* — eit greinnett har alltid lekkasje mellom greiner, og å tette
det krev ein sekundær hud som då må teiknast. Reaction-diffusion vert
forkasta fordi det berre genererer mønster på ei form nokon alt har
bestemt; det bryt «grown, not drawn» i kjernen.

Etablerte implementasjonar det er verdt å sjå på før du byggjer
(referansar med lenkjer i §11): Anders Hoff (inconvergent) sin
differential-mesh-essay for kjernemekanikken; Long Nguyen (ICD
Stuttgart) sin MeshGrow frå C#-workshopen for half-edge-datastruktur og
kollisjon; Anemone+Kangaroo2-tråden på grasshopper3d for det
loop-baserte GH-oppsettet; Cabbage (2025) for korleis moderne
implementasjonar unngår sjølvkollisjon.

---

## 2. Arkitektur: tre fasar

Heile pipelinen er deterministisk gitt eit `random_seed`, slik at kvart
søsken kan reproduserast eksakt.

```
PHASE A  GROW      differential growth av open mesh-mansjett frå krageringen,
                   med harde clamps (keep-out, overheng, boks) kvar iterasjon,
                   til massebudsjettet er brukt eller fronten stoppar.
PHASE B  PERFORATE porøsitetspass: skjer porer i den ferdig-vaksne flata,
                   styrt av felt (termikk, materiale, vind) og forbode i
                   blendingssona; validert med ray-casting + reparasjonsloop.
PHASE C  BUILD     offset til solid (vegg), boolsk union med kragemodul,
                   mesh-sjekkar, STL-eksport, slicer.
```

Porene vert skorne i eit eige pass (B) i staden for under veksten fordi
holtopologi midt i ein differential-growth-loop er den vanlegaste kjelda
til ikkje-manifold mesh og krasj — og fordi blendfri-valideringa
(ray-casting) uansett må køyre på den *ferdige* forma. Dette er eit
medvite implementerbarheits-val, ikkje juks: porefeltet vert akkumulert
*under* veksten (kvar face arvar feltverdiane frå iterasjonen han vart
fødd i), så perforeringa er framleis ein funksjon av veksthistoria.

### Koordinatsystem (viktig — les to gonger)

Alt vert bygd i **print-rom**: `z_print`-aksen peikar opp frå
printplata, krageringen ligg i planet `z_print = 0`. Lampa **heng
omvendt** av slik ho vert printa: i hengande tilstand er kragen øvst og
munninga nedst; på printplata er kragen nedst og forma flarar
oppover-utover. Konsekvensar:

- Alle print-constraint (overheng, bruer) vert evaluerte i print-rom,
  som er rommet modellen står i. Ingen flipping av logikk trengst.
- Blendings-geometrien (strålar frå pæra ned mot augehøgd i hengande
  rom) vert i print-rom til strålar **oppover**: elevasjon
  `glare_band = [3°, 40°]` *over* horisonten frå kjeldepunktet.
- Konveksjons-utlaupet («skorsteinen», øvst i hengande rom) ligg i
  print-rom i bandet like *over* krageringen: `z_print ∈ [5, 25] mm`.
- «Snøen fell» langs `+z_print` (vekstfronten flyttar seg opp frå
  plata), som i hengande rom er nedover — konsistent med metaforen.

### Fast pre-geometri (teikna, ikkje vaksen — og ærleg om det)

To ting er parametrisk modellerte, ikkje genererte, fordi dei er
grensesnitt mot standardkomponentar:

1. **Kragemodul** (E27): flat ring, hol Ø 40,5 mm (E27-skjermring
   nominell 40 mm + 0,5 mm toleranse), ytre Ø 68 mm, tjukkleik 2,4 mm,
   med ein 4 mm høg forsterkingskant der vekstmansjetten festar.
   Verktøyfri montering: skjermringen på lampeholderen klemmer kragen —
   standard E27-mekanikk, ingen eigne klips. Masse ≈ 12 g (reservert i
   budsjettet). GU10-variant: separat krage med friksjonsring tilpassa
   den aktuelle GU10-armaturen (mål armaturen først; GU10-hus er ikkje
   standardiserte i ytre diameter).
2. **Frøring** (seed mesh): ein kort mesh-sylinder som veksten startar
   frå, Ø 68 mm, høgd 8 mm, ~48 vertexar i to ringar. Nedste ring er
   forankra (pinned) til kragekanten.

Kjeldepunktet (LED-filamentsenter) ligg i print-rom i
`src = (0, 0, 55 mm)` — dvs. 55 mm «over» krageplanet, som hengande er
55 mm under ringen; typisk for E27-pære (mål di faktiske pære og juster
`z_src`).

---

## 3. PHASE A — vekstloopen, pseudokode

Skriven som éin GhPython-komponent inne i ein Anemone-loop, eller som
rein Python i Rhino 8 ScriptEditor. `V` = vertexliste, `E` = kantliste,
`F` = faceliste (bruk `Rhino.Geometry.Mesh` + naboskapstabellar, eller
Plankton for half-edge).

```
# ---------- initialisation ----------
mesh   <- seed_ring_mesh(R_seed, H_seed, n_seed)
pin    <- vertex indices of bottom ring          # anchored to collar
front  <- vertex indices of top (naked) ring     # growth front
birth[f] <- 0 for all faces                      # iteration face was born
field_cache[f] <- sample_fields(f)               # frozen field values at birth
rng    <- Random(random_seed)
iter   <- 0
mass   <- shell_mass(mesh, wall_t) + m_collar

# ---------- main loop ----------
while iter < n_iter_max and mass < m_stop and front not empty:

    # 1. per-vertex scalar fields (see §4)
    for v in V:
        g[v]  <- glare_weight(v, src, glare_band)        # 0..1
        w[v]  <- windward_weight(v, wind_azimuth, p_wind) # 0..1 (lo-side)
        t[v]  <- vent_weight(v, z_vent_band)              # 0..1
        fert[v] <- clamp( f_base
                          + k_wind_fert * w[v]
                          - k_glare_fert * g[v]
                          + k_front * front_falloff(v, front), 0, 1)

    # 2. forces (displacement accumulation, unit: mm)
    for v in V not in pin:
        D[v] <- 0
        D[v] += k_spring * sum over edges(v,u):
                    (|vu| - l_target) * unit(u - v)          # edge springs
        D[v] += k_col * sum over neighbours u within r_col,
                    non-adjacent:
                    (r_col - |vu|) * unit(v - u)             # collision/repulsion
        D[v] += k_lap * (laplacian_smooth(v) - v)            # fairing
        if v in front:
            D[v] += k_flow * fert[v] *
                    unit( 0.72 * z_hat + 0.70 * radial_out(v) )  # growth bias

    # 3. integrate with displacement clamp
    for v in V not in pin:
        if |D[v]| > max_disp: D[v] <- max_disp * unit(D[v])
        v_new <- v + D[v]

        # 4. HARD CLAMPS (order matters)
        v_new <- project_out_of_keepout(v_new, keepout_sdf)   # thermal
        v_new <- clamp_to_bounds(v_new, R_max, H_max, z_min=0)
        v_new <- overhang_guard(v, v_new, mesh, theta_clamp)  # see §5.2
        v <- v_new

    # 5. adaptivity  (this IS the growth)
    for e in E where len(e) > l_split:
        p_split <- fert_edge(e) * aniso_weight(e)             # see §4.4
        if rng.uniform() < p_split:
            split_edge(e)          # midpoint vertex; inherits front-membership
            birth[new faces] <- iter
            field_cache[new faces] <- current field values    # archive of layers
    for e in E where len(e) < l_collapse: collapse_edge(e)
    flip_edges_for_quality(mesh)   # valence/aspect, standard Delaunay-ish flips

    # 6. periodic repair (every n_repair iterations)
    if iter % n_repair == 0:
        overhang_repair(mesh, theta_max, z_hat)               # see §5.2
        remove_degenerate_faces(mesh)

    # 7. bookkeeping
    mass <- shell_mass(mesh, wall_t) + m_collar
    front <- naked boundary vertices with z > z_front_min
    iter += 1

# ---------- termination ----------
report(iter, mass, area, n_vertices, stop_reason)
```

Merknader:

- **Steg 5 er veksten.** Fjørene (steg 2) strekkjer kantar nær fronten
  og der `fert` er høg; splitting legg inn nye vertexar; overskotet av
  materiale buklar flata til folder («skavlar»). Det er standard
  differential-growth-mekanikk, jf. inconvergent og Long Nguyen.
- **`field_cache` er arkivet.** Kvar face frys feltverdiane frå
  fødselsiterasjonen sin. PHASE B les desse, ikkje notidsverdiar — slik
  vert porøsiteten ein funksjon av *historia*, og lagstrukturen
  («snøfall for snøfall») vert lesbar i den ferdige forma.
- **Kangaroo2-ruta (utan eigen kraftkode):** byt ut steg 2–3 med ein
  Zombie-solver inne i Anemone-loopen med goals `EdgeLengths
  (target=l_target)`, `SphereCollide (radius=r_col/2)`,
  `SolidPointCollide (keep-out-solid, outside)`, `Anchor (pin)`, og ein
  `Load`-goal på front-vertexane for vekstbiasen. Splitting, felt og
  overhengsvakta må framleis vere ein liten GhPython før/etter solveren.
  Sjå Anemone+K2-tråden i §11 for oppsettmønsteret.

---

## 4. Felta (kostnadssida)

Alle felt er skalare, `0..1`, evaluerte per vertex (face-verdi =
snitt av hjørna).

### 4.1 `glare_weight` (blendfri-trykket)

```
d      <- unit(v - src)
elev   <- asin(d.z)                        # print-rom: oppover = mot auga
g(v)   <- smoothstep inside elev ∈ [3°, 40°], falloff sigma_glare = 5°
```

Banda [3°, 40°] dekkjer siktlinjer frå pære (heng ~1,9 m) til ståande og
sitjande auge (1,2–1,6 m) på 1–5 m avstand. `g` senkar fertiliteten
(tettare, rolegare vekst i sona) i PHASE A og forbyr porer i PHASE B.

### 4.2 `windward_weight` (le/lo-asymmetrien)

```
w(v) <- max(0, cos(azimuth(v) - wind_azimuth)) ^ p_wind
```

`w ≈ 1` på lo-sida (mot «vinden»): høg fertilitet → djupare folder, og
høg porøsitet i PHASE B. `w ≈ 0` på le-sida: glatt, tett, lystett —
snøen har lagt seg der.

### 4.3 `vent_weight` (konveksjonstrykket)

```
t(v) <- 1 if z(v) ∈ [z_vent_lo, z_vent_hi] else falloff sigma_vent
```

Skorsteinsbandet like over kragen (hengande: like under taket av
skjermen). PHASE B skal levere `A_vent_min` open flate her. Saman med
den opne munninga gjev det gjennomtrekk forbi pæra.

### 4.4 `aniso_weight` (skuggetrykket)

```
aniso_weight(e) <- 1 + a_z * (1 - |unit(e) · z_hat|)
```

Horisontale kantar får inntil `1 + a_z` gonger høgare
splittingssjanse → foldene organiserer seg som horisontale ryggar →
ryggane følgjer printlaga → skuggen på veggen teiknar lagstrukturen.
Dette er den ordna anisotropien frå briefen, implementert som éi linje.

---

## 5. Handheving per constraint: hard clamp eller kostnad?

Prinsipp: **tryggleik og fysikk = hard clamp** (kan aldri brytast, uansett
kva felta vil); **kvalitetar og karakter = kostnadsfelt** (kan vektast —
det er der søskena bur).

| # | Constraint (brief) | Mekanisme | Fase | Detalj |
|---|---|---|---|---|
| 1 | Termikk: 40 mm klaring | **Hard**: SDF-projeksjon | A, kvar iter | §5.1 |
| 2 | Termikk: konveksjon | Mjuk (felt `t`) + **hard sjekk** `A_vent ≥ A_vent_min` | B | §6 |
| 3 | Overheng < 50° | **Hard**: guard + repair | A, kvar iter | §5.2 |
| 4 | Bru < 8 mm | **Hard**: `pore_dmax = 7 mm` | B | §6 |
| 5 | Masse < 150 g | **Hard**: stoppvilkår `m_stop` | A | §3 steg 7 |
| 6 | Vegg 0,8–1,2 mm | **Hard**: konstant offset `wall_t` | C | §8 |
| 7 | Blendfri | Mjukt felt `g` i A + **hard validering** (ray-cast + reparasjon) i B | A+B | §6 |
| 8 | Skugge/anisotropi | Rein kostnad (`a_z`) | A | §4.4 |
| 9 | Le/lo | Rein kostnad (`k_wind_fert`, `w_wind_pore`) | A+B | §4.2 |
| 10 | E27/GU10, verktøyfri | Utanfor algoritmen: parametrisk kragemodul | C | §2 |

### 5.1 Keep-out (termikk) som SDF

```
keepout_sdf(p) = min( |p - src| - r_keepout,                     # sphere r=40 at source
                      capsule_dist(p, axis z∈[0, z_src+25], r_bulb) )
project_out_of_keepout(p): if sdf < 0, move p along sdf-gradient to sdf = +0.5 mm
```

Sfæren gjev 40 mm klaring frå LED-punktet; kapselen held mansjetten
klar av pærekroppen. Ingen vertex kan nokon gong stå inne i sona — dette
er den eine regelen som aldri vert vekta.

### 5.2 Overheng: guard + repair

Definisjon (print-rom): `theta_over(f) = asin(max(0, -n̂(f) · z_hat))`,
der `n̂` er utovervend face-normal. Vertikal vegg → 0°, tak → 90°.
Budsjett frå briefen: 50°. Vi klemmer på 47° (guard) og reparerer på 50°
for å ha slicer-margin.

```
overhang_guard(v_old, v_new, mesh, theta_clamp=47°):
    if any face incident to v_new has theta_over > theta_clamp:
        binary-search s in {0.5, 0.25, 0.0}:
            v_try <- v_old + s * (v_new - v_old)
            accept first v_try that passes
    return accepted position

overhang_repair(mesh, theta_max=50°):        # every n_repair iterations
    for up to 5 rounds:
        bad <- faces with theta_over > theta_max
        if bad empty: break
        for f in bad:
            v_low <- lowest vertex of f
            v_low.z += 0.2 * l_target        # rotate face towards vertical
```

Guarden hindrar at ein iterasjon skaper overheng; repair-passet ryddar
dei få som oppstår via kantflipping. Sidan porene i PHASE B er ≤ 7 mm,
er alle «tak» over porer lovlege bruer (< 8 mm) — teardrop-forming av
porene er difor valfri, ikkje påkravd.

---

## 6. PHASE B — perforering + blendfri-validering, pseudokode

```
# pore candidate score per face (uses ARCHIVED field values)
for f in F:
    P[f] <- w_mat_pore
            + w_vent_pore * t_cache[f]
            + w_wind_pore * w_cache[f]
            - w_glare_pore * g_now[f]        # glare re-evaluated on final form
            - rim_guard(f)                    # 1 near collar ring & mouth rim, else 0

# deterministic Poisson-disk pore placement
centers <- poisson_disk_sample(faces weighted by max(0, P - P_thr),
                               min_dist = pore_dmax + web_min, rng)
for c in centers:
    d_pore <- lerp(pore_dmin, pore_dmax, P[c])       # 3..7 mm
    if g_now(c) > 0.10: skip                         # NO pores in glare band
    cut_pore(mesh, c, d_pore)                        # region-grow faces, delete,
                                                     # smooth rim (2 laplacian steps)

# hard validation loop
repeat:
    rays <- stratified directions from src, elev ∈ [3°,40°], az ∈ [0°,360°),
            n_rays = 2000
    misses <- rays with zero mesh intersections
    if misses empty and vent_area(mesh) >= A_vent_min: break
    if misses: close_nearest_pore(worst miss)        # deterministic repair
    if vent_area < A_vent_min: enlarge/add pore in vent band (respect pore_dmax)
```

Valideringa er **hard**: forma går ikkje vidare til PHASE C før alle
2000 strålar i blendingsbandet treffer minst eitt skal-lag, og
ventilarealet er levert. (Éin vegg på 0,9 mm kvit PLA diffuserer nok
til at «minst eitt kryss» er rett kriterium ved 800 lm/2700 K; verifiser
fysisk i veke 2 og stram til `occlusion_min = 2` i bandet [3°, 25°] om
målinga viser blending.)

---

## 7. Full parameterliste

Startverdiar = søsken S1. Alle lengder i mm, vinklar i grader, masse i
gram, areal i mm².

**Oppsett og grenser**

| Parameter | Start | Eining | Kommentar |
|---|---|---|---|
| `random_seed` | 42 | – | reproduserbarheit |
| `R_seed` / `H_seed` / `n_seed` | 34 / 8 / 48 | mm/mm/stk | frøring på kragekant |
| `z_src` | 55 | mm | LED-senter over krageplan; **mål pæra** |
| `r_keepout` | 40 | mm | sfære rundt `src` (brief-krav) |
| `r_bulb` | 31 | mm | kapselradius rundt pærekropp |
| `R_max` / `H_max` | 150 / 250 | mm | boks-clamp |
| `m_max` / `m_stop` / `m_collar` | 150 / 135 / 12 | g | stopp med margin |
| `rho_PLA` | 1.24e-3 | g/mm³ | |
| `wall_t` | 0.9 | mm | 2 perimeterar à 0,45 (0,4-dyse) |

**Vekstkjerne (PHASE A)**

| Parameter | Start | Eining | Kommentar |
|---|---|---|---|
| `l_target` | 3.5 | mm | målkantlengd |
| `l_split` | 5.25 | mm | 1,5 × `l_target` |
| `l_collapse` | 1.4 | mm | 0,4 × `l_target` |
| `r_col` | 7.0 | mm | kollisjonsradius = 2 × `l_target` |
| `k_spring` / `k_col` / `k_lap` / `k_flow` | 1.0 / 1.5 / 0.30 / 0.45 | – | kraftvekter |
| `max_disp` | 0.7 | mm/iter | stabilitetsclamp |
| `f_base` | 0.30 | – | grunnfertilitet |
| `k_front` | 0.50 | – | ekstra fertilitet nær fronten |
| `n_iter_max` | 500 | – | |
| `n_repair` | 10 | – | repair-frekvens |
| `theta_clamp` / `theta_max` | 47 / 50 | ° | overheng guard/repair |

**Felt og vekting**

| Parameter | Start | Eining | Kommentar |
|---|---|---|---|
| `glare_band` | [3, 40] | ° elev | print-rom, over horisont frå `src` |
| `sigma_glare` | 5 | ° | mjuk kant på bandet |
| `k_glare_fert` | 0.6 | – | glare senkar fertilitet |
| `wind_azimuth` | 200 | ° | retning «vinden» kjem frå |
| `p_wind` | 2.0 | – | skarpleik le/lo |
| `k_wind_fert` | 0.5 | – | lo-side veks meir |
| `a_z` | 0.6 | – | anisotropi (skugge) |
| `z_vent_lo` / `z_vent_hi` | 5 / 25 | mm | skorsteinsband |
| `A_vent_min` | 2500 | mm² | hard sjekk i PHASE B |

**Perforering (PHASE B)**

| Parameter | Start | Eining | Kommentar |
|---|---|---|---|
| `P_thr` | 0.55 | – | porekandidat-terskel |
| `pore_dmin` / `pore_dmax` | 3 / 7 | mm | 7 < 8 mm brubudsjett |
| `web_min` | 3 | mm | minste steg mellom porer |
| `w_mat_pore` / `w_vent_pore` / `w_wind_pore` / `w_glare_pore` | 0.30 / 0.35 / 0.35 / 1.0 | – | |
| `n_rays` | 2000 | – | blendfri-validering |
| `occlusion_min` | 1 | kryss | skjerp til 2 om måling krev |

---

## 8. PHASE C — eksportpipeline til printbar STL

1. **Meshvask** (Rhino/GH): `Weld` (vinkel 30°), `UnifyMeshNormals`,
   slett degenererte faces. Valfritt: éin runde Weaverbird
   `wbLaplacianSmoothing` (styrke 0,2) — ikkje meir, elles vaskar du
   vekk lagryggane skuggen treng.
2. **Tjukning til solid**: offset ±`wall_t/2` frå vekstflata (flata =
   midtflate), slik at veggen ligg symmetrisk om det algoritmen har
   validert. Verktøy: Rhino 8 `OffsetMesh` (Solid=On, BothSides=On)
   eller Weaverbird `wbMeshThicken`. Porerimane vert automatisk lukka av
   solid-offseten.
3. **Kragemodul**: boolsk union (`MeshBooleanUnion`) mellom skal og
   parametrisk krage (§2). Om booleanen strevar: modeller kragen med
   8 mm overlapp inn i frøringa og bruk Dendro (voxel-union, voxelstorleik
   0,3 mm) — robust, og avrundinga på 0,3 mm er ønskt ved rota.
4. **Sjekkar før eksport** (alle skal passere):
   - `_Check`: closed mesh, manifold, 0 naked edges, 0 non-manifold edges
   - `MeshSelfIntersect`: ingen treff
   - Normalar peikar ut; volum > 0
   - Estimert masse `volume × rho_PLA` < 150 g
   - Min. veggtjukkleik ≥ 0,8 mm (stikkprøve med `_Distance` på 5 tverrsnitt)
5. **Eksport**: binær STL, einingar mm, toleranse arva frå mesh (ikkje
   re-mesh ved eksport).
6. **Slicer** (PrusaSlicer eller Cura, 0,4-dyse), sjekkliste:
   - [ ] Orientering: krage **ned** på plata (= print-rommet i modellen)
   - [ ] Lag 0,2 mm; perimeterar 2 à 0,45 mm (= `wall_t` 0,9 — slicer
         skal fylle veggen med nøyaktig 2 strengar, null gap fill)
   - [ ] Arachne/«detect thin walls» PÅ
   - [ ] Infill 0 %; topp/botn-lag 0 (alt er vegg)
   - [ ] **Support AV** — om sliceren markerer support-behov har
         algoritmen feila; gå tilbake, ikkje slå på support
   - [ ] Overhengs-preview: ingen raude felt > 50°
   - [ ] Bruer: preview-sjekk at alle bruer < 8 mm (porene garanterer det)
   - [ ] Søm (seam): aligned, plassert på le-sida (`wind_azimuth + 180°`)
   - [ ] Kjøling 100 % frå lag 4; fart ≤ 40 mm/s på perimeter (tynn vegg)
   - [ ] Brim 5 mm (liten kontaktflate ved kragen)
   - [ ] Slicer-estimert filamentmasse < 150 g (siste kontroll)
   - [ ] Timelapse-kamera PÅ (dokumentasjonskravet: lag-for-lag = snøfall)

---

## 9. Dei tre søskena (5.31: same grammatikk, ulik trykkvekting)

Same kode, same `random_seed`-disiplin (ulikt seed per søsken er lov —
det er vêret, ikkje grammatikken). Berre vektene under skil dei; alt
anna er identisk med §7.

| Parameter | **S1 «Fonn»** (vind/skugge) | **S2 «Trabekel»** (materialminimum) | **S3 «Kjerne»** (lys/blending) |
|---|---|---|---|
| `random_seed` | 42 | 137 | 271 |
| `k_wind_fert` | **0.9** | 0.3 | 0.2 |
| `p_wind` | **3.0** | 1.5 | 1.5 |
| `a_z` (anisotropi) | 0.7 | 0.4 | **0.9** |
| `k_glare_fert` | 0.6 | 0.6 | **1.0** |
| `m_stop` | 135 | **105** | 142 |
| `l_target` | 3.5 | **2.8** (finare vev) | 3.5 |
| `P_thr` | 0.55 | **0.40** (meir ope) | **0.70** (mindre ope) |
| `w_mat_pore` | 0.30 | **0.60** | 0.15 |
| `w_wind_pore` | **0.55** | 0.35 | 0.20 |
| `pore_dmax` | 7 | 7 | **5** |
| `glare_band` | [3, 40] | [3, 40] | **[0, 45]** + `occlusion_min=2` i [3, 25] |
| Karakter | dramatisk le/lo-skavl; skuggen som hovudmotiv | trabekel-vev, lettast mogleg, mest porøs | tettast, rolegast, strengast mot blending; lagskugge via `a_z` |

Forventa lesing (2.142/3.3-testen): tre objekt som openbert er i slekt —
same kornstorleik, same lag-logikk, same rot — men der ein kan *peike*
på kva trykk som har vunne i kvart av dei. Om familien ser ut som ein
«stil», er det stilarten-som-sverm demonstrert.

---

## 10. Validering (koplar til veke 2–3 i briefen)

- **Blending**: tend lampe, 2700 K/800 lm, mørkt rom; sjå mot pæra frå
  1,2 m og 1,6 m augehøgd på 1–5 m. Ingen direkte filament-sikt.
  Luxmeter i augehøgd som støtte. Feiler S1/S2 → køyr PHASE B om att
  med `occlusion_min = 2`.
- **Termikk**: termoelement (eller IR) på innsida av skalet nærast
  kjelda, 60 min drift, 10 W-ekvivalent LED. Krav: < 50 °C stabilt
  (10° margin til PLA-mjukning). Feiler → auk `r_keepout` til 45 og
  `A_vent_min` til 3200.
- **Masse**: vekt < 150 g inkl. krage.
- **Skugge**: lampe 0,6 m frå kvit vegg; foto 16:9. Lagryggane skal vere
  lesbare i skuggen. Svak teikning → auk `a_z` med 0,15.

---

## 11. Referansar (implementasjon)

- Anders Hoff (inconvergent): [On Generative Algorithms — Differential
  Mesh](https://inconvergent.net/generative/differential-mesh/) —
  kjernemekanikken (split/kollisjon/fairing) forklart kort og presist.
- Long Nguyen / ICD Stuttgart: [C# Scripting and Plugin Development for
  Grasshopper](https://www.icd.uni-stuttgart.de/teaching/workshops/workshop-live-streaming-c-scripting-and-plugin-development-for-grasshopper/)
  og [videoopptak 2018](https://discourse.mcneel.com/t/video-recordings-2018-c-scripting-and-plugin-development-for-grasshopper/62175)
  — MeshGrow-casestudien: half-edge, kantsplitting, kollisjon. Beste
  strukturelle førebilete for PHASE A sjølv om du skriv Python.
- [Differential Curve Growth with Anemone &
  Kangaroo2](https://www.grasshopper3d.com/forum/topics/differential-curve-growth-with-anemone-kangaroo2)
  (grasshopper3d-forum) — loop-oppsettet Anemone + K2 Zombie-solver.
- [Use Anemone To Create A Differential Growth Algorithm
  (YouTube)](https://www.youtube.com/watch?v=qviTRO7mqDo) og
  [Parametric House: Differential
  Growth](https://parametrichouse.com/differential-growth/) —
  innføringsnivå, godt for å få loopen til å snurre første gong.
- [Cabbage: A Differential Growth Framework for Open Surfaces
  (arXiv 2025)](https://arxiv.org/html/2504.18040v1) — open Python-kode;
  sjå korleis dei hindrar sjølvkollisjon på opne flater.
- Emilie Yu m.fl.: [Interactive Differential Growth for
  Design](https://em-yu.github.io/media/papers/interactive-diff-growth.pdf)
  — felt-styrt vekst (samsvarar med §4-arkitekturen her).
