#!/usr/bin/env python3
"""Skavl v0.4, lamp hybrid: the rib/slit grammar from skavl_vase.py (v0.3)
brought back onto the LAMP, with the two clamps the vases switched off
turned back ON:

  - glare (blend): no slit may sit where a straight ray from the LED centre
    reaches an eye in the glare elevation band; those cells stay closed, so
    you never see the bare bulb through a slit (ref-03 lamellokklusjon);
  - thermal: the wall keeps a floor radius around the LED band, and the low
    slits stay open as the convection intake (chimney out the top rim).

Everything else is the vase generator: raised ribs, continuous slits along
the rib direction, print-physics clamps (overhang, bridge, web, mass).

Run:  python3 skavl_lampe.py   (writes print/lampe-*.3mf,
                                validering-lampe-v0.4.md, silhuett-lampe-v0.4.svg)
"""

import math
import os

import numpy as np

import skavl as sk
import skavl_vase as vg

# lamp geometry (E27, LED) reused from the v0.2 lamp module
R_SOKKEL = sk.R_SOKKEL          # E27 collar radius incl. tolerance [mm]
COLLAR_RINGS = sk.COLLAR_RINGS
Z_LED = sk.Z_LED               # LED centre height [mm]
LED_BAND = sk.LED_BAND
R_TERM_FLOOR = sk.R_TERM_FLOOR
GLARE_BAND_DEG = sk.GLARE_BAND_DEG   # (-5, 60): no slit here
N_LAG, DZ, M = sk.N_LAG, sk.DZ, sk.M
THETA = sk.THETA
DRIFT_MAX = vg.DRIFT_MAX
BRU_MAKS, WEB_MIN = vg.BRU_MAKS, vg.WEB_MIN
OVERHENG_DEG = sk.OVERHENG_DEG
H = N_LAG * DZ

SIBLINGS = {
    # roleg: faerre, roleg twist, tett mot augehoegd
    "lampe-roleg": dict(
        seed=511, n_rib=40, twist_deg=70.0, wobble=0.0, rib_relief=4.0,
        profil=[(0, R_SOKKEL), (30, 60), (130, 88), (200, 70), (240, 64)],
        m_poly=4, poly_amp=4.0, gap_frac=0.42,
        drope_lam=0.0, drope_styrke=0.0,
    ),
    # open: meir opning der glare tillet det (laagt, konveksjon)
    "lampe-open": dict(
        seed=622, n_rib=44, twist_deg=95.0, wobble=1.5, rib_relief=4.5,
        profil=[(0, R_SOKKEL), (28, 66), (130, 92), (205, 74), (240, 66)],
        m_poly=3, poly_amp=4.0, gap_frac=0.5,
        drope_lam=0.0, drope_styrke=0.0,
    ),
}


def r_term_floor(z):
    """Radial floor around the LED band so the wall never crowds the bulb."""
    ramp = DRIFT_MAX / DZ
    dist = max(0.0, LED_BAND[0] - z, z - LED_BAND[1])
    return max(R_SOKKEL, R_TERM_FLOOR - ramp * dist)


def radius_field_lamp(cfg):
    """Vase radius field + E27 collar pin + thermal floor around the LED."""
    r = vg.radius_field(cfg)                       # ribs + profile + drift clamp
    for i in range(N_LAG + 1):
        z = i * DZ
        if i <= COLLAR_RINGS:
            r[i, :] = R_SOKKEL
            continue
        floor = r_term_floor(z)
        r[i, :] = np.clip(r[i, :], floor, sk.R_MAKS)
    # re-run the upward drift clamp after flooring so print physics holds
    for i in range(1, N_LAG + 1):
        r[i, :] = np.clip(r[i, :], r[i - 1, :] - DRIFT_MAX, r[i - 1, :] + DRIFT_MAX)
    return r


def slit_mask_lamp(r, cfg):
    """Vase slit mask, then close every slit cell inside the glare band."""
    open_mask = vg.slit_mask(r, cfg)
    z_c = (np.arange(N_LAG) + 0.5) * DZ
    r_c = sk.cell_radius(r)
    for i in range(N_LAG):
        elev = np.degrees(np.arctan2(z_c[i] - Z_LED, r_c[i, :]))
        glare = (elev >= GLARE_BAND_DEG[0] - 1.5) & (elev <= GLARE_BAND_DEG[1] + 1.5)
        open_mask[i, glare] = False
    return open_mask


def validate_lamp(name, r, open_mask, mesh, tags, cfg):
    rep = vg.validate(name, r, open_mask, mesh, tags, cfg)
    # glare: count open cells whose LED-ray elevation is in the band
    z_c = (np.arange(N_LAG) + 0.5) * DZ
    r_c = sk.cell_radius(r)
    hits = 0
    for i in range(N_LAG):
        row = open_mask[i, :]
        if not row.any():
            continue
        elev = np.degrees(np.arctan2(z_c[i] - Z_LED, r_c[i, :]))
        hits += int(np.count_nonzero(row & (elev >= GLARE_BAND_DEG[0])
                                     & (elev <= GLARE_BAND_DEG[1])))
    rep["blendceller"] = hits
    # thermal clearance: min wall radius within the LED band
    zc_all = np.arange(N_LAG + 1) * DZ
    band = (zc_all >= LED_BAND[0]) & (zc_all <= LED_BAND[1])
    rep["term_klaring_mm"] = float(r[band].min()) if band.any() else float(r.min())
    rep["r_sokkel_mm"] = float(r[0].mean())
    return rep


def write_report(reports, path):
    lines = [
        "# Skavl v0.4 lampe-hybrid, valideringsrapport (`skavl_lampe.py`)",
        "",
        "> Ribbe/slisse-grammatikken fraa vase-v0.3 paa lampa, med glare- og",
        "> termikk-klemmene paa att. Blendfri ved konstruksjon: ingen slisse",
        "> i glare-bandet; konveksjon gjennom dei laage slissane, ut toppen.",
        "",
        "| Maaltal | Krav | " + " | ".join(r["namn"] for r in reports) + " |",
        "|---|---|" + "---|" * len(reports),
    ]

    def row(label, krav, fmt, key):
        lines.append(f"| {label} | {krav} | "
                     + " | ".join(fmt.format(r[key]) for r in reports) + " |")

    row("Fro", "loggfort", "{}", "fro")
    row("Ribber", "-", "{}", "n_ribber")
    row("Twist", "-", "{:.0f} grader", "twist_deg")
    row("Vasstett solid", "ja", "{}", "vasstett")
    row("Masse (PLA)", "< 150 g", "{:.0f} g", "masse_g")
    row("Masse (PETG)", "< 150 g", "{:.0f} g", "masse_petg_g")
    row("Sokkelradius (E27 + tol)", f"~{R_SOKKEL:.1f} mm", "{:.1f} mm", "r_sokkel_mm")
    row("Termisk klaring (LED-band)", f">= {R_TERM_FLOOR:.0f} mm", "{:.1f} mm", "term_klaring_mm")
    row("Vindauge i glare-bandet", "0", "{}", "blendceller")
    row("Overheng maks (skal)", f"< {OVERHENG_DEG} grader", "{:.1f} grader", "overheng_maks")
    row("Skalareal over budsjett", "< 1 %", "{:.2f} %", "overheng_brot_areal_pst")
    row("Ribbekant-drift", f"< {OVERHENG_DEG} grader", "{:.1f} grader", "ribbekant_maks_deg")
    row("Bru, maks slissespenn", f"<= {BRU_MAKS} mm", "{:.1f} mm", "bru_maks_mm")
    row("Opningsgrad heile flata", "-", "{:.0f} %", "opningsgrad_pst")
    row("Fil", "-", "`{}`", "fil")
    lines += [
        "",
        "Glare-bandet [{:.0f}, {:.0f}] grader elevasjon fraa LED (z = {:.0f} mm)".format(
            GLARE_BAND_DEG[0], GLARE_BAND_DEG[1], Z_LED),
        "er heilt lukka, augehoegd ser aldri den nakne paera gjennom ein slisse.",
        "Dei laage slissane (under LED) er opne som konveksjonsinntak.",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "print"), exist_ok=True)
    reports, sil = [], []
    for name, cfg in SIBLINGS.items():
        cfg["_wob"] = sk.make_noise(cfg["seed"] + 500, K=12, n_lo=1, n_hi=3,
                                    lam_lo=120.0, lam_hi=320.0)
        r = radius_field_lamp(cfg)
        open_mask = slit_mask_lamp(r, cfg)
        mesh, tags = sk.build_mesh(r, open_mask)
        rep = validate_lamp(name, r, open_mask, mesh, tags, cfg)
        out = os.path.join(here, "print", f"lampe-{name.split('-')[1]}.3mf")
        mesh.export(out)
        rep["fil"] = os.path.relpath(out, here)
        reports.append(rep)
        sil.append((name, r, open_mask))
        print(f"{name}: watertight={rep['vasstett']} masse={rep['masse_g']:.0f} g "
              f"blend={rep['blendceller']} term={rep['term_klaring_mm']:.0f}mm "
              f"overheng={rep['overheng_maks']:.1f} bru={rep['bru_maks_mm']:.1f} "
              f"opning={rep['opningsgrad_pst']:.0f}%")

    sk.silhouette_svg(sil, os.path.join(here, "silhuett-lampe-v0.4.svg"))
    write_report(reports, os.path.join(here, "validering-lampe-v0.4.md"))

    fail = []
    for rep in reports:
        if not rep["vasstett"]:
            fail.append(f"{rep['namn']}: ikkje vasstett")
        if rep["masse_g"] >= 150:
            fail.append(f"{rep['namn']}: masse {rep['masse_g']:.0f} g")
        if rep["blendceller"] > 0:
            fail.append(f"{rep['namn']}: {rep['blendceller']} slissar i glare-bandet")
        if rep["bru_maks_mm"] > BRU_MAKS + 0.01:
            fail.append(f"{rep['namn']}: bru {rep['bru_maks_mm']:.1f} mm")
        if rep["overheng_brot_areal_pst"] > 1.0:
            fail.append(f"{rep['namn']}: skal over overheng-budsjett")
        if rep["ribbekant_maks_deg"] > OVERHENG_DEG:
            fail.append(f"{rep['namn']}: ribbekant {rep['ribbekant_maks_deg']:.1f} grader")
        if rep["term_klaring_mm"] < R_TERM_FLOOR - 0.5:
            fail.append(f"{rep['namn']}: term klaring {rep['term_klaring_mm']:.1f} mm")
    if fail:
        raise SystemExit("VALIDERING FEILA:\n  " + "\n  ".join(fail))
    print("Alle portar passerte.")


if __name__ == "__main__":
    main()
