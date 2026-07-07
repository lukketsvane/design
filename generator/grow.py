#!/usr/bin/env python3
"""FORMLÆRE generativ motor (v1) — frå genom til produksjonsmodell.

Ein agent-basert vekstmotor som realiserer formspråket (radial/segmentert/
bulbøs keramikk) frå eit *genom*. Genomet er ein vektor av seleksjonstrykk-
vekter — bokstavleg ein posisjon i formrommet (traktaten 1.3). Vekst =
sfære-aggregasjon under desse trykka; forma fell ut av navigasjonen
(«grown, not drawn»). Ut kjem vasstette STL-ar (produksjonsklare) + eit
kontaktark av «søsken» (stilarten som sverm, traktaten 3.3).

Bruk:
    python3 generator/grow.py --n 6 --seed 42 --out generator/out

Avhengig: numpy, scikit-image (marching cubes), trimesh (mesh + eksport),
matplotlib (render). Alt reint CPU/headless.
"""
from __future__ import annotations
import argparse, json, os, math
from dataclasses import dataclass, asdict, field
from typing import List, Tuple
import numpy as np
from skimage import measure
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ------------------------------------------------------------------ genom
@dataclass
class Genom:
    """Ein posisjon i formrommet. Kvart felt er eit seleksjonstrykk."""
    seed: int = 0
    n_buds: int = 46            # tal på sfærer som aggregerer (kompleksitet)
    symmetry: int = 6           # rotasjonssymmetri (radialt trykk)
    symmetry_break: float = 0.18  # jitter — bryt stempelet til ein sverm (3.3)
    vertical_bias: float = 0.35   # 0=kulerund (blomkål), 1=totem/søyle
    radial_bias: float = 0.55     # trong til å bulke utover (krans/skive)
    radius_start: float = 0.30    # rot-sfæreradius
    radius_falloff: float = 0.86  # barn krympar (materialminimum-trykk)
    blend: float = 0.09           # smooth-union k (kor mjukt blobane smeltar)
    iso_pad: float = 0.06         # lukk overflata → vasstett

    def label(self) -> str:
        return (f"sym{self.symmetry} vb{self.vertical_bias:.2f} "
                f"rb{self.radial_bias:.2f} n{self.n_buds}")


# --------------------------------------------------------------- aggregasjon
def grow_spheres(g: Genom) -> List[Tuple[np.ndarray, float]]:
    """Bud-vekst: start frå rota, knopp barn på foreldre-overflata i
    retningar sett av symmetri + vertikal/radial trykk. Returnerer
    (senter, radius)-liste. Dette er formgjevaren som navigerer (5.11)."""
    rng = np.random.default_rng(g.seed)
    spheres: List[Tuple[np.ndarray, float]] = [(np.zeros(3), g.radius_start)]
    for _ in range(g.n_buds - 1):
        # vel eit eksisterande foreldre (nyare får litt høgare sjanse → vekst utover)
        idx = int(rng.integers(0, len(spheres)))
        pc, pr = spheres[idx]
        # retning: kvantiser til symmetri-akse i xy, jitter, pluss vertikal drift
        k = max(1, g.symmetry)
        base = (2 * math.pi / k) * rng.integers(0, k)
        ang = base + rng.normal(0, g.symmetry_break)
        out = np.array([math.cos(ang), math.sin(ang), 0.0])
        up = np.array([0.0, 0.0, 1.0])
        d = g.radial_bias * out + g.vertical_bias * up
        d += rng.normal(0, g.symmetry_break, 3) * 0.5
        n = np.linalg.norm(d)
        d = d / n if n > 1e-9 else out
        cr = pr * g.radius_falloff
        cc = pc + d * (pr + cr) * 0.7   # barn overlappar foreldre litt → smelter
        spheres.append((cc, cr))
    return spheres


# ------------------------------------------------------------------- felt
def _smin(a: np.ndarray, b: np.ndarray, k: float) -> np.ndarray:
    """Polynomisk smooth-min: mjuk union som gjev blobb-samanvekst (metaball)."""
    if k <= 1e-6:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def build_mesh(g: Genom, res: int = 96):
    """Sfærer → signert distansefelt (smooth union) → marching cubes → mesh."""
    spheres = grow_spheres(g)
    centers = np.array([c for c, _ in spheres])
    radii = np.array([r for _, r in spheres])
    lo = (centers - radii[:, None]).min(0) - 0.15
    hi = (centers + radii[:, None]).max(0) + 0.15
    # kubisk, isotropt gitter
    span = (hi - lo).max()
    lo = (lo + hi) / 2 - span / 2
    hi = lo + span
    xs = [np.linspace(lo[i], hi[i], res) for i in range(3)]
    gx, gy, gz = np.meshgrid(*xs, indexing="ij")
    P = np.stack([gx, gy, gz], -1)          # (res,res,res,3)
    sdf = np.full((res, res, res), 1e3)
    for c, r in spheres:
        d = np.linalg.norm(P - c, axis=-1) - r
        sdf = _smin(sdf, d, g.blend)
    # lukk overflata mot gitterkanten → vasstett
    sdf[[0, -1], :, :] = g.iso_pad
    sdf[:, [0, -1], :] = g.iso_pad
    sdf[:, :, [0, -1]] = g.iso_pad
    spacing = tuple((hi - lo) / (res - 1))
    verts, faces, normals, _ = measure.marching_cubes(sdf, level=0.0, spacing=spacing)
    verts = verts + lo
    mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
    # behald største samanhengande komponent (fjern flytande øyar)
    parts = mesh.split(only_watertight=False)
    if len(parts):
        mesh = max(parts, key=lambda m: len(m.faces))
    trimesh.repair.fill_holes(mesh)
    trimesh.repair.fix_normals(mesh)
    # skaler til 180 mm høgd (produksjonsstorleik)
    ext = mesh.extents
    if ext[2] > 1e-6:
        mesh.apply_scale(180.0 / ext[2])
    mesh.apply_translation(-mesh.bounds[0])   # sett på golv
    return mesh


# ----------------------------------------------------------------- render
def render_axis(ax, mesh, title: str):
    v, f = mesh.vertices, mesh.faces
    ax.plot_trisurf(v[:, 0], v[:, 1], f, v[:, 2],
                    color="#a8c6d0", edgecolor="none",
                    linewidth=0, antialiased=True, shade=True)
    ax.set_box_aspect((1, 1, 1.4))
    try:
        ax.set_axis_off()
    except Exception:
        pass
    ax.view_init(elev=18, azim=35)
    ax.set_title(title, fontsize=7, color="#333")


# ------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=6, help="tal på søsken")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--res", type=int, default=96)
    ap.add_argument("--out", default="generator/out")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    genomes: List[Genom] = []
    for i in range(args.n):
        # sverm kring ein attraktor: varier trykka, ikkje forma direkte
        genomes.append(Genom(
            seed=int(rng.integers(0, 1_000_000)),
            n_buds=int(rng.integers(28, 60)),
            symmetry=int(rng.integers(3, 9)),
            symmetry_break=float(rng.uniform(0.08, 0.30)),
            vertical_bias=float(rng.uniform(0.15, 0.75)),
            radial_bias=float(rng.uniform(0.35, 0.75)),
            radius_falloff=float(rng.uniform(0.80, 0.92)),
            blend=float(rng.uniform(0.05, 0.13)),
        ))

    cols = min(3, args.n)
    rows = math.ceil(args.n / cols)
    fig = plt.figure(figsize=(cols * 3.2, rows * 3.4), dpi=130)
    fig.patch.set_facecolor("white")
    report = []
    for i, g in enumerate(genomes):
        mesh = build_mesh(g, res=args.res)
        stl = os.path.join(args.out, f"sibling_{i:02d}.stl")
        mesh.export(stl)
        rec = dict(index=i, stl=os.path.basename(stl), genom=asdict(g),
                   watertight=bool(mesh.is_watertight),
                   n_faces=int(len(mesh.faces)),
                   extent_mm=[round(float(x), 1) for x in mesh.extents],
                   volume_cm3=round(float(mesh.volume) / 1000.0, 1) if mesh.is_watertight else None)
        report.append(rec)
        ax = fig.add_subplot(rows, cols, i + 1, projection="3d")
        wt = "✓" if mesh.is_watertight else "✗ ope"
        render_axis(ax, mesh, f"#{i:02d} · {g.label()} · vasstett {wt}")
        print(f"[{i}] {g.label()} → {stl}  watertight={mesh.is_watertight} "
              f"faces={len(mesh.faces)} ext={rec['extent_mm']}mm")

    fig.suptitle("FORMLÆRE · generativ motor v1 — sverm av søsken frå éin grammatikk",
                 fontsize=11, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    sheet = os.path.join(args.out, "contact_sheet.png")
    fig.savefig(sheet, facecolor="white")
    with open(os.path.join(args.out, "genomes.json"), "w") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
    print(f"\nKontaktark: {sheet}\nGenom-rapport: {os.path.join(args.out,'genomes.json')}")


if __name__ == "__main__":
    main()
