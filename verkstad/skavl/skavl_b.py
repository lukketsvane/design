#!/usr/bin/env python3
"""Skavl generator B v0.1, the rotation grammar as radial lamellae.

Retningsendring frå Iver (2026-07-06): referansebileta i
`reference/formretning-2026-07/` (analyse:
`research/2026-07-06-formretning-rotasjonsgrammatikk.md`). Kjernegrepet er
éin profil, rotasjonsarray, vertikal stabling. Der generator A
(`skavl.py`) veks eit kontinuerleg skal som eit radiusfelt r(theta, z),
byggjer generator B lampa av N radiale lameller: éin dropeprofil kopiert
kring aksen. Same designbrief, same valideringsport, ny geometri.

Topologi (v0.1): ei tromme, ikkje ein kuppel. Tre av dei fire
referansebileta (01, 02, 04) er ringar/tromler av dropeforma finnar, ikkje
lukka kuplar; det er den lette, print-vennlege forma. Kvar lamell er ein
ståande, linse-/dropeforma blad-finne (spiss i topp og botn, feit på
buken) i planet (radius u, hogd z), ekstrudert tangentielt med tjukkleik
t_lamell, vridd valfritt phi_skru grader (rotor-effekten frå referanse
04), og plassert i vinkel theta_k. Ein slank botnring og toppring bind
finnane saman. Fordi finnane står vertikalt og buken svulmar mildt, held
overhenget seg under budsjettet utan støtte.

Ærleg funn-modus: blendinga vert MÅLT (strålecasting frå LED-senteret
over blendbandet), ikkje garantert ved konstruksjon slik generator A gjer
det. Rapporten fortel kor stor del av blendbandet lamellane faktisk
stengjer, og flagg-ar resten. Det er ein eigenskap ved radiale finnar
kring ei punktkjelde, og eit reelt seleksjonstrykk aksen må svare på.

Run:  python3 skavl_b.py    (skriv print/skavl-b-*.3mf, validering-b-v0.1.md,
                             silhuett-b-v0.1.svg)
"""

import math
import os
import numpy as np
import trimesh
from shapely.geometry import Polygon

# ---------------------------------------------------------------- parameters
# Namn følgjer lamell-modus-tabellen i briefs/skavl-algoritme.md.
H = 196.0             # total hogd [mm]
NZ = 140              # profil-sample langs z
R_SOKKEL = 22.3       # E27-krage inkl. +0,3 mm toleranse [mm]
Z_LED = 98.0          # LED-senter [mm], midt i trumma
R_MID = 82.0          # nominell mantelradius (finnane sit kring denne) [mm]
R_MAKS = 108.0        # format [mm]
T_LAMELL = 1.6        # lamelltjukkleik [mm], 4 perimeter a 0,4 (naturleg union)
RING_H = 7.0          # høgd på topp-/botnring [mm]
RING_IN = 5.0         # kor djupt ringen grip innover forbi finnefoten [mm]
RING_OUT = 2.5        # kor langt ringen stikk utover finnefoten [mm]
OVERHENG_DEG = 50.0   # print-overhengbudsjett
PLA_DENSITY = 1.24e-3          # g/mm^3
PETG_DENSITY = 1.27e-3         # g/mm^3
GLARE_BAND_DEG = (-5.0, 60.0)  # LED-stråle-elevasjon som ikkje skal sleppe ut

SIBLINGS = {
    # tre vektingar, éin grammatikk (jf. generator A sine tre søsken).
    # "lamell-" prefiks for å ikkje kollidere med generator A sine filer
    # (skavl-a/b/c-*.3mf). belly = kor langt buken svulmar ut forbi R_MID;
    # depth = blad-djupn på buken.
    "lamell-roleg": dict(N=24, phi_skru=0.0,  belly=12.0, depth=7.5, power=0.7,  seed=11, amp=0.06),
    "lamell-open":  dict(N=18, phi_skru=0.0,  belly=18.0, depth=10.0, power=0.55, seed=23, amp=0.10),
    "lamell-rotor": dict(N=30, phi_skru=16.0, belly=9.0,  depth=6.5, power=0.8,  seed=37, amp=0.05),
}


def smoothstep(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


# ----------------------------------------------------------------- profile
def lamell_profile(cfg):
    """Closed lens/drop polygon in the (u=radius, z) plane for one fin.

    A standing blade, pointed near top and bottom and fat at the belly
    (references 01 and 03). A half-sine `bump` peaking mid-height drives
    both the outward swell of the belly and the blade depth, so the fin
    swells out and thickens together and tapers back to the ring radius at
    both ends. The mild swell keeps the upper outer face within the print
    overhang budget without support. Seeded amplitude varies the belly line
    per sibling without breaking the rhythm.
    """
    rng = np.random.default_rng(cfg["seed"])
    wobble = 1.0 + cfg["amp"] * rng.uniform(-1, 1)
    z = np.linspace(0.0, H, NZ)
    bump = np.sin(np.pi * np.clip(z / H, 0.0, 1.0)) ** cfg["power"]

    r_out = R_MID + cfg["belly"] * wobble * bump
    r_out = np.minimum(r_out, R_MAKS)
    depth = 4.0 + (cfg["depth"] - 4.0) * bump          # >=4 mm at the ring ends
    r_in = r_out - depth

    # up the outer edge, down the inner edge -> simple closed polygon
    pts = [(r_out[i], z[i]) for i in range(NZ)]
    pts += [(r_in[i], z[i]) for i in range(NZ - 1, -1, -1)]
    poly = Polygon(pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    return poly, z, r_out, r_in


# -------------------------------------------------------------------- mesh
def one_lamella(poly, phi_skru):
    """Extrude the profile polygon tangentially by T_LAMELL, centred on the
    x-z plane, with an optional twist phi_skru (deg) about the z-axis that
    grows with height (the rotor effect from reference 04)."""
    m = trimesh.creation.extrude_polygon(poly, height=T_LAMELL)
    # extrude_polygon extrudes the (x,y) polygon along +z; our polygon is in
    # (u,z) so remap: polygon-x -> world-x (radius), polygon-y -> world-z,
    # extrusion-z -> world-y (tangential), centred on y=0.
    v = m.vertices.copy()
    remap = np.column_stack([v[:, 0], v[:, 2] - T_LAMELL / 2.0, v[:, 1]])
    m.vertices = remap
    trimesh.repair.fix_normals(m)
    if phi_skru:
        # twist: rotate each vertex about z by an angle proportional to height
        ang = math.radians(phi_skru) * (m.vertices[:, 2] / H)
        c, s = np.cos(ang), np.sin(ang)
        x, y = m.vertices[:, 0].copy(), m.vertices[:, 1].copy()
        m.vertices[:, 0] = c * x - s * y
        m.vertices[:, 1] = s * x + c * y
    return m


def build(cfg):
    poly, z, r_out, r_in = lamell_profile(cfg)
    base = one_lamella(poly, cfg["phi_skru"])
    parts = []
    for k in range(cfg["N"]):
        th = k * 2.0 * math.pi / cfg["N"]
        m = base.copy()
        c, s = math.cos(th), math.sin(th)
        R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])
        m.vertices = m.vertices @ R.T
        parts.append(m)

    # slim rings that tie the fin ends. The top ring is a floating annulus, so
    # its underside is chamfered to 45 deg (a revolved cross-section) to stay
    # inside the print overhang budget. The bottom ring rests on the bed, so a
    # plain band is fine there.
    ra, rb = R_MID - RING_IN, R_MID + RING_OUT

    def ring_flat(z0):
        outer = trimesh.creation.cylinder(radius=rb, height=RING_H, sections=160)
        inner = trimesh.creation.cylinder(radius=ra, height=RING_H + 2.0, sections=160)
        outer.apply_translation((0, 0, z0 + RING_H / 2.0))
        inner.apply_translation((0, 0, z0 + RING_H / 2.0))
        return trimesh.boolean.difference([outer, inner])

    def ring_chamfered(z0):
        ch = (rb - ra) / 2.0
        mid = (ra + rb) / 2.0
        cs = [(ra, z0 + RING_H), (rb, z0 + RING_H), (rb, z0 + ch),
              (mid, z0), (ra, z0 + ch), (ra, z0 + RING_H)]
        m = trimesh.creation.revolve(np.array(cs, float), sections=160)
        trimesh.repair.fix_normals(m)
        return m

    parts.append(ring_flat(0.0))              # bottom ring, on the bed
    parts.append(ring_chamfered(H - RING_H))  # top ring, chamfered underside

    solid = trimesh.boolean.union(parts)
    if isinstance(solid, list):
        solid = trimesh.util.concatenate(solid)
    trimesh.repair.fix_normals(solid)
    return solid, (z, r_out, r_in)


# --------------------------------------------------------------- validation
def glare_fraction(mesh, n_az=180, n_el=40):
    """Fraction of rays from the LED centre, across the full azimuth and the
    glare elevation band, that hit the shade (blocked). Radial fins around a
    point source cannot block every ray; this MEASURES how much they do."""
    az = np.linspace(0, 2 * math.pi, n_az, endpoint=False)
    el = np.radians(np.linspace(GLARE_BAND_DEG[0], GLARE_BAND_DEG[1], n_el))
    dirs = []
    for e in el:
        ce = math.cos(e)
        for a in az:
            dirs.append((ce * math.cos(a), ce * math.sin(a), math.sin(e)))
    dirs = np.array(dirs)
    origins = np.tile([0.0, 0.0, Z_LED], (len(dirs), 1))
    hit = mesh.ray.intersects_any(ray_origins=origins, ray_directions=dirs)
    return float(hit.mean())


def validate(name, mesh, prof):
    rep = {"namn": name}
    rep["vasstett"] = bool(mesh.is_watertight)
    rep["volum_mm3"] = float(mesh.volume)
    rep["masse_g"] = float(mesh.volume) * PLA_DENSITY
    rep["masse_petg_g"] = float(mesh.volume) * PETG_DENSITY
    rep["trekantar"] = int(len(mesh.faces))
    rep["r_maks_mm"] = float(np.linalg.norm(mesh.vertices[:, :2], axis=1).max())
    rep["hogd_mm"] = float(mesh.vertices[:, 2].max())

    # overhang on printed surfaces; exclude the bottom-ring base annulus that
    # rests on the bed (centroid at z ~ 0), which is contact area, not overhang
    cz = mesh.triangles_center[:, 2]
    printed = cz > 1.0
    nz = mesh.face_normals[printed, 2]
    down = np.clip(-nz, 0.0, 1.0)
    ang = np.degrees(np.arcsin(down))
    areas = mesh.area_faces[printed]
    rep["overheng_maks"] = float(ang.max())
    rep["overheng_brot_areal_pst"] = float(
        areas[ang > OVERHENG_DEG].sum() / areas.sum() * 100.0)
    rep["glare_stengt_pst"] = glare_fraction(mesh) * 100.0
    return rep


# --------------------------------------------------------------------- svg
def silhouette_svg(profiles, path):
    W, Hh, pad = 940, 340, 30
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {Hh}" '
             f'font-family="sans-serif" font-size="13">',
             f'<rect width="{W}" height="{Hh}" fill="white"/>']
    for k, (name, (z, r_out, r_in)) in enumerate(profiles):
        ox = pad + 150 + k * 300
        oy = Hh - pad
        right = [f"{ox + r_out[i]:.1f},{oy - z[i]:.1f}" for i in range(len(z))]
        left = [f"{ox + r_in[i]:.1f},{oy - z[i]:.1f}" for i in reversed(range(len(z)))]
        parts.append('<polygon points="' + " ".join(right + left)
                     + '" fill="#e0f2f1" stroke="#00695c" stroke-width="1.3"/>')
        # mirror to hint the rotation array
        rightm = [f"{ox - r_out[i]:.1f},{oy - z[i]:.1f}" for i in range(len(z))]
        leftm = [f"{ox - r_in[i]:.1f},{oy - z[i]:.1f}" for i in reversed(range(len(z)))]
        parts.append('<polygon points="' + " ".join(rightm + leftm)
                     + '" fill="#eceff1" stroke="#90a4ae" stroke-width="0.8"/>')
        parts.append(f'<text x="{ox}" y="{Hh - 8}" text-anchor="middle" '
                     f'fill="#00695c">skavl {name}</text>')
    parts.append(f'<text x="{pad}" y="{pad - 10}" fill="#90a4ae">'
                 'éin lamell-profil (farga) kopiert kring aksen &#183; '
                 'grå = spegel</text></svg>')
    with open(path, "w") as f:
        f.write("\n".join(parts))


def write_report(reports, path):
    lines = [
        "# Skavl generator B v0.1, valideringsrapport (generert av `skavl_b.py`)",
        "",
        "> Rotasjonsgrammatikken (retningsendring frå Iver, referansebileta).",
        "> Same valideringsport som generator A, men blendinga er MÅLT ved",
        "> strålecasting, ikkje garantert ved konstruksjon (sjå funn nedst).",
        "",
        "| Måltal | Krav | " + " | ".join(r["namn"] for r in reports) + " |",
        "|---|---|" + "---|" * len(reports),
    ]

    def row(label, krav, fmt, key):
        vals = " | ".join(fmt.format(r[key]) for r in reports)
        lines.append(f"| {label} | {krav} | {vals} |")

    row("Lamellar", "-", "{}", "N")
    row("Frø", "loggført", "{}", "fro")
    row("Vasstett solid", "ja", "{}", "vasstett")
    row("Masse (PLA 1,24 g/cm³)", "< 150 g", "{:.0f} g", "masse_g")
    row("Masse (PETG 1,27 g/cm³)", "< 150 g", "{:.0f} g", "masse_petg_g")
    row("Overheng, maks", f"< {OVERHENG_DEG}°", "{:.1f}°", "overheng_maks")
    row("Areal over overhengbudsjett", "< 1 %", "{:.2f} %", "overheng_brot_areal_pst")
    row("Blendband stengt (målt)", "mål 100 %", "{:.0f} %", "glare_stengt_pst")
    row("Største radius", f"≤ {R_MAKS} mm", "{:.1f} mm", "r_maks_mm")
    row("Høgd", "-", "{:.0f} mm", "hogd_mm")
    row("Trekantar", "-", "{}", "trekantar")
    row("Fil", "-", "`{}`", "fil")
    lines += [
        "",
        "## Funn v0.1",
        "",
        "Radiale finnar kring ei punktkjelde stengjer ikkje heile blendbandet:",
        "ein stråle som går rett ut i gapet mellom to finnar slepp ut. Målinga",
        "over seier kor mykje kvart søsken faktisk stengjer. Dette er eit reelt",
        "seleksjonstrykk aksen må svare på i v0.2: anten (a) ein tynn indre",
        "diffusor-sylinder i blendbandet, (b) tettare/breiare lamellar med",
        "overlapp i projeksjon, eller (c) å godta at lampa er ein *retnings*-",
        "lampe (blendfri berre i visse azimut). Traktat 5.6: omhugen langs",
        "blendaksen er no synleg og målt, ikkje gøymd.",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "print"), exist_ok=True)
    reports, profiles = [], []
    for name, cfg in SIBLINGS.items():
        solid, prof = build(cfg)
        rep = validate(name, solid, prof)
        rep["N"] = cfg["N"]
        rep["fro"] = cfg["seed"]
        out = os.path.join(here, "print", f"skavl-{name}.3mf")
        solid.export(out)
        rep["fil"] = os.path.relpath(out, here)
        reports.append(rep)
        profiles.append((name, prof))
        print(f"{name}: watertight={rep['vasstett']} masse={rep['masse_g']:.0f} g "
              f"overheng_maks={rep['overheng_maks']:.1f}deg "
              f"glare_stengt={rep['glare_stengt_pst']:.0f}%")

    silhouette_svg(profiles, os.path.join(here, "silhuett-b-v0.1.svg"))
    write_report(reports, os.path.join(here, "validering-b-v0.1.md"))

    failures = []
    for rep in reports:
        if not rep["vasstett"]:
            failures.append(f"{rep['namn']}: ikkje vasstett")
        if rep["masse_g"] >= 150:
            failures.append(f"{rep['namn']}: masse {rep['masse_g']:.0f} g >= 150 g")
        if rep["overheng_brot_areal_pst"] > 1.0:
            failures.append(f"{rep['namn']}: {rep['overheng_brot_areal_pst']:.2f} % "
                            f"av skalet over {OVERHENG_DEG} deg")
    # glare is a measured finding in v0.1, not yet a hard gate (see report)
    if failures:
        raise SystemExit("VALIDERING FEILA:\n  " + "\n  ".join(failures))
    print("Harde portar (vasstett/masse/overheng) passerte. "
          "Blend er målt funn, sjå rapport.")


if __name__ == "__main__":
    main()
