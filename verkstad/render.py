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
from PIL import Image, ImageFilter, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------- look config
SIZE = 1200          # final PNG edge [px]
SS = 3               # default supersampling (render at SIZE*SS, then downscale)
SS_LAMP = 4          # lamps: extra supersampling for the fine window lace
SS_TT = 2            # turntables: lighter, they are secondary
SKAVL_ZROT = 118.0   # turn the porous windward band to a trailing accent

FILAMENT = {         # warm off-white printed plastic, per family
    "skavl": np.array([0.90, 0.88, 0.84]),
    "knagg": np.array([0.83, 0.81, 0.77]),
    "repsett": np.array([0.88, 0.55, 0.14]),   # kintsugi gold-orange (signal)
    "radial": np.array([0.66, 0.83, 0.77]),    # celadon porcelain
    "lattice": np.array([0.66, 0.83, 0.77]),   # celadon porcelain
    "lykt": np.array([0.90, 0.86, 0.78]),      # warm cream ceramic
    "krone": np.array([0.91, 0.87, 0.79]),     # warm cream ceramic
}
# families whose 3MF files are not named "{family}-{name}.3mf"
FILE_PREFIX = {"repsett": "skoeytehylse", "radial": "ribbe",
               "lattice": "lattice"}
# families whose print/ dir differs from the family name
FAMILY_DIR = {"lattice": "radial"}
# glossier sheen for the porcelain-read families
FAMILY_SHEEN = {"radial": 0.26, "lattice": 0.30, "lykt": 0.22,
                "krone": 0.20}
# families rendered with the soft porcelain studio rig + grey backdrop
PORCELAIN_FAMILIES = {"radial", "lattice", "lykt", "krone"}

# two directional lights (world direction the light TRAVELS, i.e. toward the
# object) and their radiances; no ambient term
KEY_DIR = np.array([0.42, 0.40, -0.82])     # from upper front-left
FILL_DIR = np.array([-0.78, -0.10, -0.32])  # from right, wrapping the back
KEY_I = 1.10
FILL_I = 0.62
SHEEN = 0.035        # faint Blinn sheen so edges catch a little light
SHEEN_POW = 22.0
# the light rig; families that want a different look reassign this (e.g. the
# porcelain preset below). Default is the two-light product rig.
LIGHTS = [(KEY_DIR, KEY_I), (FILL_DIR, FILL_I)]
# optional vertical grey backdrop (top_grey, bottom_grey) in 0..1; None = white
BACKDROP = None


def porcelain_lights():
    """A softer, wrapping three-light studio rig for a glossy-ceramic read:
    a broad key from upper front, two soft fills from the sides, higher fill
    ratio so shadows stay open. Returns a LIGHTS list."""
    return [(np.array([0.30, 0.55, -0.78]), 0.82),    # broad key, high front
            (np.array([-0.85, 0.10, -0.30]), 0.52),   # soft fill left
            (np.array([0.80, -0.20, -0.28]), 0.44)]   # soft fill right
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
    prefix = FILE_PREFIX.get(family, family)
    fdir = FAMILY_DIR.get(family, family)
    path = os.path.join(HERE, fdir, "print", f"{prefix}-{name}.3mf")
    mesh = trimesh.load(path, force="mesh", process=False)

    if family == "repsett":
        # couplers are modelled axis-vertical; lay them down so the product
        # shot shows the tube flank, the collar and the pinned holes
        mesh.apply_transform(trimesh.transformations.rotation_matrix(
            math.pi / 2, (1, 0, 0)))
        mesh.apply_transform(trimesh.transformations.rotation_matrix(
            math.radians(-18), (0, 0, 1)))
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
def shade(normals, view_dirs, base_rgb, sheen=None):
    """Two directional lights, no ambient, faint Blinn sheen. normals and
    view_dirs are per-sample unit vectors; returns linear RGB.

    Two-sided: the normal is flipped to face the viewer, so surfaces seen
    from behind (the inside of a hollow shade through its opening or windows)
    read as softly lit rather than pure black."""
    sheen = SHEEN if sheen is None else sheen
    n = normals * np.sign(np.sum(normals * view_dirs, axis=1))[:, None]
    col = np.zeros(n.shape[:1] + (3,))
    for i, (Ldir, I) in enumerate(LIGHTS):
        L = -Ldir / np.linalg.norm(Ldir)          # surface -> light
        ndl = np.clip(n @ L, 0.0, 1.0)
        col += (I * ndl)[:, None] * base_rgb[None, :]
        if i == 0 and sheen > 0:                   # spec off the key only
            H = L + view_dirs
            H /= np.linalg.norm(H, axis=1, keepdims=True) + 1e-9
            ndh = np.clip(np.sum(n * H, axis=1), 0.0, 1.0)
            col += (sheen * I * ndh ** SHEEN_POW)[:, None]
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
               yfov=0.42, margin=1.16, ss=None, name=None):
    ss = SS if ss is None else ss
    global LIGHTS, BACKDROP, SHEEN_POW
    saved = (LIGHTS, BACKDROP, SHEEN_POW)
    if family in PORCELAIN_FAMILIES:
        LIGHTS, BACKDROP, SHEEN_POW = porcelain_lights(), (0.90, 0.82), 12.0
    try:
        return _render_png(mesh, family, out_path, az_deg, el_deg,
                           yfov, margin, ss, name)
    finally:
        LIGHTS, BACKDROP, SHEEN_POW = saved


def lykt_inner(mesh, vpos, ncorner):
    """Interior-face mask for the lykt shades, purely geometric so every
    variant works from one rule: a corner is interior when its normal points
    toward the local core. For the torus the core is the tube's centre
    circle; for every other shell it is the solid's midpoint."""
    rxy = np.linalg.norm(mesh.vertices[:, :2], axis=1)
    b = mesh.bounds
    if rxy.min() > 0.14 * rxy.max():          # central hole: a torus
        R0 = (rxy.max() + rxy.min()) / 2.0
        zc = (b[0][2] + b[1][2]) / 2.0
        e = vpos.copy()
        e[..., 2] = 0.0
        e /= np.linalg.norm(e, axis=2, keepdims=True) + 1e-9
        tc = R0 * e
        tc[..., 2] = zc
        inward = tc - vpos
        inward /= np.linalg.norm(inward, axis=2, keepdims=True) + 1e-9
        return np.sum(ncorner * inward, axis=2) > 0.2
    cen = np.array([0.0, 0.0, (b[0][2] + b[1][2]) / 2.0])
    out = vpos - cen
    out /= np.linalg.norm(out, axis=2, keepdims=True) + 1e-9
    return np.sum(ncorner * out, axis=2) < -0.2


# taarn har ein liner (indre skal): sjoelve linerflata les som lyskjelde
# (band i radius), men gjennom liner-slisa ser ein moerkt, som i referansen
KRONE_GLOW_RHO = {"taarn": (50.0, 57.5)}


def _render_png(mesh, family, out_path, az_deg, el_deg, yfov, margin, ss,
                name=None):
    W = H = SIZE * ss
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
                FILAMENT[family], sheen=FAMILY_SHEEN.get(family)).reshape(F, 3, 3)

    if family == "skavl":
        # inner shell (normal points toward the vertical axis) glows warm, so
        # the cavity and the porous windows read as a lit source
        rad = vpos.copy()
        rad[..., 2] = 0.0
        rad /= np.linalg.norm(rad, axis=2, keepdims=True) + 1e-9
        inner = np.sum(ncorner * rad, axis=2) < -0.15
        lin[inner] = INTERIOR_EMISSIVE
    elif family == "lykt":
        lin[lykt_inner(mesh, vpos, ncorner)] = INTERIOR_EMISSIVE
    elif family == "krone":
        # inner shell glows (radial test, like skavl); the taarn liner sits
        # closest to the bulb, so the whole liner reads as the source
        rad = vpos.copy()
        rad[..., 2] = 0.0
        rad /= np.linalg.norm(rad, axis=2, keepdims=True) + 1e-9
        inner = np.sum(ncorner * rad, axis=2) < -0.15
        glow_rho = KRONE_GLOW_RHO.get(name)
        if glow_rho:
            lo, hi = glow_rho
            rr = np.linalg.norm(vpos[..., :2], axis=2)
            inner |= (rr > lo) & (rr < hi)
        lin[inner] = INTERIOR_EMISSIVE

    # backface cull (keep faces with any vertex in front of the camera)
    front = zc > 1e-6
    keep = front[mesh.faces].any(axis=1)
    color, mask = rasterise(px, depth, mesh.faces[keep], lin[keep], W, H)

    # composite: soft shadow on the backdrop, then the shaded object on top
    shadow = shadow_mask(mesh, cam, W, H, yfov)
    if BACKDROP is None:
        canvas = np.ones((H, W, 3))
    else:
        top, bot = BACKDROP
        ramp = np.linspace(top, bot, H)[:, None] * np.ones((1, W))
        canvas = np.repeat(ramp[..., None], 3, axis=2)
    canvas *= (1.0 - 0.34 * shadow[..., None])       # grey the shadow area
    srgb = np.clip(color, 0.0, 1.0) ** (1.0 / 2.2)   # gamma encode object
    canvas[mask] = srgb[mask]

    img = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8))
    img = img.resize((SIZE, SIZE), Image.LANCZOS)
    img.save(out_path)
    return out_path


# ------------------------------------------------------------------- family
# per family: strip title and the three siblings with their short labels, the
# "three siblings side by side" shot the design briefs ask for (Salone)
# key -> (title, hero-file prefix, [(hero basename tail, short label)])
FAMILY_INFO = {
    "skavl": ("Skavl, tre søsken, éin grammatikk", "skavl",
              [("a-roleg", "roleg"), ("b-open", "open"),
               ("c-asketisk", "asketisk")]),
    "knagg": ("Knagg #1, tre hypotesar, éin grammatikk", "knagg",
              [("kraftlinje", "kraftlinje"), ("kanalisert", "kanalisert"),
               ("medvite-svak", "medvite-svak")]),
    "skavl-v03": ("Skavl v0.3, tre søsken, slissar i lagretninga", "skavl",
                  [("a-roleg-v03", "roleg"), ("b-open-v03", "open"),
                   ("c-asketisk-v03", "asketisk")]),
    "repsett": ("Reparasjonssett, skøytehylse, mekanisk skøyt ikkje lim",
                "repsett",
                [("boey-d08", "bøying d8"), ("boey-d12", "bøying d12"),
                 ("torsjon-d10", "torsjon d10")]),
    "radial": ("Ribbe, radiale finnar, tre søsken", "radial",
               [("leaf", "blad"), ("vertebra", "virvel"), ("spiral", "spiral")]),
    "lattice": ("Ribbe, vove gitter med augehol, tre søsken", "lattice",
                [("coral", "korall"), ("reef", "rev"), ("column", "søyle")]),
    "lykt": ("Lykt, fem grunnformer, eitt regelverk", "lykt",
             [("kuppel", "kuppel"), ("ball", "ball"), ("krone", "krone"),
              ("smultring", "smultring"), ("terning", "terning")]),
    "krone": ("Krone, eitt parametersett, tre verdisett", "krone",
              [("taarn", "taarn"), ("krans", "krans"), ("skaal", "skaal")]),
}
# v0.3 lamp models (tall layer-direction slots), rendered via --v03
V03_MODELS = [("skavl", "a-roleg-v03"), ("skavl", "b-open-v03"),
              ("skavl", "c-asketisk-v03")]
# reparasjonssett, skoeytehylse family, rendered via --repsett
REPSETT_MODELS = [("repsett", "boey-d08"), ("repsett", "boey-d12"),
                  ("repsett", "torsjon-d10")]
# radial-fin (ribbe) family, rendered via --radial
RADIAL_MODELS = [("radial", "leaf"), ("radial", "vertebra"),
                 ("radial", "spiral")]
# lattice (woven eye-hole) family, rendered via --lattice
LATTICE_MODELS = [("lattice", "coral"), ("lattice", "reef"),
                  ("lattice", "column")]
# lykt (parametric shade grammar) family, rendered via --lykt
LYKT_MODELS = [("lykt", "kuppel"), ("lykt", "ball"), ("lykt", "krone"),
               ("lykt", "smultring"), ("lykt", "terning")]
# krone (SDF shade, one parameter set) family, rendered via --krone
KRONE_MODELS = [("krone", "taarn"), ("krone", "krans"), ("krone", "skaal")]
FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def _font(bold, size):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def build_family(family, out_dir):
    """Composite the three sibling heroes side by side on white with a title
    and per-variant labels."""
    title, prefix, variants = FAMILY_INFO[family]
    tiles = [Image.open(os.path.join(out_dir, f"{prefix}-{n}.png")).convert("RGB")
             for n, _ in variants]
    tw, th = tiles[0].size
    gap, margin, top, bottom = 36, 56, 108, 92
    ink, sub = (38, 44, 50), (120, 130, 138)
    W = len(tiles) * tw + (len(tiles) - 1) * gap + 2 * margin
    H = top + th + bottom
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(canvas)

    f_title, f_label = _font(True, 54), _font(False, 40)
    tb = d.textbbox((0, 0), title, font=f_title)
    d.text(((W - (tb[2] - tb[0])) / 2, 30), title, font=f_title, fill=ink)

    for i, (tile, (_, label)) in enumerate(zip(tiles, variants)):
        x = margin + i * (tw + gap)
        canvas.paste(tile, (x, top))
        lb = d.textbbox((0, 0), label, font=f_label)
        d.text((x + (tw - (lb[2] - lb[0])) / 2, top + th + 14),
               label, font=f_label, fill=sub)

    out = os.path.join(out_dir, f"{family}-familie.png")
    canvas.save(out)
    return out


def build_turntable(mesh, family, name, out_dir, angles=(0, 90, 180, 270)):
    """Render the model from four azimuths and tile them into one strip, so a
    single image shows the object in the round."""
    import tempfile
    tiles = []
    for az in angles:
        tmp = os.path.join(tempfile.gettempdir(), f"_tt_{family}_{name}_{az}.png")
        render_png(mesh, family, tmp, az_deg=az, ss=SS_TT)
        tiles.append(Image.open(tmp).convert("RGB"))
        os.remove(tmp)
    tw, th = tiles[0].size
    gap, margin, bottom = 24, 40, 64
    W = len(tiles) * tw + (len(tiles) - 1) * gap + 2 * margin
    canvas = Image.new("RGB", (W, th + bottom), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    f_label = _font(False, 34)
    for i, (tile, az) in enumerate(zip(tiles, angles)):
        x = margin + i * (tw + gap)
        canvas.paste(tile, (x, 0))
        lab = f"{az} grader"
        lb = d.textbbox((0, 0), lab, font=f_label)
        d.text((x + (tw - (lb[2] - lb[0])) / 2, th + 12), lab,
               font=f_label, fill=(120, 130, 138))
    out = os.path.join(out_dir, f"{family}-{name}-turntable.png")
    canvas.save(out)
    return out


# ---------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--turntable", action="store_true",
                    help="also write 4-angle turntables per model")
    ap.add_argument("--family", action="store_true",
                    help="composite the three siblings of each family side by "
                         "side (uses existing hero renders, no re-render)")
    ap.add_argument("--only", default=None, help="family/name filter")
    ap.add_argument("--ss", type=int, default=None,
                    help="override supersampling factor for hero renders")
    ap.add_argument("--v03", action="store_true",
                    help="render the v0.3 slot lamps and their family strip")
    ap.add_argument("--repsett", action="store_true",
                    help="render the reparasjonssett couplers and family strip")
    ap.add_argument("--radial", action="store_true",
                    help="render the radial-fin (ribbe) lamps and family strip")
    ap.add_argument("--lattice", action="store_true",
                    help="render the woven eye-hole lattice lamps + family")
    ap.add_argument("--lykt", action="store_true",
                    help="render the parametric lykt shades + family strip")
    ap.add_argument("--krone", action="store_true",
                    help="render the krone SDF shades + family strip")
    args = ap.parse_args()

    out_dir = os.path.join(HERE, "renders")
    os.makedirs(out_dir, exist_ok=True)

    if args.family:
        for family in FAMILY_INFO:
            try:
                out = build_family(family, out_dir)
            except FileNotFoundError:
                continue                       # heroes for this family not built
            print(f"family {family}: {os.path.relpath(out, HERE)}")
        return

    models = (V03_MODELS if args.v03 else
              REPSETT_MODELS if args.repsett else
              RADIAL_MODELS if args.radial else
              LATTICE_MODELS if args.lattice else
              LYKT_MODELS if args.lykt else
              KRONE_MODELS if args.krone else MODELS)
    for family, name in models:
        if args.only and args.only not in f"{family}/{name}":
            continue
        mesh = load_oriented(family, name)
        if args.turntable:
            # turntables only; heroes already exist from a plain run
            out = build_turntable(mesh, family, name, out_dir)
            print(f"turntable {family}-{name}: {os.path.relpath(out, HERE)}")
            continue
        hero = os.path.join(out_dir, f"{family}-{name}.png")
        # lamps carry a fine porous window band; give them extra supersampling
        # so the lace resolves cleanly instead of blocky
        ss = args.ss if args.ss else (SS_LAMP if family == "skavl" else SS)
        el = 5 if family in PORCELAIN_FAMILIES else 16   # eye-level porcelain
        if name in ("krans", "skaal"):
            el = 14                          # flate formar: litt ovanfraa
        render_png(mesh, family, hero, ss=ss, el_deg=el, name=name)
        print(f"hero  {family}-{name}: {os.path.relpath(hero, HERE)} (ss={ss})")

    if args.v03:
        out = build_family("skavl-v03", out_dir)
        print(f"family skavl-v03: {os.path.relpath(out, HERE)}")
    if args.repsett:
        out = build_family("repsett", out_dir)
        print(f"family repsett: {os.path.relpath(out, HERE)}")
    if args.radial:
        out = build_family("radial", out_dir)
        print(f"family radial: {os.path.relpath(out, HERE)}")
    if args.lattice:
        out = build_family("lattice", out_dir)
        print(f"family lattice: {os.path.relpath(out, HERE)}")
    if args.lykt:
        out = build_family("lykt", out_dir)
        print(f"family lykt: {os.path.relpath(out, HERE)}")
    if args.krone:
        out = build_family("krone", out_dir)
        print(f"family krone: {os.path.relpath(out, HERE)}")


if __name__ == "__main__":
    main()
