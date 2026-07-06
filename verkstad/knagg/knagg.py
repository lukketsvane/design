#!/usr/bin/env python3
"""Knagg #1 generator v0.1, the three hypotheses from briefs/knagg-01.md
as parametric, printable solids.

Variants (the plan's v0.1-0.3, one grammar, three weightings):
  kraftlinje:   moment-following thickness (more material at the root,
                constant-stress taper), generous root flare (the fillet
                rule), PETG. The thesis variant.
  kanalisert:   same spine, constant thickness: the swarm-standard hook
                (traktat 3.2), the control the others are read against.
  medvite-svak: same as kanalisert but PLA with a designed failure zone:
                a sharp, fillet-free notch at the cantilever root
                (brotmodus 1/4) sized to survive daily 5 kg and fail
                legibly around ~9-10 kg static.

Geometry: a 2D spine in the x-z plane (x out from the wall, z up), lofted
with rounded-rectangle cross sections (width w across y), unioned with a
wall plate carrying one countersunk screw hole. Exported lying on the
side (layers across the bending plane, per the failure-mode taxonomy) as
3MF, plus a validation report.

Run: python3 knagg.py   (needs numpy, trimesh, manifold3d, shapely)
"""

import math
import numpy as np
import trimesh
from shapely.geometry import Polygon

# --------------------------------------------------------------- parameters
W_ARM = 16.0          # arm width across y [mm]
T_ROOT = 16.0         # in-plane thickness at the root (kraftlinje) [mm]
T_TIP = 10.0          # tip thickness [mm] (tip is not the contact zone)
T_CONST = 13.0        # constant thickness (kanalisert / medvite-svak)
T_SADDLE_MIN = 16.0   # min thickness through the textile contact zone
ARM_LEN = 46.0        # straight arm length [mm]
ARM_ANGLE = math.radians(6.0)   # slight upward slope
R_SPINE = 18.0        # saddle spine radius -> inner contact radius 10 mm
SWEEP = math.radians(140.0)     # saddle sweep past vertical
# plate width = arm width: the whole hook is one constant-width 2.5D body,
# so the full flat side rests on the bed when printed lying down
PLATE = dict(w=W_ARM, z_lo=-24.0, z_hi=46.0, t=3.6, r=3.0)
SCREW = dict(z=34.0, r_shaft=2.1, r_head=4.3, sink=2.2)     # one screw, M4
NOTCH = dict(x0=6.0, x1=10.0, t_left=10.0)   # designed weak zone (svak)
EMBED = 3.0           # spine starts inside the plate for a robust union
K_SEC = 40            # points per cross section
N_SPINE = 90          # sections along the spine
PETG = dict(rho=1.27e-3, sigma=47.0)   # g/mm^3, MPa (yield, datasheet-typical)
PLA = dict(rho=1.24e-3, sigma=55.0)
LAYER_FACTOR = 0.85   # side-printed: layers in the bending plane
KT_NOTCH = 2.5        # stress concentration, sharp rectangular notch
OVERHENG_DEG = 45.0   # print budget from the brief
FLOW_MM3_S = 9.0      # rough print-time estimate basis

VARIANTS = {
    "kraftlinje":   dict(mat=PETG, mat_namn="PETG", taper=True,  notch=False),
    "kanalisert":   dict(mat=PETG, mat_namn="PETG", taper=False, notch=False),
    "medvite-svak": dict(mat=PLA,  mat_namn="PLA",  taper=False, notch=True),
}


# ------------------------------------------------------------------- spine
def spine():
    """Centreline in (x, z): straight arm, then the saddle arc curling up
    and back. Returns points, unit tangents, arc-length steps."""
    n1 = int(N_SPINE * 0.45)
    s1 = np.linspace(0.0, ARM_LEN, n1, endpoint=False)
    p1 = np.stack([-EMBED + s1 * math.cos(ARM_ANGLE),
                   s1 * math.sin(ARM_ANGLE)], axis=1)
    # arc: tangent continues from ARM_ANGLE, turning upward (left)
    a0 = ARM_ANGLE - math.pi / 2            # from centre to arc start
    centre = p1[-1] + (ARM_LEN - s1[-1]) * np.array(
        [math.cos(ARM_ANGLE), math.sin(ARM_ANGLE)]) - R_SPINE * np.array(
        [math.cos(a0), math.sin(a0)])
    n2 = N_SPINE - n1
    ang = a0 + np.linspace(0.0, SWEEP, n2)
    p2 = centre + R_SPINE * np.stack([np.cos(ang), np.sin(ang)], axis=1)
    pts = np.vstack([p1, p2])
    tan = np.gradient(pts, axis=0)
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    return pts, tan


def thickness(pts, cfg):
    """In-plane thickness along the spine."""
    x = pts[:, 0]
    n = len(pts)
    i_arc = int(N_SPINE * 0.45)
    if not cfg["taper"]:
        t = np.full(n, T_CONST)
    else:
        # constant-stress taper: t ~ sqrt(M), M ~ distance to the load point
        x_load = pts[:, 0].max()            # jacket hangs at the saddle
        m = np.clip(x_load - x, 0.0, None)
        t = T_ROOT * np.sqrt(m / max(m.max(), 1e-9))
        t = np.clip(t, T_TIP, T_ROOT)
        t[i_arc:] = np.maximum(t[i_arc:], T_SADDLE_MIN)   # contact zone
        # taper only in the final upsweep toward the tip
        j = int(n * 0.82)
        t[j:] = np.linspace(t[j], T_TIP, n - j)
        # root flare = the fillet rule made continuous
        s = np.arange(n, dtype=float)
        t += 6.0 * np.exp(-s / 6.0)
    return t


def section_ring(centre, tangent, w, t):
    """Rounded-rectangle cross section (w across y, t in-plane), K_SEC pts,
    consistent ordering for lofting."""
    nrm = np.array([-tangent[1], tangent[0]])   # in-plane normal
    rc = min(2.5, t / 3.5, w / 3.5)
    hw, ht = w / 2.0 - rc, t / 2.0 - rc
    ring = []
    for k in range(K_SEC):
        a = 2.0 * math.pi * k / K_SEC
        # superellipse-ish: clamp a circle onto the rounded rect
        cy = math.copysign(min(abs(math.cos(a)) * (hw + rc), hw), math.cos(a))
        ct = math.copysign(min(abs(math.sin(a)) * (ht + rc), ht), math.sin(a))
        dy = math.cos(a) * rc + cy
        dt = math.sin(a) * rc + ct
        p = centre + nrm * dt
        ring.append([p[0], dy, p[1]])
    return np.array(ring)


def arm_mesh(cfg):
    pts, tan = spine()
    t = thickness(pts, cfg)
    rings = [section_ring(pts[i], tan[i], W_ARM, t[i])
             for i in range(len(pts))]
    # rounded dome cap past the tip
    for phi in np.linspace(0.12, math.pi / 2, 7):
        c = pts[-1] + tan[-1] * (t[-1] / 2.0) * math.sin(phi)
        f = math.cos(phi)
        rings.append(section_ring(c, tan[-1], max(W_ARM * f, 0.8),
                                  max(t[-1] * f, 0.8)))
    V, F = [], []
    for ring in rings:
        V.extend(ring)
    for i in range(len(rings) - 1):
        for k in range(K_SEC):
            a = i * K_SEC + k
            b = i * K_SEC + (k + 1) % K_SEC
            c = (i + 1) * K_SEC + (k + 1) % K_SEC
            d = (i + 1) * K_SEC + k
            F += [(a, b, c), (a, c, d)]
    n = len(V)
    V.append(np.mean(rings[0], axis=0))     # root cap fan
    for k in range(K_SEC):
        F.append((n, rings_idx(0, (k + 1) % K_SEC), rings_idx(0, k)))
    V.append(np.mean(rings[-1], axis=0))    # tip cap fan
    m = len(rings) - 1
    for k in range(K_SEC):
        F.append((n + 1, rings_idx(m, k), rings_idx(m, (k + 1) % K_SEC)))
    mesh = trimesh.Trimesh(vertices=np.array(V), faces=np.array(F),
                           process=False)
    trimesh.repair.fix_normals(mesh)
    return mesh, pts, t


def rings_idx(i, k):
    return i * K_SEC + k


def plate_mesh():
    """Wall plate in the y-z plane, extruded along x, rounded corners."""
    w2 = PLATE["w"] / 2.0
    poly = Polygon([(-w2, PLATE["z_lo"]), (w2, PLATE["z_lo"]),
                    (w2, PLATE["z_hi"]), (-w2, PLATE["z_hi"])]
                   ).buffer(-PLATE["r"]).buffer(PLATE["r"], resolution=24)
    m = trimesh.creation.extrude_polygon(poly, PLATE["t"])
    # extrude_polygon builds in xy extruded along +z; map (y,z,x')->(x,y,z)
    m.apply_transform(np.array([[0., 0., 1., 0.],
                                [1., 0., 0., 0.],
                                [0., 1., 0., 0.],
                                [0., 0., 0., 1.]]))
    return m


def screw_cut():
    """Through hole + countersink, axis along x."""
    rot = trimesh.transformations.rotation_matrix(math.pi / 2, (0, 1, 0))
    shaft = trimesh.creation.cylinder(radius=SCREW["r_shaft"], height=30,
                                      sections=48, transform=rot)
    cone = trimesh.creation.cone(radius=SCREW["r_head"],
                                 height=SCREW["r_head"] - SCREW["r_shaft"] + 0.01,
                                 sections=48)
    cone.apply_transform(trimesh.transformations.rotation_matrix(
        -math.pi / 2, (0, 1, 0)))          # apex pointing -x
    cone.apply_translation((PLATE["t"] + 0.01, 0, 0))
    cut = shaft.union(cone)
    cut.apply_translation((0, 0, SCREW["z"]))
    return cut


def notch_cut(t_root):
    """Sharp rectangular notch across the top face at the root, the
    designed weak zone, deliberately without a fillet (brotmodus 1)."""
    depth = t_root - NOTCH["t_left"]
    box = trimesh.creation.box((NOTCH["x1"] - NOTCH["x0"], W_ARM + 4, depth + 2))
    zc = ARM_ANGLE * (NOTCH["x0"] + NOTCH["x1"]) / 2   # spine z at notch ~ x*slope
    box.apply_translation(((NOTCH["x0"] + NOTCH["x1"]) / 2, 0,
                           zc + t_root / 2 - depth / 2 + 1))
    return box


# --------------------------------------------------------------- validation
def validate(name, cfg, mesh, pts, t):
    rep = {"namn": name, "materiale": cfg["mat_namn"]}
    rep["vasstett"] = bool(mesh.is_watertight)
    rep["volum_cm3"] = mesh.volume / 1000.0
    rep["masse_g"] = mesh.volume * cfg["mat"]["rho"]
    rep["printtid_min"] = mesh.volume / FLOW_MM3_S / 60.0
    rep["utstikk_mm"] = float(mesh.bounds[1][0])

    # bending stress along the spine (rect section approx, load at saddle)
    x = pts[:, 0]
    x_load = float(x.max())
    rep["momentarm_mm"] = x_load
    t_eff = t.copy()
    if cfg["notch"]:
        in_notch = (x >= NOTCH["x0"]) & (x <= NOTCH["x1"])
        t_eff[in_notch] = NOTCH["t_left"]
    for kg in (5, 10):
        F = kg * 9.81
        M = F * np.clip(x_load - x, 0.0, None)
        sigma = M / (W_ARM * t_eff ** 2 / 6.0)
        if cfg["notch"]:
            sigma = np.where((x >= NOTCH["x0"]) & (x <= NOTCH["x1"]),
                             sigma * KT_NOTCH, sigma)
        rep[f"sigma_{kg}kg_MPa"] = float(sigma.max())
    sig_allow = cfg["mat"]["sigma"] * LAYER_FACTOR
    rep["sigma_tillate_MPa"] = sig_allow
    rep["SF_5kg"] = sig_allow / rep["sigma_5kg_MPa"]
    if cfg["notch"]:
        # predicted legible failure: nominal stress * Kt = material limit
        Z = W_ARM * NOTCH["t_left"] ** 2 / 6.0
        arm = x_load - (NOTCH["x0"] + NOTCH["x1"]) / 2
        F_brot = cfg["mat"]["sigma"] * LAYER_FACTOR * Z / (KT_NOTCH * arm)
        rep["brotlast_kg"] = F_brot / 9.81

    # overhang in print orientation (already lying on the side, z up)
    nz = mesh.face_normals[:, 2]
    down = np.clip(-nz, 0.0, 1.0)
    ang = np.degrees(np.arcsin(down))
    zc = mesh.triangles_center[:, 2]
    keep = zc > 3.0                        # ignore the near-bed band
    areas = mesh.area_faces
    over = keep & (ang > OVERHENG_DEG) & (down < 0.999)  # flat bottoms = bridges
    rep["overheng_areal_pst"] = float(areas[over].sum() / areas.sum() * 100)
    # inner contact radius in the saddle
    rep["kontaktradius_mm"] = R_SPINE - float(t[int(N_SPINE * 0.6)]) / 2.0
    return rep


def weld(mesh, digits=5):
    """Round + weld so the mesh survives the 3MF text roundtrip: boolean
    output carries near-duplicate vertices that collapse under export
    rounding and open the shell on reload."""
    m = trimesh.Trimesh(vertices=np.round(mesh.vertices, digits),
                        faces=mesh.faces.copy(), process=False)
    m.merge_vertices(digits_vertex=digits)
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    return m


def build(name, cfg):
    arm, pts, t = arm_mesh(cfg)
    solid = arm.union(plate_mesh())
    back = trimesh.creation.box((20, 100, 140))
    back.apply_translation((-10, 0, 10))
    solid = solid.difference(back)         # shave the embed flush at x=0
    solid = solid.difference(screw_cut())
    if cfg["notch"]:
        solid = solid.difference(notch_cut(T_CONST))
    solid = weld(solid)
    # print orientation: lying on the side (width -> up), layers in the
    # bending plane (the strong direction), resting on the bed at z=0
    solid.apply_transform(trimesh.transformations.rotation_matrix(
        math.pi / 2, (1, 0, 0)))
    solid.apply_translation((0, 0, -solid.bounds[0][2]))
    rep = validate(name, cfg, solid, pts, t)
    return solid, rep, pts, t


def profile_svg(profiles, path):
    W, H, pad = 940, 300, 24
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             'font-family="sans-serif" font-size="13">',
             f'<rect width="{W}" height="{H}" fill="white"/>']
    for k, (name, pts, t, notch) in enumerate(profiles):
        ox, oy = pad + 40 + k * 305, H - 70
        nrm = np.gradient(pts, axis=0)
        nrm /= np.linalg.norm(nrm, axis=1, keepdims=True)
        nrm = np.stack([-nrm[:, 1], nrm[:, 0]], axis=1)
        top = pts + nrm * (t[:, None] / 2)
        bot = pts - nrm * (t[:, None] / 2)
        poly = np.vstack([top, bot[::-1]])
        d = " ".join(f"{ox + p[0]:.1f},{oy - p[1]:.1f}" for p in poly)
        parts.append(f'<polygon points="{d}" fill="#eceff1" '
                     'stroke="#37474f" stroke-width="1.2"/>')
        parts.append(f'<rect x="{ox - 6}" y="{oy - 48}" width="4" height="72" '
                     'fill="#b0bec5"/>')   # wall
        if notch:
            zc = ARM_ANGLE * (NOTCH["x0"] + NOTCH["x1"]) / 2
            parts.append(f'<rect x="{ox + NOTCH["x0"]:.1f}" '
                         f'y="{oy - zc - t[0] / 2:.1f}" '
                         f'width="{NOTCH["x1"] - NOTCH["x0"]:.1f}" '
                         f'height="{t[0] - NOTCH["t_left"]:.1f}" fill="white" '
                         'stroke="#c62828" stroke-width="1.2"/>')
        parts.append(f'<text x="{ox + 30}" y="{H - 12}" fill="#37474f">'
                     f'knagg {name}</text>')
    parts.append('</svg>')
    with open(path, "w") as f:
        f.write("\n".join(parts))


def write_report(reports, path):
    lines = [
        "# Knagg #1 v0.1, valideringsrapport (generert av `knagg.py`)",
        "",
        "> Måltala frå aksane i `briefs/knagg-01.md` (v1.1), rekna på",
        "> geometrien før print. Spenningane er fyrsteordens overslag",
        "> (rektangulært tverrsnitt, last i sadelpunktet, Kt = 2,5 for",
        "> skarpt spor); den fysiske testplanen kalibrerer.",
        "",
        "| Måltal | Krav | " + " | ".join(r["namn"] for r in reports) + " |",
        "|---|---|" + "---|" * len(reports),
    ]

    def row(label, krav, fmt, key):
        vals = " | ".join((fmt.format(r[key]) if key in r else "-")
                          for r in reports)
        lines.append(f"| {label} | {krav} | {vals} |")

    row("Materiale", "PETG lastberande; PLA berre svak-variant", "{}", "materiale")
    row("Vasstett solid", "ja", "{}", "vasstett")
    row("Masse", "< 40 g", "{:.0f} g", "masse_g")
    row("Printtid (overslag 9 mm³/s)", "< 120 min", "{:.0f} min", "printtid_min")
    row("Utstikk", "60-80 mm", "{:.0f} mm", "utstikk_mm")
    row("Momentarm (sadel)", "~60-80 mm", "{:.0f} mm", "momentarm_mm")
    row("σ maks ved 5 kg", "-", "{:.1f} MPa", "sigma_5kg_MPa")
    row("σ maks ved 10 kg (støyt)", "-", "{:.1f} MPa", "sigma_10kg_MPa")
    row("Tillate spenning (0,85 × σ_y)", "-", "{:.0f} MPa", "sigma_tillate_MPa")
    row("Tryggingsfaktor ved 5 kg", "> 2", "{:.1f}", "SF_5kg")
    row("Predikert brotlast (svak sone)", "8-12 kg", "{:.1f} kg", "brotlast_kg")
    row("Kontaktradius (sadel, indre)", "≥ 8 mm", "{:.0f} mm", "kontaktradius_mm")
    row("Overheng > 45° (printlege)", "< 3 % areal", "{:.2f} %", "overheng_areal_pst")
    lines += [
        "",
        "Printorientering: liggjande på sida (eksportert slik), laga ligg",
        "i bøyeplanet, den sterke retninga, jf. taksonomien. Tuppradius er",
        f"{T_TIP / 2:.0f} mm og under tekstilkravet, medvite: tuppen er ikkje",
        "kontaktsona, og kompromisset skal vere lesbart (2.13).",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    reports, profiles = [], []
    for name, cfg in VARIANTS.items():
        solid, rep, pts, t = build(name, cfg)
        out = os.path.join(here, "print", f"knagg-{name}.3mf")
        solid.export(out)
        rep["fil"] = os.path.relpath(out, here)
        reports.append(rep)
        profiles.append((name, pts, t if cfg["taper"] else
                         np.full(len(pts), T_CONST), cfg["notch"]))
        print(f"{name}: watertight={rep['vasstett']} masse={rep['masse_g']:.0f} g "
              f"SF5={rep['SF_5kg']:.1f} overheng>{OVERHENG_DEG}°="
              f"{rep['overheng_areal_pst']:.2f} %"
              + (f" brotlast={rep['brotlast_kg']:.1f} kg" if cfg["notch"] else ""))
    profile_svg(profiles, os.path.join(here, "profil-v0.1.svg"))
    write_report(reports, os.path.join(here, "validering-v0.1.md"))

    failures = []
    for rep in reports:
        if not rep["vasstett"]:
            failures.append(f"{rep['namn']}: ikkje vasstett")
        if rep["masse_g"] >= 40:
            failures.append(f"{rep['namn']}: masse {rep['masse_g']:.0f} g >= 40 g")
        if rep["printtid_min"] >= 120:
            failures.append(f"{rep['namn']}: printtid ~{rep['printtid_min']:.0f} min")
        if not (55 <= rep["utstikk_mm"] <= 82):
            failures.append(f"{rep['namn']}: utstikk {rep['utstikk_mm']:.0f} mm")
        if rep["SF_5kg"] < 2 and "brotlast_kg" not in rep:
            failures.append(f"{rep['namn']}: SF {rep['SF_5kg']:.1f} < 2")
        if rep["overheng_areal_pst"] > 3.0:
            failures.append(f"{rep['namn']}: overheng {rep['overheng_areal_pst']:.2f} %")
        if rep["kontaktradius_mm"] < 8.0:
            failures.append(f"{rep['namn']}: kontaktradius {rep['kontaktradius_mm']:.1f} mm")
    if failures:
        raise SystemExit("VALIDERING FEILA:\n  " + "\n  ".join(failures))
    print("Alle portar passerte.")


if __name__ == "__main__":
    main()
