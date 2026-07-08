#!/usr/bin/env python3
"""Grind: ein grafbasert byggjar for skjelett-strukturar av roer og kuler,
smelta saman som keramikk (Ivers fem referansar 2026-07-08: tromme, stjerne,
totem, korg, krabbe). Same konstruksjonsprinsipp som ../krone/krone.py: eitt
signert felt der alt er mjuke unionar (smin), polygonisert med marching
cubes. Heile strukturen er n-periodisk kring aksen og definert av eitt
segment:

  nivaa      L nodekransar i hoegda, radius som funksjon av u (botn, topp,
             buk), valfri twist (fasedreiing per nivaa)
  stag       kapsel-bogar mellom nivaa (BOGE bular utover), valfrie
             X-diagonalar
  ringar     torusar paa nivaa (ingen, endane, alle)
  eiker      stag fraa oevste krans inn til koppen
  kopp       sentral lysestake-kopp med boring
  kuler      ledd-kuler paa nodane, knoppar (smaa nubbar utover)
  munningar  opne roerender som foeter (aksial boring subtrahert)

Koeyr: python3 grind.py            (skriv print/grind-*.3mf + rapport)
       python3 grind.py --only korg --pitch 1.4
"""

import argparse
import math
import os
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))

VARIANTS = {
    # laag tromleforma korg med ovale hol, eiker og kopp (ref 1)
    "tromme": dict(n=8, L=2, H=84.0, R=64.0, f_bot=1.0, f_top=1.0, buk=0.0,
                   twist=0.0, bow=12.0, tube=7.2, diag=0.0, rings=2,
                   spokes=1, ball=9.0, nub=4.2, cup=20.0, mlen=0.0,
                   tilt=0.0, k=5.0),
    # flat stjernefot med kraftige kuler og kopp (ref 2)
    "stjerne": dict(n=5, L=1, H=36.0, R=84.0, f_bot=1.0, f_top=1.0, buk=0.0,
                    twist=0.0, bow=0.0, tube=7.0, diag=0.0, rings=2,
                    spokes=1, ball=13.0, nub=0.0, cup=18.0, mlen=0.0,
                    tilt=0.0, k=6.0),
    # hoeg open totem med boga stag og roermunningar (ref 3)
    "totem": dict(n=3, L=3, H=170.0, R=50.0, f_bot=1.1, f_top=0.85,
                  buk=0.0, twist=0.5, bow=14.0, tube=8.0, diag=1.0,
                  rings=1, spokes=0, ball=9.5, nub=0.0, cup=0.0, mlen=20.0,
                  tilt=28.0, k=6.5),
    # korgvase i tre nivaa med X-fletting og knoppar (ref 4)
    "korg": dict(n=6, L=3, H=148.0, R=58.0, f_bot=1.18, f_top=0.92,
                 buk=-0.08, twist=0.5, bow=7.0, tube=5.6, diag=1.0,
                 rings=2, spokes=0, ball=6.5, nub=3.2, cup=0.0, mlen=0.0,
                 tilt=0.0, k=4.5),
    # laag krabbe med kopp og skraastilte roerfoeter (ref 5)
    "krabbe": dict(n=5, L=1, H=52.0, R=62.0, f_bot=1.0, f_top=1.0, buk=0.0,
                   twist=0.0, bow=0.0, tube=6.8, diag=0.0, rings=2,
                   spokes=1, ball=9.0, nub=0.0, cup=17.0, mlen=18.0,
                   tilt=52.0, k=6.0),
    # kloeverfot: tilta blad-loops kring koppen, knoppkuler (ref 6)
    "kloever": dict(n=4, L=1, H=52.0, R=40.0, f_bot=1.0, f_top=1.0, buk=0.0,
                    twist=0.0, bow=0.0, tube=7.0, diag=0.0, rings=0,
                    spokes=1, ball=8.5, nub=0.0, cup=16.0, mlen=0.0,
                    tilt=0.0, k=5.5,
                    loop=26.0, loop_out=50.0, loop_zf=0.34, loop_tilt=56.0,
                    loop_ell=0.85),
    # dropebur: hoege vertikale drope-loops, midtring med kopp (ref 7)
    "drope": dict(n=3, L=1, H=150.0, R=33.0, f_bot=1.0, f_top=1.0, buk=0.0,
                  twist=0.0, bow=0.0, tube=6.4, diag=0.0, rings=2,
                  spokes=1, ball=0.0, nub=0.0, cup=15.0, mlen=0.0,
                  tilt=0.0, k=6.5,
                  loop=36.0, loop_out=62.0, loop_zf=0.43, loop_tilt=6.0,
                  loop_ell=1.6, loop_lean=15.0),
}
VARIANTS["drope"]["cup_zf"] = 0.55
for _c in VARIANTS.values():
    _c.setdefault("cup_zf", 0.0)          # 0 = automatisk (topp)
    _c.setdefault("loop", 0.0)
    _c.setdefault("loop_out", 40.0)
    _c.setdefault("loop_zf", 0.4)
    _c.setdefault("loop_tilt", 0.0)
    _c.setdefault("loop_ell", 1.0)
    _c.setdefault("loop_lean", 0.0)


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1.0 - h) + a * h - k * h * (1.0 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


# --------------------------------------------------- segment-geometrien
def levels(c):
    """(z, r, fase) for kvar nodekrans."""
    L = c["L"]
    out = []
    for l in range(L):
        u = 0.55 if L == 1 else l / (L - 1.0)
        r = c["R"] * (c["f_bot"] + (c["f_top"] - c["f_bot"]) * u
                      + 4.0 * c["buk"] * u * (1.0 - u))
        z = 0.55 * c["H"] if L == 1 else u * c["H"]
        per = 2.0 * math.pi / c["n"]
        out.append((z, r, c["twist"] * per * l))
    return out


def node(lv, th):
    z, r, ph = lv
    return np.array([r * math.cos(th + ph), r * math.sin(th + ph), z])


def arc_points(p0, p1, bow, m=10):
    """Kjede av punkt fraa p0 til p1, bula utover radielt med sin-profil."""
    ts = np.linspace(0.0, 1.0, m + 1)
    pts = []
    for t in ts:
        p = p0 + (p1 - p0) * t
        e = p[:2].copy()
        nrm = np.linalg.norm(e)
        if nrm > 1e-9 and bow:
            p = p.copy()
            p[:2] += e / nrm * bow * math.sin(math.pi * t)
        pts.append(p)
    return pts


def elements(c):
    """Kapslar (p0, p1, radius, kopiar), kuler (p, r), torusar (z, r, rr),
    boringar (p0, akse, radius, lengd). Alt for EITT segment; 'kopiar' er
    theta-offset som elementet ogsaa finst paa (naboar for diagonalane)."""
    lv = levels(c)
    per = 2.0 * math.pi / c["n"]
    caps, balls, tori, bores = [], [], [], []
    tube = c["tube"]

    for l in range(len(lv) - 1):                     # stag med boge
        p0, p1 = node(lv[l], 0.0), node(lv[l + 1], 0.0)
        pts = arc_points(p0, p1, c["bow"])
        for a, b in zip(pts[:-1], pts[1:]):
            caps.append((a, b, tube, (0.0,)))
        if c["diag"] > 0.01:                         # X-kryss til naboane
            for sgn in (1.0, -1.0):
                q1 = node(lv[l + 1], sgn * per)
                pts = arc_points(p0, q1, c["bow"] * 0.5, m=7)
                for a, b in zip(pts[:-1], pts[1:]):
                    caps.append((a, b, tube * c["diag"], (0.0, -sgn * per)))

    for i, l in enumerate(lv):                       # ringar
        if c["rings"] == 2 or (c["rings"] == 1 and i in (0, len(lv) - 1)):
            tori.append((l[0], l[1], tube))

    zc = c["H"] if c["L"] > 1 else c["H"] * 0.98     # kopp + eiker
    if c.get("cup_zf", 0.0) > 0.01:
        zc = c["cup_zf"] * c["H"]
    if c["cup"] > 0.5:
        if c["spokes"]:
            top = lv[-1]
            p0 = node(top, 0.0)
            p1 = np.array([c["cup"] * 0.75 * math.cos(top[2]),
                           c["cup"] * 0.75 * math.sin(top[2]), zc])
            pts = arc_points(p0, p1, 0.0, m=3)
            for a, b in zip(pts[:-1], pts[1:]):
                caps.append((a, b, tube, (0.0,)))

    for l in lv:                                     # kuler og knoppar
        p = node(l, 0.0)
        if c["ball"] > 0.3:
            balls.append((p, c["ball"]))
        if c["nub"] > 0.3:
            e = p.copy()
            e[:2] *= (l[1] + tube * 1.25) / (l[1] + 1e-9)
            balls.append((e, c["nub"]))

    if c["mlen"] > 0.5:                              # roerfoeter med boring
        p = node(lv[0], 0.0)
        e = p[:2] / (np.linalg.norm(p[:2]) + 1e-9)
        t = math.radians(c["tilt"])
        d = np.array([e[0] * math.sin(t), e[1] * math.sin(t), -math.cos(t)])
        caps.append((p, p + d * c["mlen"], tube * 1.5, (0.0,)))
        bores.append((p + d * c["mlen"] * 0.3, d, tube * 0.85,
                      c["mlen"] * 0.9 + 6.0))

    loops = []
    if c.get("loop", 0.0) > 1.0:                     # blad/drope-loop
        e = np.array([1.0, 0.0, 0.0])
        t_hat = np.array([0.0, 1.0, 0.0])
        z_hat = np.array([0.0, 0.0, 1.0])
        ti = math.radians(c["loop_tilt"])
        N = math.cos(ti) * t_hat + math.sin(ti) * z_hat
        u1 = e.copy()
        u2 = np.cross(N, u1)
        be = math.radians(c.get("loop_lean", 0.0))   # +lean: topp mot aksen
        cb, sb = math.cos(be), math.sin(be)
        rot = np.array([[cb, 0.0, -sb], [0.0, 1.0, 0.0], [sb, 0.0, cb]])
        u1, u2, N = rot @ u1, rot @ u2, rot @ N
        C = e * c["loop_out"] + z_hat * (c["loop_zf"] * c["H"])
        loops.append((C, u1, u2, N, c["loop"], c["loop_ell"], tube))
    return caps, balls, tori, bores, loops, zc


def _seg_dist(P, a, b, r):
    ab = b - a
    t = np.clip(((P - a) @ ab) / (ab @ ab + 1e-12), 0.0, 1.0)
    q = a + t[:, None] * ab
    return np.linalg.norm(P - q, axis=1) - r


def field(P, c):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    rho = np.hypot(x, y)
    per = 2.0 * math.pi / c["n"]
    th = np.arctan2(y, x)
    thw = ((th + per / 2.0) % per) - per / 2.0        # senterbasert wrap
    caps, balls, tori, bores, loops, zc = elements(c)

    f = np.full(len(P), 1e9)
    k = c["k"]
    for zt, rt, rr in tori:
        d = np.hypot(rho - rt, z - zt) - rr
        f = smin(f, d, k)
    for off_list_geom in (caps,):
        for a, b, r, offs in off_list_geom:
            for off in offs:
                tw = thw - off
                Q = np.column_stack([rho * np.cos(tw), rho * np.sin(tw), z])
                f = smin(f, _seg_dist(Q, a, b, r), k)
    for p, r in balls:
        Q = np.column_stack([rho * np.cos(thw), rho * np.sin(thw), z])
        f = smin(f, np.linalg.norm(Q - p, axis=1) - r, k)

    for C, u1, u2, N, rl, ell, rr in loops:           # loops (ellipse-ring)
        for off in (0.0, per, -per):
            tw = thw - off
            Q = np.column_stack([rho * np.cos(tw), rho * np.sin(tw), z])
            rel = Q - C
            a1 = rel @ u1
            a2 = (rel @ u2) / ell
            h = rel @ N
            d = np.hypot(np.hypot(a1, a2) - rl, h) - rr
            f = smin(f, d, k)

    if c["cup"] > 0.5:                                # kopp med boring
        rc, hc = c["cup"], max(c["cup"] * 1.05, 16.0)
        dcyl = np.maximum(rho - rc, np.abs(z - zc) - hc / 2.0)
        f = smin(f, dcyl, k)
        dbore = np.maximum(rho - rc * 0.68, zc + hc / 2.0 - 3.0 - z)
        f = smax(f, -dbore, 1.6)

    for p, d, r, ln in bores:                         # roermunningar
        Q = np.column_stack([rho * np.cos(thw), rho * np.sin(thw), z])
        rel = Q - p
        t = rel @ d
        rad = np.linalg.norm(rel - t[:, None] * d[None, :], axis=1)
        db = np.maximum(rad - r, np.maximum(-t - 2.0, t - ln))
        f = smax(f, -db, 1.2)
    return f


# --------------------------------- polygonisering (delt med krone.py)
def split_pinches(mesh):
    import collections
    for _ in range(4):
        cnt = collections.Counter(map(tuple, mesh.edges_sorted))
        bad_edges = {kk for kk, v in cnt.items() if v > 2}
        if not bad_edges:
            break
        bad_verts = sorted({v for e in bad_edges for v in e})
        V = mesh.vertices.copy()
        F = mesh.faces.copy()
        FN = mesh.face_normals
        newV = []
        for a in bad_verts:
            fids = np.nonzero((F == a).any(axis=1))[0]
            parent = {int(fc): int(fc) for fc in fids}

            def find(xx):
                while parent[xx] != xx:
                    parent[xx] = parent[parent[xx]]
                    xx = parent[xx]
                return xx

            edge_faces = {}
            for fc in fids:
                for xx in F[fc]:
                    if xx != a:
                        e = (min(a, int(xx)), max(a, int(xx)))
                        if e not in bad_edges:
                            edge_faces.setdefault(e, []).append(int(fc))
            for fl in edge_faces.values():
                for g in fl[1:]:
                    parent[find(fl[0])] = find(g)
            comps = {}
            for fc in fids:
                comps.setdefault(find(int(fc)), []).append(int(fc))
            groups = sorted(comps.values(), key=len, reverse=True)
            for grp in groups[1:]:
                nrm = FN[grp].mean(axis=0)
                nrm /= np.linalg.norm(nrm) + 1e-12
                ia = len(V) + len(newV)
                newV.append(V[a] + 0.02 * nrm)
                for fi in grp:
                    F[fi][F[fi] == a] = ia
        if newV:
            V = np.vstack([V, np.array(newV)])
        mesh = trimesh.Trimesh(vertices=V, faces=F, process=False)
    return mesh


def bounds(c):
    lp = c.get("loop", 0.0)
    rmax = c["R"] * max(c["f_bot"], c["f_top"], 1.0 + abs(c["buk"])) \
        + c["bow"] + c["tube"] * 2.0 + c["ball"] + c["mlen"] + 10.0
    rmax = max(rmax, c.get("loop_out", 0.0) + lp * c.get("loop_ell", 1.0)
               + c["tube"] * 2.0 + 10.0)
    zmin = -(c["mlen"] + 8.0)
    if lp > 1.0:
        zmin = min(zmin, c["loop_zf"] * c["H"] - lp * c["loop_ell"]
                   - c["tube"] * 2.0 - 6.0)
    zmax = c["H"] + max(c["cup"] * 1.2, 10.0) + c["ball"] + 8.0
    if lp > 1.0:
        zmax = max(zmax, c["loop_zf"] * c["H"] + lp * c["loop_ell"]
                   + c["tube"] * 2.0 + 6.0)
    return rmax, zmin, zmax


def build(name, pitch=0.8):
    from skimage import measure
    c = VARIANTS[name]
    r_max, z_min, z_max = bounds(c)
    xs = np.arange(-r_max, r_max + pitch, pitch)
    zs = np.arange(z_min, z_max + pitch, pitch)
    nx, nz = len(xs), len(zs)
    vol = np.empty((nz, nx, nx), np.float32)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    chunk = max(1, int(5e6 // (nx * nx)))
    for i0 in range(0, nz, chunk):
        zz = zs[i0:i0 + chunk]
        P = np.column_stack([
            np.broadcast_to(X, (len(zz),) + X.shape).ravel(),
            np.broadcast_to(Y, (len(zz),) + Y.shape).ravel(),
            np.repeat(zz, X.size)])
        vol[i0:i0 + chunk] = field(P, c).reshape(len(zz), nx, nx)
    verts, faces, _, _ = measure.marching_cubes(vol, level=-0.12,
                                                spacing=(pitch,) * 3)
    verts = verts[:, [1, 2, 0]]
    verts[:, 0] -= r_max
    verts[:, 1] -= r_max
    verts[:, 2] += z_min
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    if mesh.volume < 0:
        mesh.invert()
    trimesh.smoothing.filter_taubin(mesh, lamb=0.5, nu=-0.53, iterations=6)
    try:
        if len(mesh.faces) > 240_000:
            mesh = mesh.simplify_quadric_decimation(face_count=240_000)
    except BaseException:
        pass
    comps = mesh.split(only_watertight=False)
    mesh = trimesh.util.concatenate([m for m in comps if len(m.faces) > 60])
    mesh = split_pinches(mesh)
    mesh.apply_translation([0, 0, -mesh.bounds[0][2]])
    return mesh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--pitch", type=float, default=0.8)
    args = ap.parse_args()
    os.makedirs(os.path.join(HERE, "print"), exist_ok=True)
    rows = []
    for name in VARIANTS:
        if args.only and args.only not in name:
            continue
        mesh = build(name, pitch=args.pitch)
        out = os.path.join(HERE, "print", f"grind-{name}.3mf")
        mesh.export(out)
        ext = [round(float(v), 1) for v in mesh.extents]
        vol = float(mesh.volume) / 1000.0
        rows.append((name, ext, round(vol, 1), mesh.is_watertight,
                     len(mesh.faces)))
        print(f"{name}: {ext} mm, {vol:.0f} cm3, "
              f"watertight={mesh.is_watertight}, tris={len(mesh.faces)}")
    if not rows:
        return
    rep = os.path.join(HERE, "validering-v01.md")
    with open(rep, "w") as f:
        f.write("# Grind v0.1, validering\n\n")
        f.write(f"Generert av `grind.py` (pitch {args.pitch} mm). "
                "PLA 1,24 g/cm3.\n\n")
        f.write("| variant | boks (mm) | volum (cm3) | masse (g) |"
                " vasstett | trekantar |\n|---|---|---|---|---|---|\n")
        for name, ext, vol, wt, tris in rows:
            f.write(f"| {name} | {ext[0]} x {ext[1]} x {ext[2]} | {vol} |"
                    f" {round(vol * 1.24)} | {'ja' if wt else 'NEI'} |"
                    f" {tris} |\n")
    print(f"-> {os.path.relpath(rep, HERE)}")


if __name__ == "__main__":
    main()
