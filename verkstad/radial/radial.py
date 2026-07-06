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
VARIANTS = {
    "leaf": dict(n_fin=30, H=185.0, r_max=88.0, hub_r=14.0, t=2.5,
                 power=0.58, twist_deg=0.0, neck=0.0, bump_freq=0,
                 tip_out=0.0, hook=0.0, lobe_p=0.65, K=170),
    "vertebra": dict(n_fin=34, H=190.0, r_max=86.0, hub_r=15.0, t=2.4,
                     power=0.56, twist_deg=0.0, neck=0.10, bump_freq=8,
                     tip_out=7.0, hook=0.55, lobe_p=0.72, K=170),
    "spiral": dict(n_fin=36, H=184.0, r_max=88.0, hub_r=14.0, t=2.3,
                   power=0.56, twist_deg=34.0, neck=0.10, bump_freq=7,
                   tip_out=8.0, hook=0.72, lobe_p=0.86, K=180),
}


def envelope(z, cfg):
    """Outer radius at height z: a ball (0 at the poles, r_max at the equator,
    `power` < 1 fuller) with rounded vertebra lobes on the edge. Each lobe is
    a smooth node with a deep neck below it; `hook` skews the node upward so
    the tips beak up-and-out like scales."""
    zf = np.clip(z / cfg["H"], 0.0, 1.0)
    base = cfg["r_max"] * np.power(np.sin(np.pi * zf), cfg["power"])
    if cfg["bump_freq"]:
        p = (cfg["bump_freq"] * zf) % 1.0
        if cfg["hook"]:
            # skew the phase so the node rises slowly and drops fast (a beak)
            p = np.clip(p + cfg["hook"] * p * (1.0 - p), 0.0, 1.0)
        node = np.power(np.clip(np.sin(np.pi * p), 0.0, 1.0), cfg["lobe_p"])
        base = base * (1.0 - cfg["neck"]) + (cfg["neck"] * base
                                             + cfg["tip_out"]) * node
    return base


def fin_polygon(cfg):
    """Silhouette of one fin in (s, z); a leaf from the hub out to the
    envelope, existing only where the envelope clears the hub."""
    zs = np.linspace(0.0, cfg["H"], cfg["K"])
    r_out = envelope(zs, cfg)
    keep = r_out > cfg["hub_r"] + 0.8
    idx = np.flatnonzero(keep)
    lo, hi = idx[0], idx[-1] + 1
    zs, r_out = zs[lo:hi], r_out[lo:hi]
    r_in = np.full_like(zs, cfg["hub_r"])
    outer = list(zip(r_out, zs))
    inner = list(zip(r_in[::-1], zs[::-1]))
    return Polygon(outer + inner)


def build_fin(theta0, cfg):
    """Extrude the fin silhouette to a thin wall and place it at angle theta0.
    With twist, the wall is sheared per height so it spirals."""
    poly = fin_polygon(cfg)
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


def build(cfg):
    parts = [build_fin(2.0 * math.pi * b / cfg["n_fin"], cfg)
             for b in range(cfg["n_fin"])]
    parts.append(hub(cfg))
    mesh = trimesh.util.concatenate(parts)
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])     # rest on z = 0
    return mesh


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    for name, cfg in VARIANTS.items():
        mesh = build(cfg)
        out = os.path.join(here, "print", f"ribbe-{name}.3mf")
        mesh.export(out)
        print(f"{name}: tris={len(mesh.faces)} "
              f"extent={[round(x, 1) for x in mesh.extents]} -> "
              f"{os.path.relpath(out, here)}")


if __name__ == "__main__":
    main()
