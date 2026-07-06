#!/usr/bin/env python3
"""Skavl lamp shade generator v0.2, from pseudocode (briefs/skavl-algoritme.md)
to watertight, printable geometry.

Architecture: curve stack as a radius field r(theta, z) on a cylinder grid.
Each ring inherits the ring below (a "snowfall"), grows by seeded noise
weighted by the wind field (lee = smooth/tight, windward = porous/open),
and is then projected through hard clamps: overhang budget, thermal floor,
format box. Windows are cut on the windward side as grid cells removed from
the solid, with bridge (<= 8 mm) and web (>= 3 mm) budgets enforced by
construction. The solid is lofted with wall thickness t_vegg and exported
as 3MF + a validation report.

v0.2 simplifications vs. the pseudocode (documented in README.md):
- rings are star-shaped (r as function of theta) => self-intersection is
  impossible by construction, so the repulsion term (F_fraastoyt) drops out;
- a base-profile guidance term is added so the family has lamp proportions
  instead of drifting to the format box;
- glare is handled by construction: no window cell may have a straight
  line from the LED centre at an elevation angle within the glare band.

Run:  python3 skavl.py            (writes print/*.3mf, validering-v0.2.md,
                                   silhuett-v0.2.svg)
"""

import math
import numpy as np
import trimesh

# ---------------------------------------------------------------- parameters
# Names follow the parameter table in briefs/skavl-algoritme.md.
N_LAG = 120          # rings above ring 0 (2 mm each -> 240 mm tall)
DZ = 2.0             # ring spacing [mm]
M = 240              # theta samples per ring (cell ~2.1 mm wide at r=80)
DT = 0.3             # growth step length
W_VEKST = 1.0        # growth weight
W_GLATT = 0.4        # smoothing weight (increased on the lee side)
POROS_GAIN = 1.6     # windward growth gain
GLATT_GAIN = 0.5     # lee growth gain
W_BLEND = 0.8        # inward tip inside the glare band [mm/step]
W_PROFIL = 0.5       # pull toward the base profile (v0.2 addition)
THETA_LE = 0.0       # where the lee side faces [rad]
R_SOKKEL = 22.3      # E27 collar radius incl. +0.3 mm tolerance [mm]
COLLAR_RINGS = 4     # rings pinned to the collar radius
R_MIN, R_MAKS = 35.0, 110.0   # format box [mm]
Z_LED = 130.0        # LED (bulb) centre height [mm]
LED_BAND = (85.0, 175.0)      # thermal band around the source [mm]
R_TERM_FLOOR = 70.0  # bulb radius ~30 mm + 40 mm clearance [mm]
T_VEGG = 1.0         # wall thickness [mm]
OVERHENG_DEG = 50.0  # print overhang budget
DRIFT_MAX = DZ * math.tan(math.radians(45.0))  # radial drift/ring, 5 deg margin
BRU_MAKS = 8.0       # max unsupported window span [mm]
WEB_MIN = 3.0        # min material between windows [mm]
VIND_TERSKEL = -0.15 # windows only where vind(theta) < this
GLARE_BAND_DEG = (-5.0, 60.0)   # LED-ray elevation band with no windows
BLEND_TIP_DEG = (-5.0, 35.0)    # elevation band where the wall tips inward
RIM_RINGS = 4        # closed cell rows at bottom and top
PLA_DENSITY = 1.24e-3           # g/mm^3
PETG_DENSITY = 1.27e-3          # g/mm^3, PETG-vurderinga i brief v1.1

SIBLINGS = {
    # per pseudocode section 5: three weightings, one grammar
    "a-roleg":    dict(seed=11, amp=0.8, p_terskel=0.62, bulge=92.0, w_glatt=0.5),
    "b-open":     dict(seed=23, amp=1.1, p_terskel=0.48, bulge=92.0, w_glatt=0.4),
    "c-asketisk": dict(seed=37, amp=0.6, p_terskel=0.55, bulge=80.0, w_glatt=0.45),
}

THETA = np.arange(M) * 2.0 * math.pi / M
VIND = np.cos(THETA - THETA_LE)          # 1 = lee, -1 = windward
LE_T = (VIND + 1.0) / 2.0                # 0 = windward, 1 = lee


# ------------------------------------------------------------------- fields
def make_noise(seed, K=24, n_lo=2, n_hi=14, lam_lo=30.0, lam_hi=160.0):
    """Seeded harmonic noise on the cylinder: periodic in theta, smooth in z,
    std ~ 1. A sum of random-phase cosines stands in for simplex noise."""
    rng = np.random.default_rng(seed)
    n = rng.integers(n_lo, n_hi + 1, K)
    lam = rng.uniform(lam_lo, lam_hi, K)
    phi = rng.uniform(0, 2 * math.pi, K)
    psi = rng.uniform(0, 2 * math.pi, K)
    a = 1.0 / np.sqrt(n)
    a *= 2.0 / math.sqrt(np.sum(a * a))   # sum of term variances a^2/4 -> std 1

    def noise(theta, z):
        th = np.asarray(theta)[..., None]
        zz = np.asarray(z if np.ndim(z) else [z])[..., None]
        val = a * np.cos(n * th + phi) * np.cos(2 * math.pi * zz / lam + psi)
        return np.clip(val.sum(axis=-1), -2.0, 2.0)

    return noise


def smoothstep(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def r_base(z, bulge):
    """Designed base silhouette: collar -> bulge at the LED -> taper."""
    return (R_SOKKEL
            + (bulge - R_SOKKEL) * smoothstep(z, 6.0, 140.0)
            - 30.0 * smoothstep(z, 160.0, 240.0))


def r_floor(z):
    """Hard radial floor: format minimum ramped up from the collar, plus the
    thermal floor around the LED band. Ramped at the drift-clamp slope
    (45 deg) so the floor can never force a violation of the drift clamp,
    which is applied before it."""
    ramp = DRIFT_MAX / DZ
    f_min = min(R_MIN, R_SOKKEL + max(0.0, z - COLLAR_RINGS * DZ) * ramp)
    dist = max(0.0, LED_BAND[0] - z, z - LED_BAND[1])
    f_led = R_TERM_FLOOR - ramp * dist
    return max(R_SOKKEL, f_min, f_led)


def elevation_deg(z, r):
    """Elevation angle of the straight ray from the LED centre out through a
    point on the wall at height z, radius r."""
    return np.degrees(np.arctan2(z - Z_LED, r))


def cell_radius(r):
    """Mean radius per cell (between rings i,i+1 and theta j,j+1), the one
    radius definition shared by mask generation and validation."""
    return 0.25 * (r[:-1, :] + r[1:, :]
                   + np.roll(r[:-1, :], -1, axis=1)
                   + np.roll(r[1:, :], -1, axis=1))


# ------------------------------------------------------------------- growth
def grow(cfg):
    """Evolve the radius field ring by ring (pseudocode steps 1-3)."""
    noise = make_noise(cfg["seed"])
    r = np.zeros((N_LAG + 1, M))
    r[0, :] = R_SOKKEL
    gain = POROS_GAIN + (GLATT_GAIN - POROS_GAIN) * LE_T   # lerp
    k_smooth = cfg["w_glatt"] * (0.5 + LE_T)               # smooth lee harder

    for i in range(1, N_LAG + 1):
        z = i * DZ
        prev = r[i - 1, :]
        if i <= COLLAR_RINGS:
            r[i, :] = R_SOKKEL
            continue
        # 1 - growth
        f_vekst = W_VEKST * cfg["amp"] * noise(THETA, z) * gain
        # 2 - pressure weighting
        f_profil = np.clip(W_PROFIL * (r_base(z, cfg["bulge"]) - prev), -4.0, 4.0)
        elev = elevation_deg(z, float(np.mean(prev)))
        f_blend = -W_BLEND if BLEND_TIP_DEG[0] <= elev <= BLEND_TIP_DEG[1] else 0.0
        cand = prev + DT * (f_vekst + f_profil + f_blend)
        # smoothing along the ring (F_glatt)
        for _ in range(2):
            lap = 0.5 * (np.roll(cand, 1) + np.roll(cand, -1)) - cand
            cand = cand + k_smooth * lap
        # 3 - hard clamps (projections, never penalties)
        cand = np.clip(cand, prev - DRIFT_MAX, prev + DRIFT_MAX)  # print physics
        floor_i = r_floor(z)
        cand = np.clip(cand, floor_i, R_MAKS)                     # term + format
        r[i, :] = cand
    return r


# ------------------------------------------------------------------ windows
def window_mask(r, cfg):
    """Open cells on the windward side (pseudocode step 4). A cell sits
    between rings i,i+1 and theta samples j,j+1."""
    wnoise = make_noise(cfg["seed"] + 1000, K=30, n_lo=5, n_hi=22,
                        lam_lo=10.0, lam_hi=40.0)
    open_mask = np.zeros((N_LAG, M), dtype=bool)
    z_c = (np.arange(N_LAG) + 0.5) * DZ
    th_c = (np.arange(M) + 0.5) * 2.0 * math.pi / M
    vind_c = np.cos(th_c - THETA_LE)
    r_c = cell_radius(r)

    for i in range(RIM_RINGS, N_LAG - RIM_RINGS):
        elev = elevation_deg(z_c[i], r_c[i, :])
        glare = ((elev >= GLARE_BAND_DEG[0] - 1.5)
                 & (elev <= GLARE_BAND_DEG[1] + 1.5))   # 1.5 deg margin
        want = ((vind_c < VIND_TERSKEL) & ~glare
                & (wnoise(th_c, z_c[i]) > cfg["p_terskel"]))
        open_mask[i, :] = want

    # enforce bridge (<= BRU_MAKS) and web (>= WEB_MIN) budgets per row,
    # using the cell width at that row's mean radius
    for i in range(N_LAG):
        row = open_mask[i, :]
        if not row.any():
            continue
        r_ci = cell_radius(r)[i, :]
        cellw_max = 2.0 * math.pi * float(r_ci.max()) / M
        cellw_min = 2.0 * math.pi * float(r_ci.min()) / M
        max_run = max(1, int(BRU_MAKS // cellw_max))   # conservative both ways
        min_gap = max(1, math.ceil(WEB_MIN / cellw_min))
        closed = np.flatnonzero(~row)
        start = int(closed[0])   # windward side is ~half the circle: exists
        new = np.zeros(M, dtype=bool)
        run, gap = 0, min_gap
        for k in range(M):
            j = (start + k) % M
            if row[j] and run < max_run and (run > 0 or gap >= min_gap):
                new[j] = True
                run += 1
                gap = 0
            else:
                run = 0
                gap += 1
        open_mask[i, :] = new
    # vertical stiffness: cap window height at 6 cells (12 mm) with 2-cell webs
    for j in range(M):
        col = open_mask[:, j]
        run, gap = 0, 99
        for i in range(N_LAG):
            if col[i] and run < 6 and (run > 0 or gap >= 2):
                run += 1
                gap = 0
            else:
                col[i] = False
                gap += 1
                run = 0
    # no diagonal window contact: two cavities meeting only at a corner make
    # a non-manifold pinch (and a stress point); close the upper cell
    for i in range(1, N_LAG):
        for j in range(M):
            if not open_mask[i, j]:
                continue
            for dj in (-1, 1):
                if (open_mask[i - 1, (j + dj) % M]
                        and not open_mask[i - 1, j]
                        and not open_mask[i, (j + dj) % M]):
                    open_mask[i, j] = False
                    break
    return open_mask


# --------------------------------------------------------------------- mesh
def build_mesh(r, open_mask):
    """Loft the two offset surfaces and stitch rims + window borders into one
    watertight solid (pseudocode 'loft + tjukkleik + kutt')."""
    cos, sin = np.cos(THETA), np.sin(THETA)
    z = np.arange(N_LAG + 1)[:, None] * DZ
    r_out, r_in = r + T_VEGG / 2.0, r - T_VEGG / 2.0
    n_grid = (N_LAG + 1) * M

    def verts(rr):
        return np.stack([rr * cos, rr * sin,
                         np.broadcast_to(z, rr.shape)], axis=-1).reshape(-1, 3)

    V = np.vstack([verts(r_out), verts(r_in)])   # outer grid, then inner grid

    def vo(i, j):
        return i * M + (j % M)

    def vi(i, j):
        return n_grid + i * M + (j % M)

    faces, tags = [], []

    def quad(a, b, c, d, tag):
        faces.append((a, b, c))
        faces.append((a, c, d))
        tags.append(tag)
        tags.append(tag)

    for i in range(N_LAG):
        for j in range(M):
            if open_mask[i, j]:
                continue
            # outer surface, CCW seen from outside
            quad(vo(i, j), vo(i, j + 1), vo(i + 1, j + 1), vo(i + 1, j), "out")
            # inner surface, reversed
            quad(vi(i, j), vi(i + 1, j), vi(i + 1, j + 1), vi(i, j + 1), "in")
    for j in range(M):   # rims
        quad(vo(0, j), vi(0, j), vi(0, j + 1), vo(0, j + 1), "rim")
        quad(vo(N_LAG, j), vo(N_LAG, j + 1), vi(N_LAG, j + 1), vi(N_LAG, j), "rim")
    # window borders: wall wherever an open cell meets a closed cell
    for i in range(N_LAG):
        for j in range(M):
            if not open_mask[i, j]:
                continue
            if not open_mask[i, (j - 1) % M]:   # closed neighbour left
                quad(vo(i, j), vo(i + 1, j), vi(i + 1, j), vi(i, j), "web")
            if not open_mask[i, (j + 1) % M]:   # right
                quad(vo(i, j + 1), vi(i, j + 1), vi(i + 1, j + 1), vo(i + 1, j + 1), "web")
            if i == 0 or not open_mask[i - 1, j]:   # below
                quad(vo(i, j), vi(i, j), vi(i, j + 1), vo(i, j + 1), "web")
            if i == N_LAG - 1 or not open_mask[i + 1, j]:   # above (bridge)
                quad(vo(i + 1, j), vo(i + 1, j + 1), vi(i + 1, j + 1), vi(i + 1, j), "web")

    mesh = trimesh.Trimesh(vertices=V, faces=np.array(faces), process=False)
    mesh.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(mesh)   # consistent outward winding
    return mesh, np.array(tags)


# --------------------------------------------------------------- validation
def validate(name, r, open_mask, mesh, tags):
    """Pseudocode step 6: the numbers before any print."""
    rep = {"namn": name}
    rep["vasstett"] = bool(mesh.is_watertight)
    rep["volum_mm3"] = float(mesh.volume)
    rep["masse_g"] = float(mesh.volume) * PLA_DENSITY
    rep["masse_petg_g"] = float(mesh.volume) * PETG_DENSITY
    rep["trekantar"] = len(mesh.faces)

    # overhang on the shell surfaces only (window tops are budgeted bridges)
    shell = np.isin(tags, ("out", "in"))
    nz = mesh.face_normals[shell][:, 2]
    down = np.clip(-nz, 0.0, 1.0)
    ang = np.degrees(np.arcsin(down))
    areas = mesh.area_faces[shell]
    rep["overheng_maks"] = float(ang.max())
    rep["overheng_p95"] = float(np.percentile(ang[ang > 0], 95)) if (ang > 0).any() else 0.0
    rep["overheng_brot_areal_pst"] = float(
        areas[ang > OVERHENG_DEG].sum() / areas.sum() * 100.0)

    # windows: area, spans, glare band check
    z_c = (np.arange(N_LAG) + 0.5) * DZ
    r_c = cell_radius(r)
    n_open = int(open_mask.sum())
    cell_areas, max_span, glare_hits = [], 0.0, 0
    for i in range(N_LAG):
        row = open_mask[i, :]
        if not row.any():
            continue
        cellw = 2.0 * math.pi * r_c[i, :] / M
        cell_areas.append(float((cellw * DZ)[row].sum()))
        # spans (with wrap): longest open run * local cell width
        ext = np.concatenate([row, row])
        best = run = 0
        for v in ext[:2 * M - 1]:
            run = run + 1 if v else 0
            best = max(best, run)
        max_span = max(max_span, min(best, M) * float(cellw[row].max()))
        elev = elevation_deg(z_c[i], r_c[i, :])
        glare_hits += int(np.count_nonzero(
            row & (elev >= GLARE_BAND_DEG[0]) & (elev <= GLARE_BAND_DEG[1])))
    rep["vindauge_n_celler"] = n_open
    rep["opningsareal_mm2"] = float(sum(cell_areas))
    lo_area = float((np.pi * 2 * r.mean() * N_LAG * DZ) * 0.5)
    rep["opningsgrad_lo_pst"] = rep["opningsareal_mm2"] / lo_area * 100.0
    rep["bru_maks_mm"] = float(max_span)
    rep["blendceller"] = glare_hits
    rep["r_maks_mm"] = float(r.max())
    rep["hogd_mm"] = float(N_LAG * DZ)
    return rep


def silhouette_svg(results, path):
    """Side elevation of the three siblings, windward side to the left."""
    W, H, pad = 940, 340, 30
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
             f'font-family="sans-serif" font-size="13">',
             f'<rect width="{W}" height="{H}" fill="white"/>']
    for k, (name, r, open_mask) in enumerate(results):
        ox = pad + 120 + k * 300
        oy = H - pad

        def pt(x, zz):
            return f"{ox + x:.1f},{oy - zz:.1f}"

        x = r * np.cos(THETA)[None, :]
        y = r * np.sin(THETA)[None, :]
        xmin, xmax = x.min(axis=1), x.max(axis=1)
        zs = np.arange(N_LAG + 1) * DZ
        right = [pt(xmax[i], zs[i]) for i in range(N_LAG + 1)]
        left = [pt(xmin[i], zs[i]) for i in reversed(range(N_LAG + 1))]
        parts.append('<polygon points="' + " ".join(right + left)
                     + '" fill="#eceff1" stroke="#37474f" stroke-width="1.2"/>')
        for i in range(0, N_LAG + 1, 5):   # layer texture
            parts.append(f'<line x1="{ox + xmin[i]:.1f}" y1="{oy - zs[i]:.1f}" '
                         f'x2="{ox + xmax[i]:.1f}" y2="{oy - zs[i]:.1f}" '
                         'stroke="#b0bec5" stroke-width="0.4"/>')
        z_c = (np.arange(N_LAG) + 0.5) * DZ
        th_c = (np.arange(M) + 0.5) * 2 * math.pi / M
        for i, j in zip(*np.nonzero(open_mask)):
            if math.sin(th_c[j]) < 0:   # front half only
                r_c = float(r[i:i + 2, j].mean())
                parts.append(f'<circle cx="{ox + r_c * math.cos(th_c[j]):.1f}" '
                             f'cy="{oy - z_c[i]:.1f}" r="1.6" fill="#37474f"/>')
        parts.append(f'<text x="{ox}" y="{H - 8}" text-anchor="middle" '
                     f'fill="#37474f">skavl {name}</text>')
    parts.append(f'<text x="{pad}" y="{pad - 10}" fill="#90a4ae">'
                 'lo-side (vind) &#8592; &#8226; &#8594; le-side · '
                 'prikkar = vindauge · linjer = kvart 10. mm</text></svg>')
    with open(path, "w") as f:
        f.write("\n".join(parts))


# --------------------------------------------------------------------- main
def main():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    reports, sil = [], []
    for name, cfg in SIBLINGS.items():
        r = grow(cfg)
        open_mask = window_mask(r, cfg)
        mesh, tags = build_mesh(r, open_mask)
        rep = validate(name, r, open_mask, mesh, tags)
        rep["fro"] = cfg["seed"]
        rep.update({f"cfg_{k}": v for k, v in cfg.items() if k != "seed"})
        out = os.path.join(here, "print", f"skavl-{name}.3mf")
        mesh.export(out)
        rep["fil"] = os.path.relpath(out, here)
        reports.append(rep)
        sil.append((name, r, open_mask))
        print(f"{name}: watertight={rep['vasstett']} masse={rep['masse_g']:.0f} g "
              f"overheng_maks={rep['overheng_maks']:.1f}deg "
              f"bru_maks={rep['bru_maks_mm']:.1f}mm blendceller={rep['blendceller']}")

    silhouette_svg(sil, os.path.join(here, "silhuett-v0.2.svg"))
    write_report(reports, os.path.join(here, "validering-v0.2.md"))

    failures = []
    for rep in reports:
        if not rep["vasstett"]:
            failures.append(f"{rep['namn']}: ikkje vasstett")
        if rep["masse_g"] >= 150:
            failures.append(f"{rep['namn']}: masse {rep['masse_g']:.0f} g >= 150 g")
        if rep["bru_maks_mm"] > BRU_MAKS + 0.01:
            failures.append(f"{rep['namn']}: bru {rep['bru_maks_mm']:.1f} mm > {BRU_MAKS} mm")
        if rep["blendceller"] > 0:
            failures.append(f"{rep['namn']}: {rep['blendceller']} vindauge i blendbandet")
        if rep["overheng_brot_areal_pst"] > 1.0:
            failures.append(f"{rep['namn']}: {rep['overheng_brot_areal_pst']:.2f} % "
                            f"av skalet over {OVERHENG_DEG} deg")
    if failures:
        raise SystemExit("VALIDERING FEILA:\n  " + "\n  ".join(failures))
    print("Alle portar passerte.")


def write_report(reports, path):
    lines = [
        "# Skavl v0.2, valideringsrapport (generert av `skavl.py`)",
        "",
        "> Pseudokode-steg 6 i `briefs/skavl-algoritme.md`: måltala før print.",
        "> Traktat 1.321: denne rapporten er projeksjonen som gjer flest",
        "> seleksjonstrykk synlege, legg han ved kvar print.",
        "",
        "| Måltal | Krav | " + " | ".join(r["namn"] for r in reports) + " |",
        "|---|---|" + "---|" * len(reports),
    ]

    def row(label, krav, fmt, key):
        vals = " | ".join(fmt.format(r[key]) for r in reports)
        lines.append(f"| {label} | {krav} | {vals} |")

    row("Frø", "loggført", "{}", "fro")
    row("Vasstett solid", "ja", "{}", "vasstett")
    row("Masse (PLA 1,24 g/cm³)", "< 150 g", "{:.0f} g", "masse_g")
    row("Masse (PETG 1,27 g/cm³, jf. brief v1.1)", "< 150 g", "{:.0f} g", "masse_petg_g")
    row("Overheng, maks (skal)", f"< {OVERHENG_DEG}°", "{:.1f}°", "overheng_maks")
    row("Overheng, p95", "-", "{:.1f}°", "overheng_p95")
    row("Skalareal over budsjett", "< 1 %", "{:.2f} %", "overheng_brot_areal_pst")
    row("Bru, maks vindaugsspenn", f"≤ {BRU_MAKS} mm", "{:.1f} mm", "bru_maks_mm")
    row("Vindauge i blendbandet", "0", "{}", "blendceller")
    row("Vindauge (celler)", "-", "{}", "vindauge_n_celler")
    row("Opningsareal", "-", "{:.0f} mm²", "opningsareal_mm2")
    row("Opningsgrad lo-sida", "~30 % mål", "{:.0f} %", "opningsgrad_lo_pst")
    row("Største radius", f"≤ {R_MAKS} mm", "{:.1f} mm", "r_maks_mm")
    row("Høgd", "-", "{:.0f} mm", "hogd_mm")
    row("Fil", "-", "`{}`", "fil")
    lines += [
        "",
        f"Blendfri ved konstruksjon: ingen vindaugscelle har siktline frå",
        f"LED-senteret (z = {Z_LED:.0f} mm) med elevasjon i bandet "
        f"[{GLARE_BAND_DEG[0]:.0f}°, {GLARE_BAND_DEG[1]:.0f}°]. Konveksjon går",
        "gjennom dei låge vindauga på lo-sida og ut toppopninga (skorstein).",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
