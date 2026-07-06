#!/usr/bin/env python3
"""Skavl v0.3, vase branch: rib/slit grammar from the reference images
(ref/README.md). Same curve-stack machinery as skavl.py (imported), but
the open cells come from continuous slits *between* helical ribs instead
of noise-punched windows. No LED, so the glare and thermal clamps are
off; print physics (overhang, bridge, web, mass) still gate everything.

Three siblings map to the references:
  d-vridd    <- ref-a: dense twisted lamellae, waist, m=4 mouth
  e-drope    <- ref-b: no twist, wobbling ribs, teardrop slit rhythm, flare
  f-timeglas <- ref-c: medium twist, hourglass, long slits with pinches, m=3

Run:  python3 skavl_vase.py   (writes print/vase-*.3mf,
                               validering-vase-v0.3.md, silhuett-vase-v0.3.svg)
"""

import math
import os

import numpy as np

import skavl as sk

# ---------------------------------------------------------------- parameters
N_LAG, DZ, M = sk.N_LAG, sk.DZ, sk.M          # same grid as the lamp
THETA = sk.THETA
DRIFT_MAX = sk.DRIFT_MAX                      # radial drift per ring (45 deg)
BRU_MAKS = sk.BRU_MAKS                        # max unsupported span [mm]
WEB_MIN = sk.WEB_MIN                          # min material between slits [mm]
T_VEGG = sk.T_VEGG
OVERHENG_DEG = sk.OVERHENG_DEG
R_FOT = 30.0                                  # foot radius [mm]
FOT_RINGAR = 5                                # closed rings at the foot
TOPP_RINGAR = 3                               # closed rings at the rim
H = N_LAG * DZ

SIBLINGS = {
    # ref-a: mange ribber, sterk twist, innsnoert midje hoegt, kvadratisk munning.
    # Twist og storste radius er klemde til FDM-printbar ribbekant (< 50 grader):
    # ref-a er glasert keramikk (stottefri prosess), FDM tvingar slakare twist.
    "d-vridd": dict(
        seed=101, n_rib=44, twist_deg=112.0, wobble=0.0, rib_relief=4.0,
        profil=[(0, R_FOT), (30, 64), (95, 80), (150, 58), (205, 74), (240, 70)],
        m_poly=4, poly_amp=5.0, gap_frac=0.36,
        drope_lam=0.0, drope_styrke=0.0,
    ),
    # ref-b: faerre ribber, ingen twist men vibrering, dropar, trompet-topp
    "e-drope": dict(
        seed=202, n_rib=40, twist_deg=0.0, wobble=3.5, rib_relief=6.5,
        profil=[(0, R_FOT), (35, 80), (90, 72), (150, 52), (200, 74), (240, 98)],
        m_poly=0, poly_amp=0.0, gap_frac=0.50,
        drope_lam=68.0, drope_styrke=0.85,
    ),
    # ref-c: timeglas, medium twist, lange slissar med pinch, trekantmunning
    "f-timeglas": dict(
        seed=303, n_rib=40, twist_deg=115.0, wobble=2.0, rib_relief=4.0,
        profil=[(0, R_FOT), (35, 82), (120, 56), (200, 84), (240, 78)],
        m_poly=3, poly_amp=4.0, gap_frac=0.44,
        drope_lam=150.0, drope_styrke=0.55,
    ),
}


# ------------------------------------------------------------------- fields
def twist(z, cfg):
    """Accumulated rib rotation at height z [rad]. Smooth ease-in/out so the
    twist rate (and thus the rib-edge drift) stays inside the clamp."""
    t = sk.smoothstep(z, FOT_RINGAR * DZ, H - TOPP_RINGAR * DZ)
    return math.radians(cfg["twist_deg"]) * t


def profile(z, cfg):
    """Piecewise-linear designed silhouette through the (z, r) knots."""
    zs, rs = zip(*cfg["profil"])
    return np.interp(z, zs, rs)


def rib_phase(z, cfg):
    """u in [0,1) per theta sample at height z: 0 = rib centre, 0.5 = slit
    centre. Rotates with the twist and wobbles for e-drope, so relief and
    slits share one frame (the rib is raised, the slit between it is cut)."""
    th_frame = THETA - twist(z, cfg)
    if cfg["wobble"] > 0:
        wob = cfg["_wob"]
        th_frame = th_frame - cfg["wobble"] / max(profile(z, cfg), 1.0) \
            * wob(THETA, z)
    return (th_frame * cfg["n_rib"] / (2.0 * math.pi)) % 1.0


def radius_field(cfg):
    """r(i, j): designed profile + raised ribs + m-gon mouth harmonic, then
    one upward clamp pass for print drift (never > 45 deg). The rib relief
    makes the lamellae stand proud of the base surface (ref-a/ref-d)."""
    noise = sk.make_noise(cfg["seed"], K=16, n_lo=1, n_hi=4,
                          lam_lo=90.0, lam_hi=260.0)
    r = np.zeros((N_LAG + 1, M))
    r[0, :] = R_FOT
    for i in range(1, N_LAG + 1):
        z = i * DZ
        base = profile(z, cfg)
        # raised ribs: cosine bump peaked at the rib centre (u=0), 0 at slit
        u = rib_phase(z, cfg)
        relief = cfg["rib_relief"] * (0.5 + 0.5 * np.cos(2.0 * math.pi * u)) \
            * sk.smoothstep(z, FOT_RINGAR * DZ, FOT_RINGAR * DZ + 16.0)
        # mouth polygon harmonic, grows toward the rim, rotates with twist
        amp = cfg["poly_amp"] * sk.smoothstep(z, 0.55 * H, H)
        poly = amp * np.cos(cfg["m_poly"] * (THETA - twist(z, cfg))) \
            if cfg["m_poly"] else 0.0
        org = 1.0 * noise(THETA, z)   # gentle organic drift
        cand = base + relief + poly + org
        r[i, :] = np.clip(cand, r[i - 1, :] - DRIFT_MAX, r[i - 1, :] + DRIFT_MAX)
    return r


def slit_mask(r, cfg):
    """Open cells = slits between ribs. Cell (i, j) lies between rings
    i, i+1 and theta samples j, j+1. u is the position inside one
    rib+gap period, measured in the frame that rotates with the twist
    (and wobbles, for e-drope): the slit follows the rib."""
    n_rib = cfg["n_rib"]
    wob = cfg["_wob"]                        # shared with rib relief (aligned)
    z_c = (np.arange(N_LAG) + 0.5) * DZ
    th_c = (np.arange(M) + 0.5) * 2.0 * math.pi / M
    r_c = sk.cell_radius(r)
    open_mask = np.zeros((N_LAG, M), dtype=bool)

    period = 2.0 * math.pi / n_rib          # rib+slit angular period [rad]
    for i in range(FOT_RINGAR, N_LAG - TOPP_RINGAR):
        z = z_c[i]
        # local gap fraction: base * teardrop envelope * end taper
        env = 1.0
        if cfg["drope_styrke"] > 0:
            phase = 2.0 * math.pi * z / cfg["drope_lam"]
            env = 1.0 - cfg["drope_styrke"] * (0.5 + 0.5 * np.cos(phase)) ** 1.5
        taper = sk.smoothstep(z, FOT_RINGAR * DZ, FOT_RINGAR * DZ + 24.0) \
            * sk.smoothstep(H - z, TOPP_RINGAR * DZ, TOPP_RINGAR * DZ + 24.0)
        gap = cfg["gap_frac"] * env * taper
        # print budgets, applied to the gap fraction itself so the slit stays
        # ONE continuous vertical band (no per-row repacking that would break it
        # into dashes). Slit arc width = gap * period * r <= BRU_MAKS; the web
        # left over = (1 - gap) * period * r >= WEB_MIN. Cap gap to honour both
        # at this row's max radius.
        r_row = float(r_c[i, :].max())
        cellw = 2.0 * math.pi * r_row / M                  # one-cell margin for
        gap_bru = (BRU_MAKS - 1.6 * cellw) / (period * r_row)   # rasterisation
        gap_web = 1.0 - (WEB_MIN + 1.2 * cellw) / (period * r_row)
        gap = float(min(gap, gap_bru, gap_web))
        if gap <= 0.04:
            continue
        # rib frame: rotate with twist, wobble rib centres organically
        th_frame = th_c - twist(z, cfg)
        if cfg["wobble"] > 0:
            th_frame = th_frame - cfg["wobble"] / r_c[i, :].mean() \
                * wob(th_c, z)
        u = (th_frame * n_rib / (2.0 * math.pi)) % 1.0
        open_mask[i, :] = np.minimum(np.abs(u - 0.5), 1.0 - np.abs(u - 0.5)) < gap / 2.0

    # no diagonal-only contact between cavities (manifold safety at slit ends)
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


# --------------------------------------------------------------- validation
def validate(name, r, open_mask, mesh, tags, cfg):
    rep = {"namn": name, "fro": cfg["seed"]}
    rep["vasstett"] = bool(mesh.is_watertight)
    rep["masse_g"] = float(mesh.volume) * sk.PLA_DENSITY
    rep["masse_petg_g"] = float(mesh.volume) * sk.PETG_DENSITY
    rep["trekantar"] = len(mesh.faces)

    shell = np.isin(tags, ("out", "in"))
    nz = mesh.face_normals[shell][:, 2]
    ang = np.degrees(np.arcsin(np.clip(-nz, 0.0, 1.0)))
    areas = mesh.area_faces[shell]
    rep["overheng_maks"] = float(ang.max())
    rep["overheng_brot_areal_pst"] = float(
        areas[ang > OVERHENG_DEG].sum() / areas.sum() * 100.0)

    # rib-edge drift from twist + wobble, the analytic overhang of the webs
    r_c = sk.cell_radius(r)
    z_all = np.arange(N_LAG + 1) * DZ
    tw = np.array([twist(z, cfg) for z in z_all])
    dtw = np.abs(np.diff(tw)) / DZ                     # rad per mm
    edge_drift = r_c.max(axis=1) * dtw + (cfg["wobble"] * 0.06)
    rep["ribbekant_maks_deg"] = float(np.degrees(np.arctan(edge_drift.max())))

    z_c = (np.arange(N_LAG) + 0.5) * DZ
    max_span, area_open, area_tot = 0.0, 0.0, 0.0
    for i in range(N_LAG):
        row = open_mask[i, :]
        cellw = 2.0 * math.pi * r_c[i, :] / M
        area_tot += float((cellw * DZ).sum())
        if not row.any():
            continue
        area_open += float((cellw * DZ)[row].sum())
        ext = np.concatenate([row, row])
        best = run = 0
        for v in ext[:2 * M - 1]:
            run = run + 1 if v else 0
            best = max(best, run)
        max_span = max(max_span, min(best, M) * float(cellw[row].max()))
    rep["bru_maks_mm"] = float(max_span)
    rep["opningsgrad_pst"] = area_open / area_tot * 100.0
    rep["r_maks_mm"] = float(r.max())
    rep["hogd_mm"] = float(H)
    rep["n_ribber"] = cfg["n_rib"]
    rep["twist_deg"] = cfg["twist_deg"]
    return rep


def write_report(reports, path):
    lines = [
        "# Skavl v0.3 vase-greina, valideringsrapport (generert av `skavl_vase.py`)",
        "",
        "> Ribbe/slisse-grammatikken fraa referansebileta (`ref/README.md`).",
        "> Vase, ikkje lampe: blend- og termikk-klemmene er av; printfysikken",
        "> gjeld fullt ut. Traktat 1.321: rapporten er projeksjonen som gjer",
        "> flest seleksjonstrykk synlege.",
        "",
        "| Maaltal | Krav | " + " | ".join(r["namn"] for r in reports) + " |",
        "|---|---|" + "---|" * len(reports),
    ]

    def row(label, krav, fmt, key):
        vals = " | ".join(fmt.format(r[key]) for r in reports)
        lines.append(f"| {label} | {krav} | {vals} |")

    row("Fro", "loggfort", "{}", "fro")
    row("Ribber", "-", "{}", "n_ribber")
    row("Twist", "-", "{:.0f} grader", "twist_deg")
    row("Vasstett solid", "ja", "{}", "vasstett")
    row("Masse (PLA 1,24 g/cm3)", "< 150 g", "{:.0f} g", "masse_g")
    row("Masse (PETG 1,27 g/cm3)", "< 150 g", "{:.0f} g", "masse_petg_g")
    row("Overheng maks (skal)", f"< {OVERHENG_DEG} grader", "{:.1f} grader", "overheng_maks")
    row("Skalareal over budsjett", "< 1 %", "{:.2f} %", "overheng_brot_areal_pst")
    row("Ribbekant-drift (analytisk)", f"< {OVERHENG_DEG} grader", "{:.1f} grader", "ribbekant_maks_deg")
    row("Bru, maks slissespenn", f"<= {BRU_MAKS} mm", "{:.1f} mm", "bru_maks_mm")
    row("Opningsgrad heile flata", "25-45 % maal", "{:.0f} %", "opningsgrad_pst")
    row("Storste radius", f"<= {sk.R_MAKS} mm", "{:.1f} mm", "r_maks_mm")
    row("Hogd", "-", "{:.0f} mm", "hogd_mm")
    row("Fil", "-", "`{}`", "fil")
    lines += [
        "",
        "Slissane foelgjer ribberetninga, difor er einaste bru-spenn sjolve",
        "slissebreidda; det er slik v0.3 naar opningsgrad-maalet som v0.2",
        "(vindaugsceller) ikkje kunne naa (6-8 %). Vasane er sleeves (ope",
        "botn); eit laust golv kan printast separat om dei skal halde vatn",
        "(glassroyr inni er tilraadd uansett for blomar).",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


# --------------------------------------------------------------------- main
def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "print"), exist_ok=True)
    reports, sil = [], []
    for name, cfg in SIBLINGS.items():
        # one wobble field per sibling, shared by rib relief and slit mask
        cfg["_wob"] = sk.make_noise(cfg["seed"] + 500, K=12, n_lo=1, n_hi=3,
                                    lam_lo=120.0, lam_hi=320.0)
        r = radius_field(cfg)
        open_mask = slit_mask(r, cfg)
        mesh, tags = sk.build_mesh(r, open_mask)
        rep = validate(name, r, open_mask, mesh, tags, cfg)
        out = os.path.join(here, "print", f"vase-{name}.3mf")
        mesh.export(out)
        rep["fil"] = os.path.relpath(out, here)
        reports.append(rep)
        sil.append((name, r, open_mask))
        print(f"{name}: watertight={rep['vasstett']} masse={rep['masse_g']:.0f} g "
              f"overheng={rep['overheng_maks']:.1f} ribbekant={rep['ribbekant_maks_deg']:.1f} "
              f"bru={rep['bru_maks_mm']:.1f}mm opning={rep['opningsgrad_pst']:.0f}%")

    sk.silhouette_svg(sil, os.path.join(here, "silhuett-vase-v0.3.svg"))
    write_report(reports, os.path.join(here, "validering-vase-v0.3.md"))

    failures = []
    for rep in reports:
        if not rep["vasstett"]:
            failures.append(f"{rep['namn']}: ikkje vasstett")
        if rep["masse_g"] >= 150:
            failures.append(f"{rep['namn']}: masse {rep['masse_g']:.0f} g >= 150 g")
        if rep["bru_maks_mm"] > BRU_MAKS + 0.01:
            failures.append(f"{rep['namn']}: bru {rep['bru_maks_mm']:.1f} mm")
        if rep["overheng_brot_areal_pst"] > 1.0:
            failures.append(f"{rep['namn']}: {rep['overheng_brot_areal_pst']:.2f} % skal over budsjett")
        if rep["ribbekant_maks_deg"] > OVERHENG_DEG:
            failures.append(f"{rep['namn']}: ribbekant {rep['ribbekant_maks_deg']:.1f} grader")
        if not (15.0 <= rep["opningsgrad_pst"] <= 55.0):
            failures.append(f"{rep['namn']}: opningsgrad {rep['opningsgrad_pst']:.0f} % utanfor 15-55")
    if failures:
        raise SystemExit("VALIDERING FEILA:\n  " + "\n  ".join(failures))
    print("Alle portar passerte.")


if __name__ == "__main__":
    main()
