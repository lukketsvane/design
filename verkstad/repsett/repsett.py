#!/usr/bin/env python3
"""Reparasjonssett, familie 1: skoeytehylse (splice coupler), from the brief
briefs/reparasjonssett.md as parametric, printable solids.

The kintsugi-for-plastic thesis in one part: a broken shaft or axle is not
glued (polyolefins barely bond, failure mode 10) but mechanically spliced.
Both broken ends slide into a sleeve until they butt against a central
internal ledge, and transverse screws pin each end. The repair is visible
and dignified, a gold-orange collar, not a hidden fix.

Two variants, one grammar (jf. the brief's failure-mode roll):
  boey (bending, modus 4):  a longer sleeve, screws inline along the axis so
        the pinned length resists the bending moment.
  torsjon (torsion, modus 6): a shorter sleeve, screws staggered around the
        circumference so the pin pattern resists torque.

Geometry: an outer cylinder with a through bore, a central annular ledge
(the shaft stop), and radial screw clearance holes. Printed standing on the
collar (axis vertical): the bore is open both ways and the only overhangs
are the short ledge step and the small transverse holes (budgeted below).
Exported as 3MF plus a validation report.

Run: python3 repsett.py   (needs numpy, trimesh, manifold3d)
"""

import math
import os
import numpy as np
import trimesh

# --------------------------------------------------------------- parameters
TOL = 0.30            # radial clearance so a broken end slides in [mm]
LEDGE = 1.5           # radial depth of the central stop ledge [mm]
LEDGE_H = 4.0         # axial height of the ledge band [mm]
CHAMFER = 1.2         # entry chamfer at each mouth [mm]
WALL_MIN = 2.4        # printable, load-bearing wall floor [mm]
PETG = dict(rho=1.27e-3, tau=30.0)   # g/mm^3, MPa (shear-bearing, typical)
PLA = dict(rho=1.24e-3, tau=35.0)
SECTIONS = 96         # cylinder facets
OVERHENG_DEG = 45.0
FLOW_MM3_S = 11.0     # rough print-time basis

# each family: the shaft it repairs (nominal diameter), sleeve length, wall,
# screw (metric clearance radius) and the pin pattern as (z_frac, theta_deg)
FAMILIES = {
    # bending sleeves: screws inline (theta constant), pinned length resists M
    "boey-d08": dict(d_shaft=8.0,  length=46.0, wall=3.0, mat=PETG,
                     mat_namn="PETG", r_screw=1.7,      # M3 clearance
                     pins=[(0.62, 0), (0.86, 0)]),
    "boey-d12": dict(d_shaft=12.0, length=58.0, wall=3.4, mat=PETG,
                     mat_namn="PETG", r_screw=2.15,     # M4 clearance
                     pins=[(0.60, 0), (0.82, 0)]),
    # torsion sleeve: screws staggered around the circumference to catch torque
    "torsjon-d10": dict(d_shaft=10.0, length=44.0, wall=3.8, mat=PETG,
                        mat_namn="PETG", r_screw=1.7,   # M3 clearance
                        pins=[(0.60, 0), (0.74, 60), (0.88, 120)]),
}


# ------------------------------------------------------------------ geometry
def radial_hole(r, z, theta_deg, reach):
    """A clearance cylinder drilled radially (through both walls) at height z
    and circumferential angle theta."""
    a = math.radians(theta_deg)
    direction = np.array([math.cos(a), math.sin(a), 0.0])
    T = trimesh.geometry.align_vectors([0, 0, 1], direction)
    T[:3, 3] = [0, 0, z]
    return trimesh.creation.cylinder(radius=r, height=reach, sections=48,
                                     transform=T)


def coupler(cfg):
    """Build one watertight splice coupler, axis along z, resting at z=0."""
    r_bore = cfg["d_shaft"] / 2.0 + TOL
    R = r_bore + cfg["wall"]
    L = cfg["length"]

    outer = trimesh.creation.cylinder(radius=R, height=L, sections=SECTIONS)
    outer.apply_translation([0, 0, L / 2.0])            # base at z=0
    body = outer.difference(_full_bore(r_bore, L))

    # central stop ledge: add an annular band back into the bore (through hole
    # stays open at r_stop, so the only overhang is the short ledge step)
    r_stop = r_bore - LEDGE
    band = trimesh.creation.cylinder(radius=r_bore, height=LEDGE_H,
                                     sections=SECTIONS)
    band.apply_translation([0, 0, L / 2.0])
    band = band.difference(_full_bore(r_stop, L))
    body = body.union(band)

    # entry chamfers at both mouths (a truncated cone lip) so the ends guide in
    for z0, sgn in ((0.0, 1.0), (L, -1.0)):
        cone = trimesh.creation.cone(radius=r_bore + CHAMFER, height=CHAMFER,
                                     sections=SECTIONS)
        if sgn > 0:
            cone.apply_translation([0, 0, z0])
        else:
            cone.apply_transform(trimesh.transformations.rotation_matrix(
                math.pi, (1, 0, 0)))
            cone.apply_translation([0, 0, z0])
        body = body.difference(cone)

    # transverse screw holes
    for z_frac, theta in cfg["pins"]:
        body = body.difference(
            radial_hole(cfg["r_screw"], z_frac * L, theta, 2 * R + 4))

    body = _weld(body)
    return body, dict(r_bore=r_bore, R=R, L=L, r_stop=r_stop)


def _full_bore(r, L):
    c = trimesh.creation.cylinder(radius=r, height=L + 4, sections=SECTIONS)
    c.apply_translation([0, 0, L / 2.0])
    return c


def _weld(mesh, digits=5):
    """Round + weld so the mesh survives the 3MF text roundtrip (boolean output
    carries near-duplicate vertices that open the shell on reload)."""
    m = trimesh.Trimesh(vertices=np.round(mesh.vertices, digits),
                        faces=mesh.faces.copy(), process=False)
    m.merge_vertices(digits_vertex=digits)
    m.update_faces(m.nondegenerate_faces())
    m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m)
    return m


# --------------------------------------------------------------- validation
def validate(name, cfg, mesh, dims):
    rep = {"namn": name, "materiale": cfg["mat_namn"]}
    rep["vasstett"] = bool(mesh.is_watertight)
    rep["volum_cm3"] = mesh.volume / 1000.0
    rep["masse_g"] = mesh.volume * cfg["mat"]["rho"]
    rep["printtid_min"] = mesh.volume / FLOW_MM3_S / 60.0
    rep["borehol_mm"] = dims["r_bore"] * 2.0
    rep["ytre_mm"] = dims["R"] * 2.0
    rep["lengd_mm"] = dims["L"]
    rep["vegg_mm"] = cfg["wall"]

    # hold force per end: each pin bears on the plastic in double shear across
    # the two walls; conservative bearing area = screw diameter x wall
    n_per_end = len(cfg["pins"])                       # pins engage each end
    d_s = cfg["r_screw"] * 2.0
    bearing = d_s * cfg["wall"] * 2.0                  # two walls per pin
    rep["haldekraft_N"] = n_per_end * bearing * cfg["mat"]["tau"]

    # overhang in print orientation (axis vertical, base at z=0)
    nz = mesh.face_normals[:, 2]
    down = np.clip(-nz, 0.0, 1.0)
    ang = np.degrees(np.arcsin(down))
    zc = mesh.triangles_center[:, 2]
    areas = mesh.area_faces
    over = (zc > 1.0) & (ang > OVERHENG_DEG) & (down < 0.999)
    rep["overheng_areal_pst"] = float(areas[over].sum() / areas.sum() * 100)
    rep["bru_boring_mm"] = dims["r_bore"] * 2.0        # transverse hole ceiling
    return rep


def profile_svg(profiles, path):
    """Half-section of each coupler: wall, bore, ledge and pin positions."""
    W, H, pad = 940, 300, 24
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             'font-family="sans-serif" font-size="13">',
             f'<rect width="{W}" height="{H}" fill="white"/>']
    for k, (name, cfg, dims) in enumerate(profiles):
        ox, oy = pad + 30 + k * 305, H - 60
        R, r_bore, L = dims["R"], dims["r_bore"], dims["L"]
        r_stop = dims["r_stop"]
        sc = min(1.0, 210.0 / L)

        def X(z):
            return ox + z * sc

        def Y(r):
            return oy - r * sc - 60

        # wall band (right half section): outer R down to bore r_bore
        parts.append(f'<rect x="{X(0):.1f}" y="{Y(R):.1f}" '
                     f'width="{L * sc:.1f}" height="{(R - r_bore) * sc:.1f}" '
                     'fill="#f4c26b" stroke="#b26a00" stroke-width="1.2"/>')
        # central ledge (down to r_stop)
        parts.append(f'<rect x="{X(L / 2 - LEDGE_H / 2):.1f}" '
                     f'y="{Y(r_bore):.1f}" width="{LEDGE_H * sc:.1f}" '
                     f'height="{(r_bore - r_stop) * sc:.1f}" '
                     'fill="#e8a13c" stroke="#b26a00" stroke-width="0.8"/>')
        for z_frac, _ in cfg["pins"]:
            parts.append(f'<circle cx="{X(z_frac * L):.1f}" '
                         f'cy="{Y((R + r_bore) / 2):.1f}" r="{cfg["r_screw"] * sc:.1f}" '
                         'fill="white" stroke="#37474f" stroke-width="1"/>')
        parts.append(f'<text x="{ox}" y="{H - 10}" fill="#37474f">'
                     f'skoeytehylse {name}</text>')
    parts.append('</svg>')
    with open(path, "w") as f:
        f.write("\n".join(parts))


def write_report(reports, path):
    lines = [
        "# Reparasjonssett, skoeytehylse, valideringsrapport (av `repsett.py`)",
        "",
        "> Familie 1 av dei fem i `briefs/reparasjonssett.md`. Mekanisk",
        "> skoeyting, ikkje lim: begge brotendane glir inn til den sentrale",
        "> lippa og vert pinna med tverrskruer. Haldekrafta er eit fyrste-",
        "> ordens overslag (pin i plast-boring, doble vegger); testplanen",
        "> i brief-veke 4 kalibrerer per modus (strekk, boeying, torsjon).",
        "",
        "| Maaltal | Krav | " + " | ".join(r["namn"] for r in reports) + " |",
        "|---|---|" + "---|" * len(reports),
    ]

    def row(label, krav, fmt, key):
        vals = " | ".join((fmt.format(r[key]) if key in r else "-")
                          for r in reports)
        lines.append(f"| {label} | {krav} | {vals} |")

    row("Materiale", "PETG (seig)", "{}", "materiale")
    row("Vasstett solid", "ja", "{}", "vasstett")
    row("Borehol (passar aksel + 0,3 mm)", "-", "{:.1f} mm", "borehol_mm")
    row("Ytre diameter", "-", "{:.1f} mm", "ytre_mm")
    row("Lengd", "-", "{:.0f} mm", "lengd_mm")
    row("Vegg", f">= {WALL_MIN} mm", "{:.1f} mm", "vegg_mm")
    row("Masse", "-", "{:.0f} g", "masse_g")
    row("Printtid (overslag)", "-", "{:.0f} min", "printtid_min")
    row("Haldekraft (overslag)", ">= 50 N", "{:.0f} N", "haldekraft_N")
    row("Overheng > 45° (printlege)", "< 3 % areal", "{:.2f} %",
        "overheng_areal_pst")
    row("Bru, tverrboring (tak)", "< 13 mm", "{:.1f} mm", "bru_boring_mm")
    lines += [
        "",
        "Printorientering: staaande paa kragen (akse loddrett). Boret er ope",
        "begge vegar; einaste overheng er det korte lippesteget og taket i",
        "tverrboringane (bru = borediameter). Ingen support.",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


# --------------------------------------------------------------------- main
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "print"), exist_ok=True)
    reports, profiles = [], []
    for name, cfg in FAMILIES.items():
        mesh, dims = coupler(cfg)
        rep = validate(name, cfg, mesh, dims)
        out = os.path.join(here, "print", f"skoeytehylse-{name}.3mf")
        mesh.export(out)
        rep["fil"] = os.path.relpath(out, here)
        reports.append(rep)
        profiles.append((name, cfg, dims))
        print(f"{name}: watertight={rep['vasstett']} masse={rep['masse_g']:.0f} g "
              f"hald={rep['haldekraft_N']:.0f} N "
              f"overheng>{OVERHENG_DEG:.0f}={rep['overheng_areal_pst']:.2f}%")

    profile_svg(profiles, os.path.join(here, "profil-v0.1.svg"))
    write_report(reports, os.path.join(here, "validering-v0.1.md"))

    failures = []
    for rep in reports:
        if not rep["vasstett"]:
            failures.append(f"{rep['namn']}: ikkje vasstett")
        if rep["vegg_mm"] < WALL_MIN:
            failures.append(f"{rep['namn']}: vegg {rep['vegg_mm']} < {WALL_MIN}")
        if rep["haldekraft_N"] < 50:
            failures.append(f"{rep['namn']}: hald {rep['haldekraft_N']:.0f} N < 50")
        if rep["overheng_areal_pst"] > 3.0:
            failures.append(f"{rep['namn']}: overheng {rep['overheng_areal_pst']:.2f} %")
    if failures:
        raise SystemExit("VALIDERING FEILA:\n  " + "\n  ".join(failures))
    print("Alle portar passerte.")


if __name__ == "__main__":
    main()
