#!/usr/bin/env python3
"""Studio renderer for the Verkstad solids: takes the watertight 3MF the
generators emit and produces clean product PNGs on seamless white with two
directional lights and no ambient or environment fill, plus a soft grounding
shadow. Self-contained NumPy z-buffer rasteriser, so it needs no system GL
and runs anywhere the generators run (CI, the daily loop).

Why a software renderer: the headless GL stack (OSMesa) here renders only
specular reflections, not diffuse, so every matte surface came out black.
A small correct rasteriser sidesteps that and gives exact control over the
brief: two directional lights, no ambient, white background.

The look (deliberately neutral, jf. traktat 2.1: the form carries, not the
styling):
  - two directional lights only, no ambient: a strong key from upper
    front-left and a softer fill from front-right that opens the shadow
    side without flattening it;
  - matte filament shading (Lambert + a faint sheen) in a warm off-white,
    the read of printed PLA/PETG;
  - pure white canvas with a soft contact shadow projected under the object,
    so it sits on a surface without any visible horizon;
  - supersampled then downscaled (LANCZOS) for clean edges.

Each object is oriented to its natural read: the lamp sits on its collar,
the hook stands in wall-mounted use pose.

Run:  python3 render.py                 (hero view of every model)
      python3 render.py --turntable     (also 4-angle turntables)
      python3 render.py --only knagg     (filter by family/name)
"""

import os
import math
import argparse
import numpy as np
import trimesh
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------- look config
SIZE = 1200          # final PNG edge [px]
SS = 3               # supersampling factor (render at SIZE*SS, then downscale)
SKAVL_ZROT = 118.0   # turn the porous windward band to a trailing accent

FILAMENT = {         # warm off-white printed plastic, per family
    "skavl": np.array([0.90, 0.88, 0.84]),
    "knagg": np.array([0.83, 0.81, 0.77]),
}

# two directional lights (world direction the light TRAVELS, i.e. toward the
# object) and their radiances; no ambient term
KEY_DIR = np.array([0.42, 0.40, -0.82])     # from upper front-left
FILL_DIR = np.array([-0.78, -0.10, -0.32])  # from right, wrapping the back
KEY_I = 1.10
FILL_I = 0.62
SHEEN = 0.035        # faint Blinn sheen so edges catch a little light
SHEEN_POW = 22.0
SMOOTH_COS = 0.83    # crease threshold (~34 deg): flatter corners stay flat

# warm interior glow for the lamp: the inner shell reads as a lit source, so
# the porous windward band and the top opening glow instead of going black
# (linear RGB; gamma-encoded with the rest). Only applied to skavl.
INTERIOR_EMISSIVE = np.array([0.99, 0.90, 0.74])

MODELS = [
    ("skavl", "a-roleg"),
    ("skavl", "b-open"),
    ("skavl", "c-asketisk"),
    ("knagg", "kraftlinje"),
    ("knagg", "kanalisert"),
    ("knagg", "medvite-svak"),
]


# ------------------------------------------------------------------- loading
def load_oriented(family, name):
    """Load the 3MF and rotate it into presentation orientation, resting on
    the floor plane z = 0, centred over the origin in x and y."""
    path = os.path.join(HERE, family, "print", f"{family}-{name}.3mf")
    mesh = trimesh.load(path, force="mesh", process=False)

    if family == "knagg":
        # generators export the hook lying on its side for printing; undo
        # that so it stands in wall-mounted use pose (plate vertical, arm
        # out toward +x, hook curling up +z)
        mesh.apply_transform(trimesh.transformations.rotation_matrix(
            -math.pi / 2, (1, 0, 0)))
        mesh.apply_transform(trimesh.transformations.rotation_matrix(
            math.pi, (0, 0, 1)))
    elif family == "skavl":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(
            math.radians(SKAVL_ZROT), (0, 0, 1)))

    b = mesh.bounds
    mesh.apply_translation([-(b[0][0] + b[1][0]) / 2.0,
                            -(b[0][1] + b[1][1]) / 2.0,
                            -b[0][2]])
    return mesh


# -------------------------------------------------------------------- camera
def camera_basis(eye, target, up=(0, 0, 1)):
    eye = np.asarray(eye, float)
    target = np.asarray(target, float)
    f = target - eye
    f /= np.linalg.norm(f)
    up = np.asarray(up, float)
    s = np.cross(f, up)
    s /= np.linalg.norm(s)
    u = np.cross(s, f)
    return eye, f, s, u


def place_camera(mesh, az_deg, el_deg, yfov, margin):
    b = mesh.bounds
    centre = np.array([0.0, 0.0, (b[0][2] + b[1][2]) / 2.0])
    radius = float(np.linalg.norm(b[1] - b[0])) / 2.0
    dist = radius * margin / math.tan(yfov / 2.0)
    az, el = math.radians(az_deg), math.radians(el_deg)
    eye = centre + dist * np.array([
        math.cos(el) * math.cos(az),
        math.cos(el) * math.sin(az),
        math.sin(el)])
    return camera_basis(eye, centre), centre, dist


def project(points, cam, W, H, yfov):
    """World -> pixel coords + view-space depth (positive in front)."""
    eye, f, s, u = cam
    rel = points - eye
    xc = rel @ s
    yc = rel @ u
    zc = rel @ f                      # positive in front of the camera
    depth = np.maximum(zc, 1e-6)
    ty = math.tan(yfov / 2.0)
    tx = ty * (W / H)
    ndc_x = (xc / depth) / tx
    ndc_y = (yc / depth) / ty
    px = (ndc_x * 0.5 + 0.5) * W
    py = (1.0 - (ndc_y * 0.5 + 0.5)) * H
    return np.stack([px, py], axis=1), depth, zc


# ---------------------------------------------------------------- shading
def shade(normals, view_dirs, base_rgb):
    """Two directional lights, no ambient, faint Blinn sheen. normals and
    view_dirs are per-sample unit vectors; returns linear RGB.

    Two-sided: the normal is flipped to face the viewer, so surfaces seen
    from behind (the inside of a hollow shade through its opening or windows)
    read as softly lit rather than pure black."""
    n = normals * np.sign(np.sum(normals * view_dirs, axis=1))[:, None]
    col = np.zeros(n.shape[:1] + (3,))
    for Ldir, I in ((KEY_DIR, KEY_I), (FILL_DIR, FILL_I)):
        L = -Ldir / np.linalg.norm(Ldir)          # surface -> light
        ndl = np.clip(n @ L, 0.0, 1.0)
        col += (I * ndl)[:, None] * base_rgb[None, :]
        if I == KEY_I and SHEEN > 0:
            H = L + view_dirs
            H /= np.linalg.norm(H, axis=1, keepdims=True) + 1e-9
            ndh = np.clip(np.sum(n * H, axis=1), 0.0, 1.0)
            col += (SHEEN * I * ndh ** SHEEN_POW)[:, None]
    return col


# --------------------------------------------------------------- rasteriser
def rasterise(px, depth, tris, attrc, W, H):
    """Z-buffered barycentric rasteriser. `attrc` is a per-face-corner
    (F, 3, C) array interpolated perspective-correctly; returns (C-channel
    image, mask)."""
    C = attrc.shape[2]
    zbuf = np.full((H, W), np.inf)
    out = np.zeros((H, W, C))
    mask = np.zeros((H, W), bool)
    inv_w = 1.0 / depth                     # perspective-correct weight

    p = px
    for fi in range(len(tris)):
        a, b, c = tris[fi]
        xa, ya = p[a]; xb, yb = p[b]; xc, yc = p[c]
        minx = max(int(math.floor(min(xa, xb, xc))), 0)
        maxx = min(int(math.ceil(max(xa, xb, xc))), W - 1)
        miny = max(int(math.floor(min(ya, yb, yc))), 0)
        maxy = min(int(math.ceil(max(ya, yb, yc))), H - 1)
        if minx > maxx or miny > maxy:
            continue
        area = (xb - xa) * (yc - ya) - (xc - xa) * (yb - ya)
        if area == 0:
            continue
        ys, xs = np.mgrid[miny:maxy + 1, minx:maxx + 1]
        xs = xs + 0.5
        ys = ys + 0.5
        w0 = ((xb - xs) * (yc - ys) - (xc - xs) * (yb - ys)) / area
        w1 = ((xc - xs) * (ya - ys) - (xa - xs) * (yc - ys)) / area
        w2 = 1.0 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue
        iw = w0 * inv_w[a] + w1 * inv_w[b] + w2 * inv_w[c]
        z = 1.0 / iw
        sub = zbuf[miny:maxy + 1, minx:maxx + 1]
        take = inside & (z < sub)
        if not take.any():
            continue
        aa, ab, ac = attrc[fi]
        num = (w0[..., None] * (aa * inv_w[a])
               + w1[..., None] * (ab * inv_w[b])
               + w2[..., None] * (ac * inv_w[c]))
        val = num / iw[..., None]
        ysi, xsi = np.nonzero(take)
        gy = ysi + miny
        gx = xsi + minx
        zbuf[gy, gx] = z[take]
        out[gy, gx] = val[take]
        mask[gy, gx] = True
    return out, mask


def corner_normals(mesh):
    """Crease-aware per-face-corner normals: use the smoothed vertex normal
    where the surface is smooth, the face normal where a corner sits on a
    crease. Gives flat faces on the plate and smooth curves on the saddle
    and shade from one code path."""
    fn = np.asarray(mesh.face_normals)
    vn = np.asarray(mesh.vertex_normals)
    faces = mesh.faces
    vnc = vn[faces]                                  # (F, 3, 3)
    fnc = np.repeat(fn[:, None, :], 3, axis=1)       # (F, 3, 3)
    dot = np.sum(vnc * fnc, axis=2)                  # (F, 3)
    smooth = dot > SMOOTH_COS
    return np.where(smooth[..., None], vnc, fnc)


# ------------------------------------------------------------------ shadow
def shadow_mask(mesh, cam, W, H, yfov):
    """Soft contact shadow: drop every vertex onto z = 0 along the key light
    direction, rasterise the flattened solid, blur it."""
    Ld = KEY_DIR / np.linalg.norm(KEY_DIR)
    V = mesh.vertices.copy()
    t = V[:, 2] / (-Ld[2])                       # Ld[2] < 0
    feet = V - t[:, None] * Ld
    feet[:, 2] = 0.0
    px, depth, _ = project(feet, cam, W, H, yfov)
    _, m = rasterise(px, depth, mesh.faces,
                     np.ones((len(mesh.faces), 3, 1)), W, H)
    img = Image.fromarray((m * 255).astype(np.uint8))
    img = img.filter(ImageFilter.GaussianBlur(radius=W * 0.010))
    return np.asarray(img, float) / 255.0


# -------------------------------------------------------------------- render
def render_png(mesh, family, out_path, az_deg=38, el_deg=16,
               yfov=0.42, margin=1.16):
    W = H = SIZE * SS
    cam, centre, dist = place_camera(mesh, az_deg, el_deg, yfov, margin)
    eye = cam[0]

    px, depth, zc = project(mesh.vertices, cam, W, H, yfov)

    # crease-aware per-corner normals and view directions
    ncorner = corner_normals(mesh)                   # (F, 3, 3)
    vpos = mesh.vertices[mesh.faces]                 # (F, 3, 3)
    view = eye - vpos
    view /= np.linalg.norm(view, axis=2, keepdims=True) + 1e-9
    F = len(mesh.faces)
    lin = shade(ncorner.reshape(-1, 3), view.reshape(-1, 3),
                FILAMENT[family]).reshape(F, 3, 3)

    if family == "skavl":
        # inner shell (normal points toward the vertical axis) glows warm, so
        # the cavity and the porous windows read as a lit source
        rad = vpos.copy()
        rad[..., 2] = 0.0
        rad /= np.linalg.norm(rad, axis=2, keepdims=True) + 1e-9
        inner = np.sum(ncorner * rad, axis=2) < -0.15
        lin[inner] = INTERIOR_EMISSIVE

    # backface cull (keep faces with any vertex in front of the camera)
    front = zc > 1e-6
    keep = front[mesh.faces].any(axis=1)
    color, mask = rasterise(px, depth, mesh.faces[keep], lin[keep], W, H)

    # composite: soft shadow on white, then the shaded object on top
    shadow = shadow_mask(mesh, cam, W, H, yfov)
    canvas = np.ones((H, W, 3))
    canvas *= (1.0 - 0.34 * shadow[..., None])       # grey the shadow area
    srgb = np.clip(color, 0.0, 1.0) ** (1.0 / 2.2)   # gamma encode object
    canvas[mask] = srgb[mask]

    img = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8))
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    img.save(out_path)
    return out_path


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--turntable", action="store_true",
                    help="also write 4-angle turntables per model")
    ap.add_argument("--only", default=None, help="family/name filter")
    args = ap.parse_args()

    out_dir = os.path.join(HERE, "renders")
    os.makedirs(out_dir, exist_ok=True)

    for family, name in MODELS:
        if args.only and args.only not in f"{family}/{name}":
            continue
        mesh = load_oriented(family, name)
        hero = os.path.join(out_dir, f"{family}-{name}.png")
        render_png(mesh, family, hero)
        print(f"hero  {family}-{name}: {os.path.relpath(hero, HERE)}")
        if args.turntable:
            for k, az in enumerate((20, 110, 200, 290)):
                p = os.path.join(out_dir, f"{family}-{name}-tt{k}.png")
                render_png(mesh, family, p, az_deg=az)
                print(f"  tt{k} az={az}")


if __name__ == "__main__":
    main()
