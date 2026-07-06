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
                  taper_top=0.62, rungs=True, crown=16.0,
                  seed=7, ribvar=0.16, strut_var=0.07),
    "reef": dict(n_col=26, n_row=22, H=182.0, r_max=94.0, waist=0.32,
                 strut=4.6, wave=0.46, wavef=4.5, ribphase=0.5,
                 taper_top=0.58, rungs=True, crown=13.0,
                 seed=3, ribvar=0.12, strut_var=0.06),
    "column": dict(n_col=16, n_row=20, H=204.0, r_max=82.0, waist=0.20,
                   strut=7.4, wave=0.55, wavef=3.0, ribphase=0.5,
                   taper_top=0.8, rungs=True, crown=20.0,
                   seed=11, ribvar=0.16, strut_var=0.08),
}


def barrel_R(zf, cfg):
    """Radius profile up the barrel: bulged at the waist, drawn in at the ends,
    and pulled in further at the top (taper_top) for the open crown."""
    bulge = 1.0 - cfg["waist"] * (2.0 * zf - 1.0) ** 2
    crown = 1.0 - (1.0 - cfg["taper_top"]) * np.clip((zf - 0.6) / 0.4, 0, 1) ** 2
    return cfg["r_max"] * bulge * crown


def _rng(cfg, *key):
    """Deterministic per-key rng, so the jitter is reproducible per seed."""
    h = cfg.get("seed", 0) * 100003
    for k in key:
        h = h * 331 + int(k)
    return np.random.default_rng(h % (2 ** 32))


def node(c, r, cfg):
    N, M = cfg["n_col"], cfg["n_row"]
    zf = r / (M - 1)
    z = zf * cfg["H"]
    dtheta = 2.0 * math.pi / N
    # per-rib variation (constant along the rib, so the rib stays smooth): its
    # own wave amplitude, phase and radius, so the ribs and eye-holes are not
    # identical, a hand-made read without kinking the tubes
    rv = cfg.get("ribvar", 0.0)
    amp, phi, rfac = cfg["wave"], 0.0, 1.0
    if rv:
        g = _rng(cfg, c)
        amp *= 1.0 + g.normal(0, rv)
        phi = g.normal(0, rv * 1.4)
        rfac = 1.0 + g.normal(0, rv * 0.4)
    # adjacent ribs wave in antiphase so they pinch together (fuse) and bow
    # apart, opening lens/eye-shaped holes between them
    wig = amp * dtheta * math.sin(
        cfg["wavef"] * math.pi * zf + math.pi * (c % 2) + phi)
    th = c * dtheta + wig
    R = barrel_R(zf, cfg) * rfac
    return np.array([R * math.cos(th), R * math.sin(th), z])


def catmull_rom(pts, per=4):
    """Smooth polyline through the nodes so the ribs read as continuous tubes
    instead of a chain of straight segments (the bamboo look)."""
    pts = np.asarray(pts)
    n = len(pts)
    out = []
    for i in range(n - 1):
        p0, p1, p2, p3 = (pts[max(i - 1, 0)], pts[i], pts[i + 1],
                          pts[min(i + 2, n - 1)])
        for t in np.linspace(0.0, 1.0, per, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t
                              + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def strut(p0, p1, r):
    return trimesh.creation.cylinder(radius=r, segment=[p0, p1], sections=24)


def tube(pts, r):
    """A smooth tube along a point list: overlapping cylinders + joint balls."""
    parts = []
    for i in range(len(pts) - 1):
        if np.linalg.norm(np.asarray(pts[i + 1]) - pts[i]) < 1e-6:
            continue
        parts.append(strut(pts[i], pts[i + 1], r))
    for p in pts[::2]:
        parts.append(joint(p, r))
    return parts


def joint(p, r):
    s = trimesh.creation.icosphere(subdivisions=2, radius=r)
    s.apply_translation(p)
    return s


def build(cfg, solid=False):
    N, M = cfg["n_col"], cfg["n_row"]
    sr = cfg["strut"]
    sv = cfg.get("strut_var", 0.0)

    def rad(*key):
        return sr * (1.0 + (_rng(cfg, 9, *key).normal(0, sv) if sv else 0.0))

    P = {(c, r): node(c, r, cfg) for c in range(N) for r in range(M)}
    parts = []
    # smooth vertical ribs (spline through the nodes -> continuous tubes)
    for c in range(N):
        col = [P[(c, r)] for r in range(M)]
        parts += tube(catmull_rom(col, per=3), rad(c, 0, 1))
    # spiky crown + feet: extend each rib past the rims to a free tapering tip
    if cfg.get("crown"):
        for c in range(N):
            for end, sgn in ((M - 1, 1.0), (0, -1.0)):
                base = P[(c, end)]
                g = _rng(cfg, 5, c, end)
                out = base.copy()
                out[:2] *= 1.32 + (g.normal(0, 0.06) if sv else 0.0)
                out[2] = base[2] + sgn * cfg["crown"] * (
                    1.0 + (g.normal(0, 0.22) if sv else 0.0))
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
