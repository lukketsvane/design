#!/usr/bin/env python3
"""Ribbe v2, the lattice reading of Ivers reference: a barrel of wavy vertical
ribs made of ROUNDED tubular struts, connected by staggered rungs so the gaps
between them are eye-shaped holes. Everything is round (tubes + spherical
joints), fused and glossy, like coral or bone, hollow and open, not a solid
ball of scales.

Construction: a node grid on a barrel surface (n_col columns x n_row rows,
brick-staggered). The ribs snake in theta (adjacent ribs out of phase so they
weave). Every rib segment is a capsule (cylinder + spherical joints); rungs
bridge adjacent ribs on alternating rows. Concatenated for render; boolean
union for print.

Run: python3 lattice.py            (writes print/lattice-*.3mf)
"""

import math
import os
import numpy as np
import trimesh

VARIANTS = {
    "coral": dict(n_col=22, n_row=22, H=176.0, r_max=90.0, waist=0.34,
                  strut=6.2, wave=0.5, wavef=4.0, ribphase=0.5,
                  taper_top=0.62, rungs=True, crown=16.0),
    "reef": dict(n_col=28, n_row=28, H=182.0, r_max=94.0, waist=0.32,
                 strut=4.6, wave=0.46, wavef=5.0, ribphase=0.5,
                 taper_top=0.58, rungs=True, crown=13.0),
    "column": dict(n_col=16, n_row=20, H=204.0, r_max=82.0, waist=0.20,
                   strut=7.4, wave=0.55, wavef=3.0, ribphase=0.5,
                   taper_top=0.8, rungs=True, crown=20.0),
}


def barrel_R(zf, cfg):
    """Radius profile up the barrel: bulged at the waist, drawn in at the ends,
    and pulled in further at the top (taper_top) for the open crown."""
    bulge = 1.0 - cfg["waist"] * (2.0 * zf - 1.0) ** 2
    crown = 1.0 - (1.0 - cfg["taper_top"]) * np.clip((zf - 0.6) / 0.4, 0, 1) ** 2
    return cfg["r_max"] * bulge * crown


def node(c, r, cfg):
    N, M = cfg["n_col"], cfg["n_row"]
    zf = r / (M - 1)
    z = zf * cfg["H"]
    dtheta = 2.0 * math.pi / N
    # adjacent ribs wave in antiphase so they pinch together (fuse) and bow
    # apart, opening lens/eye-shaped holes between them
    wig = cfg["wave"] * dtheta * math.sin(
        cfg["wavef"] * math.pi * zf + math.pi * (c % 2))
    th = c * dtheta + wig
    R = barrel_R(zf, cfg)
    return np.array([R * math.cos(th), R * math.sin(th), z])


def strut(p0, p1, r):
    return trimesh.creation.cylinder(radius=r, segment=[p0, p1], sections=24)


def joint(p, r):
    s = trimesh.creation.icosphere(subdivisions=2, radius=r)
    s.apply_translation(p)
    return s


def build(cfg, solid=False):
    N, M = cfg["n_col"], cfg["n_row"]
    sr = cfg["strut"]
    P = {(c, r): node(c, r, cfg) for c in range(N) for r in range(M)}
    parts = [joint(p, sr) for p in P.values()]
    # vertical rib segments
    for c in range(N):
        for r in range(M - 1):
            parts.append(strut(P[(c, r)], P[(c, r + 1)], sr))
    # spiky crown + feet: extend each rib past the rims to a free tapering tip
    if cfg.get("crown"):
        for c in range(N):
            for end, sgn in ((M - 1, 1.0), (0, -1.0)):
                base = P[(c, end)]
                out = base.copy()
                out[:2] *= 1.32                    # splay the tip outward
                out[2] = base[2] + sgn * cfg["crown"]
                parts.append(strut(base, out, sr * 0.8))
                parts.append(joint(out, sr * 0.5))   # small beak
    # rungs: with antiphase ribs the ribs pinch and fuse on their own, so
    # rungs are only needed at the rims for a clean mouth/foot (unless the
    # variant asks for a full ladder)
    rung_rows = (range(M) if cfg.get("rungs") == "all"
                 else (0, M - 1) if cfg.get("rungs", True) else ())
    for c in range(N):
        for r in rung_rows:
            parts.append(strut(P[(c, r)], P[((c + 1) % N, r)], sr))
    mesh = (trimesh.boolean.union(parts) if solid
            else trimesh.util.concatenate(parts))
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return mesh


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--solid", action="store_true")
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "print"), exist_ok=True)
    for name, cfg in VARIANTS.items():
        mesh = build(cfg, solid=args.solid)
        out = os.path.join(here, "print", f"lattice-{name}.3mf")
        mesh.export(out)
        print(f"{name}: tris={len(mesh.faces)} "
              f"extent={[round(x, 1) for x in mesh.extents]} "
              f"watertight={mesh.is_watertight} -> {os.path.relpath(out, here)}")


if __name__ == "__main__":
    main()
