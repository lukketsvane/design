#!/usr/bin/env python3
"""Radial-fin grammar (working name: Ribbe), toward Ivers celadon-porcelain
reference: N thin radial blades whose stacked leaf/vertebra silhouettes build
a porous ball/torus, with deep gaps between the fins. The gaps are the
porosity (and the radial shadow-drawing the Skavl brief asks for); the fin
silhouette is where the "form of forces" lives.

Construction: each fin is a 2D silhouette in the (radius s, height z) plane,
extruded to a thin wall (thickness t in the tangential direction) and arrayed
around the axis, optionally with a gentle twist. The envelope R(z) sets the
overall ball; an undulation adds the vertebra bumps on the outer edge.

For fast aesthetic iteration the fins are concatenated (not booleaned); the
z-buffer renderer handles overlapping solids. Watertight union + print
validation come once the form is locked.

Run: python3 radial.py            (writes print/ribbe-*.3mf)
"""

import math
import os
import numpy as np
import trimesh
from shapely.geometry import Polygon


# --------------------------------------------------------------- parameters
# Fewer, deeper plates with an asymmetric organic-leaf profile and a small
# open core, so the assembly reads as separate see-through blades (the
# reference) rather than a closed grooved onion.
VARIANTS = {
    "leaf": dict(n_fin=22, H=190.0, r_max=94.0, hub_r=8.0, t=3.6,
                 foot=0.45, taper=0.34, twist_deg=0.0, stagger=0.0,
                 lobes=0, neck=0.0, tip_out=0.0, hook=0.0, lobe_p=0.8, K=200),
    "vertebra": dict(n_fin=26, H=196.0, r_max=90.0, hub_r=9.0, t=5.0,
                     foot=0.42, taper=0.30, twist_deg=0.0, stagger=0.5,
                     lobes=8, neck=0.09, tip_out=9.0, hook=0.55, lobe_p=0.78,
                     K=280),
    "spiral": dict(n_fin=24, H=192.0, r_max=93.0, hub_r=8.0, t=5.0,
                   foot=0.44, taper=0.33, twist_deg=42.0, stagger=0.38,
                   lobes=8, neck=0.09, tip_out=9.0, hook=0.6, lobe_p=0.80,
                   K=280),
}


def envelope(z, cfg, phase=0.0):
    """Outer radius of one blade: an asymmetric leaf (fuller foot, beaked
    tip) with optional beaked vertebra scales on the edge. `phase` staggers
    the scales between neighbouring blades so they interleave (woven) rather
    than line up into saucer tiers."""
    zf = np.clip(z / cfg["H"], 1e-4, 1.0 - 1e-4)
    leaf = np.power(zf, cfg["foot"]) * np.power(1.0 - zf, cfg["taper"])
    peak = cfg["foot"] / (cfg["foot"] + cfg["taper"])
    norm = np.power(peak, cfg["foot"]) * np.power(1.0 - peak, cfg["taper"])
    r = cfg["r_max"] * leaf / norm
    if cfg["lobes"]:
        p = (cfg["lobes"] * zf + phase) % 1.0
        if cfg["hook"]:
            p = np.clip(p + cfg["hook"] * p * (1.0 - p), 0.0, 1.0)
        node = np.power(np.clip(np.sin(np.pi * p), 0.0, 1.0), cfg["lobe_p"])
        r = r * (1.0 - cfg["neck"]) + (cfg["neck"] * r + cfg["tip_out"]) * node
    return r


def fin_polygon(cfg, phase=0.0):
    """Silhouette of one fin in (s, z); a leaf from the hub out to the
    envelope, existing only where the envelope clears the hub."""
    zs = np.linspace(0.0, cfg["H"], cfg["K"])
    r_out = envelope(zs, cfg, phase)
    keep = r_out > cfg["hub_r"] + 0.8
    idx = np.flatnonzero(keep)
    lo, hi = idx[0], idx[-1] + 1
    zs, r_out = zs[lo:hi], r_out[lo:hi]
    r_in = np.full_like(zs, cfg["hub_r"])
    outer = list(zip(r_out, zs))
    inner = list(zip(r_in[::-1], zs[::-1]))
    return Polygon(outer + inner)


def build_fin(theta0, cfg, phase=0.0):
    """Extrude the fin silhouette to a thin wall and place it at angle theta0.
    With twist, the wall is sheared per height so it spirals."""
    poly = fin_polygon(cfg, phase)
    m = trimesh.creation.extrude_polygon(poly, cfg["t"])   # in XY, extr. Z=t
    # map (X=s, Y=z, Z=thickness) -> world (x=s, y=thickness, z=height)
    swap = np.array([[1., 0., 0., 0.],
                     [0., 0., 1., 0.],
                     [0., 1., 0., 0.],
                     [0., 0., 0., 1.]])
    m.apply_transform(swap)
    m.apply_translation([0, -cfg["t"] / 2.0, 0])           # centre thickness

    if cfg["twist_deg"]:
        tw = math.radians(cfg["twist_deg"])
        V = m.vertices
        frac = np.clip(V[:, 2] / cfg["H"], 0.0, 1.0)
        ang = theta0 + tw * frac
        x, y = V[:, 0].copy(), V[:, 1].copy()
        V[:, 0] = x * np.cos(ang) - y * np.sin(ang)
        V[:, 1] = x * np.sin(ang) + y * np.cos(ang)
    else:
        m.apply_transform(trimesh.transformations.rotation_matrix(
            theta0, (0, 0, 1)))
    return m


def hub(cfg):
    """Central column the fins grow from (the socket housing region)."""
    z0, z1 = 0.12 * cfg["H"], 0.94 * cfg["H"]
    c = trimesh.creation.cylinder(radius=cfg["hub_r"] + 0.6, height=z1 - z0,
                                  sections=64)
    c.apply_translation([0, 0, (z0 + z1) / 2.0])
    return c


def build(cfg, solid=False):
    parts = [build_fin(2.0 * math.pi * b / cfg["n_fin"], cfg,
                       phase=b * cfg.get("stagger", 0.0))
             for b in range(cfg["n_fin"])]
    parts.append(hub(cfg))
    mesh = (trimesh.boolean.union(parts) if solid
            else trimesh.util.concatenate(parts))
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])     # rest on z = 0
    return mesh


PLA_DENSITY = 1.24e-3           # g/mm^3
OVERHENG_DEG = 45.0


def validate(name, cfg, mesh):
    rep = {"namn": name}
    rep["vasstett"] = bool(mesh.is_watertight)
    rep["masse_g"] = float(mesh.volume) * PLA_DENSITY
    rep["trekantar"] = len(mesh.faces)
    rep["hogd_mm"] = float(mesh.extents[2])
    rep["breidd_mm"] = float(mesh.extents[0])
    rep["vegg_mm"] = cfg["t"]
    rep["finnar"] = cfg["n_fin"]
    # overhang printed axis-vertical (the scale beaks are the risk)
    nz = mesh.face_normals[:, 2]
    down = np.clip(-nz, 0.0, 1.0)
    ang = np.degrees(np.arcsin(down))
    areas = mesh.area_faces
    over = (ang > OVERHENG_DEG) & (down < 0.999)
    rep["overheng_areal_pst"] = float(areas[over].sum() / areas.sum() * 100)
    return rep


def write_report(reports, path):
    lines = ["# Ribbe (radiale finnar), valideringsrapport (av `radial.py --solid`)",
             "",
             "> Boolsk union av finnane + nav til éin vasstett solid. Massen er",
             "> hoeg (djupe blad); for lampe vurder tynnare finnar/opnare kjerne.",
             "> Overhenget er dei oppadnebbande skjeltuppane; anten support,",
             "> orientering, eller mildare `hook` i neste steg.",
             "",
             "| Maaltal | " + " | ".join(r["namn"] for r in reports) + " |",
             "|---|" + "---|" * len(reports)]

    def row(label, fmt, key):
        lines.append(f"| {label} | "
                     + " | ".join(fmt.format(r[key]) for r in reports) + " |")

    row("Vasstett solid", "{}", "vasstett")
    row("Finnar", "{}", "finnar")
    row("Vegg (finnetjukkleik)", "{:.1f} mm", "vegg_mm")
    row("Hoegd", "{:.0f} mm", "hogd_mm")
    row("Breidd", "{:.0f} mm", "breidd_mm")
    row("Masse (PLA)", "{:.0f} g", "masse_g")
    row("Overheng > 45 grader", "{:.1f} %", "overheng_areal_pst")
    row("Trekantar", "{}", "trekantar")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--solid", action="store_true",
                    help="boolean-union into one watertight solid + validate")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    reports = []
    for name, cfg in VARIANTS.items():
        mesh = build(cfg, solid=args.solid)
        out = os.path.join(here, "print", f"ribbe-{name}.3mf")
        mesh.export(out)
        line = (f"{name}: tris={len(mesh.faces)} "
                f"extent={[round(x, 1) for x in mesh.extents]}")
        if args.solid:
            rep = validate(name, cfg, mesh)
            reports.append(rep)
            line += (f" watertight={rep['vasstett']} "
                     f"masse={rep['masse_g']:.0f}g "
                     f"overheng={rep['overheng_areal_pst']:.1f}%")
        print(line + f" -> {os.path.relpath(out, here)}")
    if args.solid:
        write_report(reports, os.path.join(here, "validering-v0.1.md"))


if __name__ == "__main__":
    main()
