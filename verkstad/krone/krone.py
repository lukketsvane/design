#!/usr/bin/env python3
"""Krone: EIN fullt parametrisert lampeskjerm, bygd som eit implisitt felt
(SDF) og polygonisert med marching cubes. Alle detaljar er mjuke unionar og
mjuke subtraksjonar i feltet, so kvar overgang smeltar saman og rundast av
(det er "merge and smoothen" som konstruksjonsprinsipp, ikkje etterarbeid).

Grammatikken er n-periodisk kring aksen: HEILE forma er definert av eitt
segment. Same parameternamn byggjer alle syskena; berre verdiane skil:

  profil     H, R_b, R_t, bulge, t     vegg som omdreiingsflate, tjukn
  krone      crown_*                   toppkanten stig i mjuke horn/toppar
  vindauge   hole_*                    stort ovalt/eggforma hol per segment
  naalehol   pins=[...]                punktklynger som slepp lys ut
  perler     beads=[...]               kuler smelta inn paa saumane
  panel      pillow, groove_*, band_z  pute-bulging og saumriller
  liner      liner=dict(...)           indre skal med eige mindre vindauge

  taarn   hoeg sylinder, tvillinghorn, hoege ovalar, liner   (ref-bilete 1)
  krans   flat 45-graders ring, mjuke toppar, eggformer      (ref-bilete 2)
  skaal   utoverflara kjegle, same regelverk, frie verdiar

Koeyr: python3 krone.py                 (alle sysken, pitch 0.8 mm)
       python3 krone.py --only krans --pitch 1.4   (rask kikk)
"""

import argparse
import math
import os
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))

VARIANTS = {
    "taarn": dict(
        n=8, H=176.0, R_b=62.0, R_t=58.0, bulge=7.0, t=5.5,
        crown_h1=27.0, crown_w1=6.0, crown_split=10.5,  # hornpar paa saumane
        crown_h2=10.0, crown_w2=4.5,                    # liten nabb paa midten
        crown_k=5.5, rim_k=2.2,
        hole_zf=0.45, hole_r0=14.0, hole_r1=14.0, hole_len=46.0, hole_k=4.0,
        pins=[dict(zf=0.86, pat="ros7", s=4.2, r=1.5, phase="c"),
              dict(zf=0.10, pat="ros19", s=4.0, r=1.5, phase="c")],
        beads=[dict(zf=0.045, r=4.2), dict(zf=0.50, r=4.2),
               dict(zf=0.79, r=4.2)],
        pillow=2.2, groove_d=1.2, groove_w=1.6, band_z=0.80,
        liner=dict(gap=13.0, t=4.0, top=0.97,
                   hole_r0=8.0, hole_r1=8.0, hole_len=30.0),
    ),
    "krans": dict(
        n=10, H=46.0, R_b=150.0, R_t=104.0, bulge=0.0, t=7.0,
        crown_h1=0.0, crown_w1=8.0, crown_split=0.0,
        crown_h2=27.0, crown_w2=17.0,                   # mjuk topp per segment
        crown_k=10.0, rim_k=3.0,
        hole_zf=0.30, hole_r0=17.0, hole_r1=9.0, hole_len=13.0, hole_k=5.5,
        pins=[dict(zf=1.24, pat="quin", s=3.4, r=1.2, phase="c")],
        beads=[dict(zf=0.13, r=5.4)],
        pillow=1.8, groove_d=1.4, groove_w=1.8, band_z=None,
        liner=None,
    ),
    "skaal": dict(
        n=12, H=92.0, R_b=56.0, R_t=112.0, bulge=0.0, t=6.0,
        crown_h1=17.0, crown_w1=8.0, crown_split=0.0,   # eitt horn per saum
        crown_h2=0.0, crown_w2=6.0,
        crown_k=7.0, rim_k=2.6,
        hole_zf=0.40, hole_r0=8.0, hole_r1=13.0, hole_len=18.0, hole_k=4.0,
        pins=[dict(zf=0.14, pat="quin", s=3.4, r=1.3, phase="c")],
        beads=[dict(zf=0.86, r=4.2)],
        pillow=1.5, groove_d=1.2, groove_w=1.7, band_z=None,
        liner=None,
    ),
}

PATTERNS = {
    "quin": lambda s: [(0, 0), (s, s), (s, -s), (-s, s), (-s, -s)],
    "ros7": lambda s: [(0, 0)] + [(s * 1.9 * math.cos(2 * math.pi * i / 6),
                                   s * 1.9 * math.sin(2 * math.pi * i / 6))
                                  for i in range(6)],
    "ros19": lambda s: ([(0, 0)]
                        + [(s * 1.8 * math.cos(2 * math.pi * i / 6),
                            s * 1.8 * math.sin(2 * math.pi * i / 6))
                           for i in range(6)]
                        + [(s * 3.4 * math.cos(2 * math.pi * (i + .5) / 12),
                            s * 3.4 * math.sin(2 * math.pi * (i + .5) / 12))
                           for i in range(12)]),
}


# ------------------------------------------------------------- feltoperasjonar
def smin(a, b, k):
    """Polynomisk mjuk minimum: union der flatene smeltar saman i radius ~k."""
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1.0 - h) + a * h - k * h * (1.0 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


# ------------------------------------------------------------------ eitt skal
def wall_field(rho, z, tc, tp, c, R_b, R_t, H, t, crown=True, deco=True):
    """Signert felt for eitt omdreiingsskal med kronekant. tc/tp er
    utbretta bogekoordinatar (mm) kring segmentsenteret og saumen."""
    u = z / H
    ub = np.clip(u, 0.0, 1.0)
    Rm = R_b + (R_t - R_b) * u + c["bulge"] * np.sin(math.pi * ub)
    slope = (R_t - R_b) / H + c["bulge"] * math.pi / H * np.cos(math.pi * ub)
    Rm = R_b + (R_t - R_b) * u + c["bulge"] * np.sin(math.pi * ub)
    if deco:
        # panelpute (bulgar mot midten) og saumriller (dropp paa saumen)
        Rm = Rm + c["pillow"] * np.cos(tc / (Rm + 1e-9) * c["n"] / 2.0) ** 2 \
             - c["groove_d"] * np.exp(-(tp / c["groove_w"]) ** 2)
        if c["band_z"] is not None:
            Rm = Rm - c["groove_d"] * np.exp(
                -((z - c["band_z"] * H) / c["groove_w"]) ** 2)
    cs = 1.0 / np.sqrt(1.0 + slope ** 2)
    g = np.abs(rho - Rm) * cs - t / 2.0

    # kronekanten: toppkanten som mjuk funksjon av vinkelen. Hornparet er
    # to gaussar kring saumen, normaliserte so toppen er h1 same kva
    # splitten er (split=0 gjev EITT horn, ikkje dobbel hoegd)
    if crown:
        norm1 = 1.0 + math.exp(-(2.0 * c["crown_split"]
                                 / c["crown_w1"]) ** 2)
        ztop = H + c["crown_h1"] / norm1 * (
            np.exp(-((tp - c["crown_split"]) / c["crown_w1"]) ** 2)
            + np.exp(-((tp + c["crown_split"]) / c["crown_w1"]) ** 2)) \
            + c["crown_h2"] * np.exp(-(tc / c["crown_w2"]) ** 2)
    else:
        ztop = H * c["liner"]["top"] if c["liner"] else H
    g = smax(g, z - ztop, c["crown_k"])
    g = smax(g, -z, c["rim_k"])
    return g, slope


def field(P, c):
    """Heile lykta som eitt signert felt, evaluert i punkta P (N, 3)."""
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    rho = np.hypot(x, y)
    th = np.arctan2(y, x)
    n = c["n"]
    per = 2.0 * math.pi / n

    def wrap(a):
        return (a + per / 2.0) % per - per / 2.0

    tc = rho * wrap(th)                    # boge fraa segmentsenter
    tp = rho * wrap(th + per / 2.0)        # boge fraa saumen

    f, slope = wall_field(rho, z, tc, tp, c,
                          c["R_b"], c["R_t"], c["H"], c["t"])
    stretch = np.sqrt(1.0 + slope ** 2)

    # stort vindauge per segment: ujamn kapsel i veggflate-koordinatar,
    # mjukt subtrahert so kanten faar den runda, "smelta" avrundinga
    zh = c["hole_zf"] * c["H"]
    m = (z - zh) * stretch
    q = np.clip(m / c["hole_len"], 0.0, 1.0)
    rq = c["hole_r0"] + (c["hole_r1"] - c["hole_r0"]) * q
    d_hole = np.hypot(tc, m - np.clip(m, 0.0, c["hole_len"])) - rq
    f = smax(f, -d_hole, c["hole_k"])

    # naalehol-klynger, skarpare subtraksjon
    for pin in c["pins"]:
        offs = PATTERNS[pin["pat"]](pin["s"])
        zp = pin["zf"] * c["H"]
        a = tc if pin["phase"] == "c" else tp
        mm_ = (z - zp) * stretch
        d = np.full_like(f, 1e9)
        for du, dv in offs:
            d = np.minimum(d, np.hypot(a - du, mm_ - dv) - pin["r"])
        f = smax(f, -d, 0.9)

    # perler paa saumane, mjukt smelta inn i veggen
    u_b = None
    for b in c["beads"]:
        zb = b["zf"] * c["H"]
        ub = zb / c["H"]
        Rmb = c["R_b"] + (c["R_t"] - c["R_b"]) * ub \
            + c["bulge"] * math.sin(math.pi * min(max(ub, 0), 1))
        d = np.sqrt(tp ** 2 + (z - zb) ** 2
                    + (rho - (Rmb + c["t"] * 0.25)) ** 2) - b["r"]
        f = smin(f, d, 2.4)

    # indre skal (liner) med eige, mindre vindauge; hard union
    if c["liner"]:
        L = c["liner"]
        cl = dict(c, t=L["t"], bulge=c["bulge"], pillow=0.0, groove_d=0.0,
                  band_z=None)
        g, sl = wall_field(rho, z, tc, tp, cl,
                           c["R_b"] - L["gap"], c["R_t"] - L["gap"],
                           c["H"], L["t"], crown=False, deco=False)
        st = np.sqrt(1.0 + sl ** 2)
        m2 = (z - zh) * st
        q2 = np.clip(m2 / L["hole_len"], 0.0, 1.0)
        rq2 = L["hole_r0"] + (L["hole_r1"] - L["hole_r0"]) * q2
        d2 = np.hypot(tc, m2 - np.clip(m2, 0.0, L["hole_len"])) - rq2
        g = smax(g, -d2, c["hole_k"] * 0.8)
        f = np.minimum(f, g)

    return f


def split_pinches(mesh):
    """MC kan la to flate-ark tangere gjennom same kant (valens 4/6).
    Solidet er lukka, men ikkje manifold. Standardgrepet: for kvart hjoerne
    paa ein slik kant, del flate-vifta rundt hjoernet i komponentar som
    berre heng saman gjennom manifolde kantar, gje kvar ekstra komponent
    sin eigen vertex-kopi, og dytt kopien 0,02 mm ut av arket."""
    import collections
    for _ in range(4):
        cnt = collections.Counter(map(tuple, mesh.edges_sorted))
        bad_edges = {k for k, v in cnt.items() if v > 2}
        if not bad_edges:
            break
        bad_verts = sorted({v for e in bad_edges for v in e})
        V = mesh.vertices.copy()
        F = mesh.faces.copy()
        FN = mesh.face_normals
        newV = []
        for a in bad_verts:
            fids = np.nonzero((F == a).any(axis=1))[0]
            # union-find over vifta: kopla gjennom manifolde kantar (a, x)
            parent = {int(f): int(f) for f in fids}

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            edge_faces = collections.defaultdict(list)
            for f in fids:
                tri = F[f]
                for x in tri:
                    if x != a:
                        e = (min(a, int(x)), max(a, int(x)))
                        if e not in bad_edges:
                            edge_faces[e].append(int(f))
            for fl in edge_faces.values():
                for g in fl[1:]:
                    parent[find(fl[0])] = find(g)
            comps = collections.defaultdict(list)
            for f in fids:
                comps[find(int(f))].append(int(f))
            groups = sorted(comps.values(), key=len, reverse=True)
            for grp in groups[1:]:            # fyrste vifta beheld a
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


# ------------------------------------------------------------------- byggjing
def build(name, pitch=0.8):
    from skimage import measure
    c = VARIANTS[name]
    zc_max = c["H"] + c["crown_h1"] + c["crown_h2"] + c["crown_k"] + 10.0
    # veggen kan lene ut over toppen (u > 1): rekn radien paa kammen med
    u_top = zc_max / c["H"]
    r_top = c["R_b"] + (c["R_t"] - c["R_b"]) * max(u_top, 1.0)
    r_max = max(c["R_b"], c["R_t"], r_top) + c["bulge"] + c["t"] + 8.0
    z_max = zc_max
    xs = np.arange(-r_max, r_max + pitch, pitch)
    zs = np.arange(-4.0, z_max + pitch, pitch)
    nx, nz = len(xs), len(zs)
    vol = np.empty((nz, nx, nx), np.float32)
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    chunk = max(1, int(6e6 // (nx * nx)))
    for i0 in range(0, nz, chunk):
        zz = zs[i0:i0 + chunk]
        P = np.column_stack([
            np.broadcast_to(X, (len(zz),) + X.shape).ravel(),
            np.broadcast_to(Y, (len(zz),) + Y.shape).ravel(),
            np.repeat(zz, X.size)])
        vol[i0:i0 + chunk] = field(P, c).reshape(len(zz), nx, nx)
    # isonivaa hakket inn i solidet: der to flater tangerer (MC-sadlar)
    # opnar gapet seg, so nettet blir manifold; forma endrar seg ~0,1 mm
    verts, faces, _, _ = measure.marching_cubes(vol, level=-0.12,
                                                spacing=(pitch, pitch, pitch))
    verts = verts[:, [1, 2, 0]]               # (z, x, y) -> (x, y, z)
    verts[:, 0] -= r_max
    verts[:, 1] -= r_max
    verts[:, 2] -= 4.0
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    if mesh.volume < 0:
        mesh.invert()
    trimesh.smoothing.filter_taubin(mesh, lamb=0.5, nu=-0.53, iterations=6)
    try:                                       # lettare fil, same form
        target = 240_000
        if len(mesh.faces) > target:
            mesh = mesh.simplify_quadric_decimation(face_count=target)
    except BaseException:
        pass
    # kast laust mikroavfall (enkelttrekantar fraa desimeringa); behald
    # dei reelle komponentane (ytre skal + ev. liner)
    comps = mesh.split(only_watertight=False)
    mesh = trimesh.util.concatenate([k for k in comps if len(k.faces) > 60])
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
        out = os.path.join(HERE, "print", f"krone-{name}.3mf")
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
        f.write("# Krone v0.1, validering\n\n")
        f.write(f"Generert av `krone.py` (pitch {args.pitch} mm). "
                "PLA 1,24 g/cm3.\n\n")
        f.write("| sysken | boks (mm) | volum (cm3) | masse (g) |"
                " vasstett | trekantar |\n|---|---|---|---|---|---|\n")
        for name, ext, vol, wt, tris in rows:
            f.write(f"| {name} | {ext[0]} x {ext[1]} x {ext[2]} | {vol} |"
                    f" {round(vol * 1.24)} | {'ja' if wt else 'NEI'} |"
                    f" {tris} |\n")
    print(f"-> {os.path.relpath(rep, HERE)}")


if __name__ == "__main__":
    main()
