#!/usr/bin/env python3
"""Lykt: ein parametrisk lampeskjerm-grammatikk. Fem grunnformer, eitt
regelverk. Alt er konstruert, ingenting er teikna for hand:

  1. eit tjukt skal paa ein grunnform (kuppel, ball, sylinder, torus,
     runda terning);
  2. store ovale/linseforma utskjeringar, borra radielt gjennom skalet;
  3. naalehol-klynger (diamant, rosett, trekant) som slepp lys ut i
     punktmoenster;
  4. perler (kuler) paa saumpunkta mellom panela;
  5. krone-piggar, finial og nabbar der forma sluttar.

Kvar variant er ein parameter-dict; same kode byggjer alle. Boolske
operasjonar via manifold3d (trimesh.boolean). Deterministisk: same
parametrar gjev same solid.

Koeyr: python3 lykt.py             (skriv print/lykt-*.3mf + rapport)
       python3 lykt.py --only ball
"""

import math
import os
import numpy as np
import trimesh
from trimesh.transformations import translation_matrix as T4

PHI = (1.0 + math.sqrt(5.0)) / 2.0

VARIANTS = {
    # dome: berande stroppar fraa apex til rim, lange gap mellom,
    # finial paa toppen, perler paa rimen, diamantklynger paa stroppane
    "kuppel": dict(kind="dome", R=92.0, t=4.4, cut=0.10, n=10,
                   gap_lat=38.0, gap_len=0.46, gap_w=0.125, holes_lat=24.0,
                   bead=4.4, pin=1.7, pin_s=4.6),
    # trunkert ikosaeder: pentagonhol, heksagon-rosettar, perler i hjoerna
    "ball": dict(kind="poly", R=82.0, t=4.2, hole_r=0.24,
                 bead=3.6, pin=1.5, pin_s=4.0),
    # sylinder med svak buk, hoege ovale vindauge, skulpturert kronekant
    "krone": dict(kind="crown", R=64.0, H=168.0, t=4.2, bulge=0.05, n=6,
                  slot_w=26.0, slot_h=62.0, slot_z=0.46,
                  crown_h=22.0, notch_r=15.0, bead=4.0, pin=1.6, pin_s=4.2),
    # torus: tre ringar med hol (ytre ekvator, topp-ytre, topp-indre),
    # nabbar rundt sentralopninga, rosettar mellom
    "smultring": dict(kind="torus", R0=66.0, r=31.0, t=4.2, n=14,
                      hole_w=22.0, hole_h=28.0, bead=3.8, nub=11.0,
                      pin=1.5, pin_s=3.6),
    # runda terning: vesica-vindauge paa fire sider, trekantklynger
    # i hjoerna, open topp
    "terning": dict(kind="cube", a=54.0, H=104.0, t=4.4, p=3.4,
                    win_r=30.0, win_off=19.5, top_r=0.66,
                    pin=1.6, pin_s=4.0),
}

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = "manifold"


# ------------------------------------------------------------ small helpers
def frame(d, v):
    """Right-handed frame from a drill direction d and a long axis v (both
    unit, v not parallel d): columns [u, v, d], u = width direction."""
    d = np.asarray(d, float)
    v = np.asarray(v, float)
    v = v - d * (v @ d)
    v /= np.linalg.norm(v)
    u = np.cross(v, d)
    return np.column_stack([u, v, d])


def place(mesh, p, d, v, sx, sy, sz):
    """Scale a unit primitive to (sx, sy, sz) in the local frame (u, v, d)
    and move it to p."""
    M = np.eye(4)
    M[:3, :3] = frame(d, v) @ np.diag([sx, sy, sz])
    M[:3, 3] = p
    m = mesh.copy()
    m.apply_transform(M)
    return m


def unit_cyl(sections=48):
    return trimesh.creation.cylinder(radius=1.0, height=1.0,
                                     sections=sections)


def unit_sph(sub=3):
    return trimesh.creation.icosphere(subdivisions=sub, radius=1.0)


def drill(p, d, v, w, h, L, sections=64):
    """Elliptical through-cutter: cross-section w x h, length L along d."""
    return place(unit_cyl(sections), p, d, v, w / 2.0, h / 2.0, L)


def bead(p, r):
    s = trimesh.creation.icosphere(subdivisions=2, radius=r)
    s.apply_translation(p)
    return s


# naalehol-moenster: offsets i (u, v)-planet, i mm
def pat_diamond(s):
    out = []
    for row, k in ((2, 1), (1, 2), (0, 3), (-1, 2), (-2, 1)):
        for i in range(k):
            out.append(((i - (k - 1) / 2.0) * 2.0 * s, row * s))
    return out


def pat_rosette(s):
    out = [(0.0, 0.0)]
    for k, rr in ((6, s), (12, 2.0 * s)):
        for i in range(k):
            a = 2.0 * math.pi * i / k + (0.26 if k == 12 else 0.0)
            out.append((rr * math.cos(a), rr * math.sin(a)))
    return out


def pat_tri(s, up=True):
    out = []
    for row in range(4):                     # 1+2+3+4 = 10 prikkar
        y = (1.5 - row) * s * (1.0 if up else -1.0)
        for i in range(row + 1):
            out.append(((i - row / 2.0) * 1.9 * s, y))
    return out


def pinholes(p, d, v, offsets, r, L=44.0):
    """A cluster of small parallel drills around p, offsets in the (u, v)
    tangent plane."""
    F = frame(d, v)
    u, vv = F[:, 0], F[:, 1]
    return [drill(p + du * u + dv * vv, d, v, 2 * r, 2 * r, L, sections=16)
            for du, dv in offsets]


def boolean_build(shell, cutters, adds):
    out = shell
    if cutters:
        out = trimesh.boolean.difference(
            [out, trimesh.util.concatenate(cutters)], engine=ENGINE)
    if adds:
        out = trimesh.boolean.union([out] + adds, engine=ENGINE)
    return out


# ------------------------------------------------------------------- kuppel
def build_kuppel(c):
    R, t = c["R"], c["t"]
    z0 = c["cut"] * R                      # kutthoegd: rimen ligg her
    outer = trimesh.creation.icosphere(subdivisions=4, radius=R)
    inner = trimesh.creation.icosphere(subdivisions=4, radius=R - t)
    box = trimesh.creation.box(extents=[3 * R, 3 * R, 2 * R])
    box.apply_translation([0, 0, z0 - R])
    shell = trimesh.boolean.difference([outer, inner, box], engine=ENGINE)

    n = c["n"]
    cutters, adds = [], []

    def sph_pt(lat, az):
        la, th = math.radians(lat), az
        d = np.array([math.cos(la) * math.cos(th),
                      math.cos(la) * math.sin(th), math.sin(la)])
        v = np.array([-math.sin(la) * math.cos(th),
                      -math.sin(la) * math.sin(th), math.cos(la)])
        return R * d, d, v

    # lange gap mellom stroppane (ellipsoide-kuttarar langs meridianane)
    for i in range(n):
        th = 2.0 * math.pi * (i + 0.5) / n
        p, d, v = sph_pt(c["gap_lat"], th)
        cutters.append(place(unit_sph(3), p, d, v,
                             c["gap_w"] * R, c["gap_len"] * R, 0.38 * R))
    # diamantklynger paa kvar stropp
    for i in range(n):
        th = 2.0 * math.pi * i / n
        p, d, v = sph_pt(c["holes_lat"], th)
        cutters += pinholes(p, d, v, pat_diamond(c["pin_s"]), c["pin"])
    # ring av naalehol rundt finialen
    for i in range(8):
        th = 2.0 * math.pi * (i + 0.5) / 8
        p, d, v = sph_pt(74.0, th)
        cutters += pinholes(p, d, v, [(0.0, 0.0)], c["pin"])

    # perler paa rimen, ved kvar stropp
    lat_rim = math.degrees(math.asin(z0 / R)) + 2.6
    for i in range(n):
        th = 2.0 * math.pi * i / n
        p, _, _ = sph_pt(lat_rim, th)
        adds.append(bead(p, c["bead"]))
    # finial: liten kjegle + kule paa apex
    fin = trimesh.creation.cone(radius=9.0, height=11.0, sections=48)
    fin.apply_translation([0, 0, R - 2.5])
    adds.append(fin)
    adds.append(bead(np.array([0, 0, R + 9.0]), 5.2))

    mesh = boolean_build(shell, cutters, adds)
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return mesh


# --------------------------------------------------------------------- ball
def _trunc_icosa_verts():
    """Dei 60 hjoerna i eit trunkert ikosaeder (einingsstorleik)."""
    base = [(0.0, 1.0, 3.0 * PHI), (1.0, 2.0 + PHI, 2.0 * PHI),
            (PHI, 2.0, 2.0 * PHI + 1.0)]
    V = set()
    for b in base:
        for cyc in range(3):
            x, y, z = b[cyc:] + b[:cyc]
            for sx in ((1, -1) if x else (1,)):
                for sy in ((1, -1) if y else (1,)):
                    for sz in ((1, -1) if z else (1,)):
                        V.add((sx * x, sy * y, sz * z))
    return np.array(sorted(V))


def _ico_dirs():
    """12 pentagon-retningar (ikosaeder-hjoerna), normaliserte."""
    out = set()
    for b in [(0.0, 1.0, PHI)]:
        for cyc in range(3):
            x, y, z = b[cyc:] + b[:cyc]
            for sy in (1, -1):
                for sz in (1, -1):
                    out.add((x, sy * y, sz * z))
    D = np.array(sorted(out))
    return D / np.linalg.norm(D, axis=1, keepdims=True)


def _hex_dirs():
    """20 heksagon-retningar (dodekaeder-hjoerna), normaliserte."""
    out = set()
    for sx in (1, -1):
        for sy in (1, -1):
            for sz in (1, -1):
                out.add((sx * 1.0, sy * 1.0, sz * 1.0))
    for b in [(0.0, 1.0 / PHI, PHI)]:
        for cyc in range(3):
            x, y, z = b[cyc:] + b[:cyc]
            for sy in (1, -1):
                for sz in (1, -1):
                    out.add((x, sy * y, sz * z))
    D = np.array(sorted(out))
    return D / np.linalg.norm(D, axis=1, keepdims=True)


def build_ball(c):
    R, t = c["R"], c["t"]
    V = _trunc_icosa_verts()
    V = V / np.linalg.norm(V, axis=1).max()        # circumradius 1
    outer = trimesh.convex.convex_hull(V * R)
    inner = trimesh.convex.convex_hull(V * (R - t))
    # roter so ei pentagonakse peikar opp: stabil fot, kabelutgang nede
    d0 = _ico_dirs()[0]
    Rz = trimesh.geometry.align_vectors(d0, [0, 0, 1.0])
    shell = trimesh.boolean.difference([outer, inner], engine=ENGINE)
    shell.apply_transform(Rz)

    pents = _ico_dirs() @ np.asarray(Rz)[:3, :3].T
    hexes = _hex_dirs() @ np.asarray(Rz)[:3, :3].T

    cutters = []
    up = np.array([0, 0, 1.0])
    # store runde hol gjennom pentagonsentera (6 aksar, hol i begge endar)
    done = []
    for d in pents:
        if any(np.allclose(d, -e) for e in done):
            continue
        done.append(d)
        v = up if abs(d @ up) < 0.9 else np.array([1.0, 0, 0])
        cutters.append(drill(np.zeros(3), d, v,
                             2 * c["hole_r"] * R, 2 * c["hole_r"] * R,
                             2.4 * R))
    # rosettar paa annakvar heksagonakse, smaa hol paa resten
    done = []
    for k, d in enumerate(hexes):
        if any(np.allclose(d, -e) for e in done):
            continue
        done.append(d)
        v = up if abs(d @ up) < 0.9 else np.array([1.0, 0, 0])
        p = d * R
        if k % 2 == 0:
            cutters += pinholes(p, d, v, pat_rosette(c["pin_s"]),
                                c["pin"], L=2.4 * R)
        else:
            cutters.append(drill(np.zeros(3), d, v, 16.0, 16.0, 2.4 * R))

    # perle i kvart av dei 60 hjoerna
    W = (V / np.linalg.norm(V, axis=1, keepdims=True)) @ np.asarray(Rz)[:3, :3].T
    adds = [bead(w * (R - 0.6), c["bead"]) for w in W]

    mesh = boolean_build(shell, cutters, adds)
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return mesh


# -------------------------------------------------------------------- krone
def build_krone(c):
    R, H, t, n = c["R"], c["H"], c["t"], c["n"]

    def ro(z):
        return R * (1.0 + c["bulge"] * math.sin(math.pi * z / H))

    zs = np.linspace(0.0, H, 48)
    prof = [(ro(z), z) for z in zs] + [(ro(z) - t, z) for z in zs[::-1]]
    prof.append(prof[0])                       # lukka profil: vasstett solid
    shell = trimesh.creation.revolve(prof, sections=96)
    if shell.volume < 0:
        shell.invert()
    if not shell.is_volume:
        shell.process(validate=True)
        trimesh.repair.fix_normals(shell)

    cutters, adds = [], []
    up = np.array([0, 0, 1.0])

    def rad(th):
        return np.array([math.cos(th), math.sin(th), 0.0])

    # hoege ovale vindauge, eitt per panel
    zc = c["slot_z"] * H
    for i in range(n):
        th = 2.0 * math.pi * i / n
        p = rad(th) * ro(zc); p[2] = zc
        cutters.append(drill(p, rad(th), up, c["slot_w"], c["slot_h"], 56.0))
    # rosettar under vindauga, diamantar i toppbandet
    for i in range(n):
        th = 2.0 * math.pi * i / n
        p = rad(th) * ro(0.14 * H); p[2] = 0.14 * H
        cutters += pinholes(p, rad(th), up, pat_rosette(c["pin_s"]),
                            c["pin"], L=40.0)
        p2 = rad(th) * ro(0.80 * H); p2[2] = 0.80 * H
        cutters += pinholes(p2, rad(th), up, pat_diamond(c["pin_s"]),
                            c["pin"], L=40.0)
    # kronekanten: skaler ut boger mellom piggposisjonane
    for i in range(n):
        th = 2.0 * math.pi * (i + 0.5) / n
        p = rad(th) * ro(H); p[2] = H + 3.0
        cutters.append(drill(p, rad(th), up,
                             2 * c["notch_r"], 2 * c["notch_r"], 40.0,
                             sections=48))
    # piggar med kuletippar paa dei staaande punkta
    for i in range(n):
        th = 2.0 * math.pi * i / n
        base = rad(th) * (ro(H) - t / 2.0); base[2] = H - 6.0
        cone = trimesh.creation.cone(radius=6.5, height=c["crown_h"],
                                     sections=32)
        cone.apply_translation(base)
        adds.append(cone)
        tip = base.copy(); tip[2] += c["crown_h"]
        adds.append(bead(tip, 2.8))
    # perler paa saumane: botnring, midtring, toppband
    for zf, extra in ((0.035, 0.0), (0.46, math.pi / n), (0.72, 0.0)):
        z = zf * H
        for i in range(n):
            th = 2.0 * math.pi * i / n + extra
            p = rad(th) * ro(z); p[2] = z
            adds.append(bead(p, c["bead"]))

    mesh = boolean_build(shell, cutters, adds)
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return mesh


# ---------------------------------------------------------------- smultring
def build_smultring(c):
    R0, r, t, n = c["R0"], c["r"], c["t"], c["n"]
    outer = trimesh.creation.torus(major_radius=R0, minor_radius=r,
                                   major_sections=128, minor_sections=64)
    inner = trimesh.creation.torus(major_radius=R0, minor_radius=r - t,
                                   major_sections=128, minor_sections=64)
    shell = trimesh.boolean.difference([outer, inner], engine=ENGINE)

    def tor_pt(th, psi):
        e = np.array([math.cos(th), math.sin(th), 0.0])
        d = math.cos(psi) * e + math.sin(psi) * np.array([0, 0, 1.0])
        v = -math.sin(psi) * e + math.cos(psi) * np.array([0, 0, 1.0])
        return R0 * e + r * d, d, v

    cutters, adds = [], []
    # ring A: ovale hol paa ytre ekvator; ring B: topp-ytre; ring C:
    # topp-indre (dei som ser ned i sentralopninga)
    for psi_deg, wf, hf, off in ((0.0, 1.0, 1.15, 0.0),
                                 (52.0, 0.92, 1.0, 0.5),
                                 (118.0, 0.78, 0.85, 0.0)):
        psi = math.radians(psi_deg)
        for i in range(n):
            th = 2.0 * math.pi * (i + off) / n
            p, d, v = tor_pt(th, psi)
            cutters.append(drill(p, d, v, c["hole_w"] * wf,
                                 c["hole_h"] * hf, 40.0))
    # rosettar paa annakvart segment, mellom ring A og B
    for i in range(0, n, 2):
        th = 2.0 * math.pi * (i + 0.5) / n
        p, d, v = tor_pt(th, math.radians(26.0))
        cutters += pinholes(p, d, v, pat_rosette(c["pin_s"]), c["pin"],
                            L=30.0)
    # perler paa saumane (to breidder)
    for psi_deg, rb in ((30.0, c["bead"]), (86.0, c["bead"] * 0.85)):
        for i in range(n):
            th = 2.0 * math.pi * (i + 0.5) / n
            p, _, _ = tor_pt(th, math.radians(psi_deg))
            adds.append(bead(p, rb))
    # nabbar rundt sentralopninga, som ei laag krone
    for i in range(n):
        th = 2.0 * math.pi * i / n
        p, d, _ = tor_pt(th, math.radians(146.0))
        cone = trimesh.creation.cone(radius=4.2, height=c["nub"],
                                     sections=24)
        M = np.eye(4)
        M[:3, :3] = frame(np.array([0, 0, 1.0]),
                          np.array([math.cos(th), math.sin(th), 0.0]))
        M[:3, 3] = p - d * 1.5
        cone.apply_transform(M)
        adds.append(cone)

    mesh = boolean_build(shell, cutters, adds)
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return mesh


# ------------------------------------------------------------------ terning
def build_terning(c):
    a, H, t, p = c["a"], c["H"], c["t"], c["p"]
    k = 64
    ang = np.linspace(0, 2 * math.pi, 4 * k, endpoint=False)
    # superellipse-profil |x/a|^p + |y/a|^p = 1
    xs = a * np.sign(np.cos(ang)) * np.abs(np.cos(ang)) ** (2.0 / p)
    ys = a * np.sign(np.sin(ang)) * np.abs(np.sin(ang)) ** (2.0 / p)
    from shapely.geometry import Polygon
    poly = Polygon(np.column_stack([xs, ys]))
    outer = trimesh.creation.extrude_polygon(poly, height=H)
    inner = trimesh.creation.extrude_polygon(poly.buffer(-t), height=H)
    inner.apply_translation([0, 0, t])
    shell = trimesh.boolean.difference([outer, inner], engine=ENGINE)

    # runda skulder: skjer med ellipsoid, flat fot att med golvkutt
    dome = unit_sph(4)
    dome.apply_transform(np.diag([a * 1.50, a * 1.50, H * 0.92, 1.0]))
    dome.apply_translation([0, 0, H * 0.30])
    shell = trimesh.boolean.intersection([shell, dome], engine=ENGINE)

    cutters = []
    up = np.array([0, 0, 1.0])
    # open topp
    top = unit_cyl(96)
    top.apply_transform(np.diag([c["top_r"] * a, c["top_r"] * a, H, 1.0]))
    top.apply_translation([0, 0, H * 0.9])
    cutters.append(top)
    # vesica-vindauge paa dei fire sidene: snittet av to sirkelsylindrar
    for i in range(4):
        th = math.pi / 2.0 * i
        d = np.array([math.cos(th), math.sin(th), 0.0])
        u = np.cross(up, d)
        pc = d * a * 0.7; pc[2] = H * 0.46
        c1 = drill(pc + u * c["win_off"], d, up,
                   2 * c["win_r"], 2 * c["win_r"], 60.0)
        c2 = drill(pc - u * c["win_off"], d, up,
                   2 * c["win_r"], 2 * c["win_r"], 60.0)
        cutters.append(trimesh.boolean.intersection([c1, c2],
                                                    engine=ENGINE))
    # trekantklynger paa dei fire runda hjoerna, oppe og nede
    for i in range(4):
        th = math.pi / 2.0 * i + math.pi / 4.0
        d = np.array([math.cos(th), math.sin(th), 0.0])
        pc = d * a * 0.86; pc[2] = H * 0.74
        cutters += pinholes(pc, d, up, pat_tri(c["pin_s"], up=False),
                            c["pin"], L=44.0)
        pc2 = d * a * 0.86; pc2[2] = H * 0.20
        cutters += pinholes(pc2, d, up, pat_tri(c["pin_s"], up=True),
                            c["pin"], L=44.0)

    mesh = boolean_build(shell, cutters, [])
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return mesh


BUILDERS = {"dome": build_kuppel, "poly": build_ball, "crown": build_krone,
            "torus": build_smultring, "cube": build_terning}


# --------------------------------------------------------------------- main
def build(name):
    cfg = VARIANTS[name]
    return BUILDERS[cfg["kind"]](cfg)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    args = ap.parse_args()
    os.makedirs(os.path.join(HERE, "print"), exist_ok=True)
    rows = []
    for name in VARIANTS:
        if args.only and args.only not in name:
            continue
        mesh = build(name)
        out = os.path.join(HERE, "print", f"lykt-{name}.3mf")
        mesh.export(out)
        ext = [round(x, 1) for x in mesh.extents]
        vol = mesh.volume / 1000.0            # cm3
        rows.append((name, ext, round(vol, 1), mesh.is_watertight,
                     len(mesh.faces)))
        print(f"{name}: {ext} mm, {vol:.0f} cm3, "
              f"watertight={mesh.is_watertight}, tris={len(mesh.faces)}")
    rep = os.path.join(HERE, "validering-v01.md")
    with open(rep, "w") as f:
        f.write("# Lykt v0.1, validering\n\n")
        f.write("Generert av `lykt.py`. PLA 1,24 g/cm3.\n\n")
        f.write("| variant | boks (mm) | volum (cm3) | masse (g) |"
                " vasstett | trekantar |\n|---|---|---|---|---|---|\n")
        for name, ext, vol, wt, tris in rows:
            f.write(f"| {name} | {ext[0]} x {ext[1]} x {ext[2]} | {vol} |"
                    f" {round(vol * 1.24)} | {'ja' if wt else 'NEI'} |"
                    f" {tris} |\n")
    print(f"-> {os.path.relpath(rep, HERE)}")


if __name__ == "__main__":
    main()
