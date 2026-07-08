/* Krone Studio, feltarbeidar: same signerte felt som ../krone.py, evaluert
   paa eit voxelgitter og polygonisert med naive SurfaceNets. Alt i mm.
   Melding inn: {cfg, res, job, want}   ut: {positions, indices, job} eller
   {stl, job} naar want === "stl". */

"use strict";

/* ------------------------------------------------------------ feltet */
function smin(a, b, k) {
  const h = Math.min(Math.max(0.5 + 0.5 * (b - a) / k, 0), 1);
  return b * (1 - h) + a * h - k * h * (1 - h);
}
function smax(a, b, k) { return -smin(-a, -b, k); }

const PATTERNS = {
  quin: s => [[0, 0], [s, s], [s, -s], [-s, s], [-s, -s]],
  ros7: s => {
    const o = [[0, 0]];
    for (let i = 0; i < 6; i++)
      o.push([1.9 * s * Math.cos(Math.PI * i / 3),
              1.9 * s * Math.sin(Math.PI * i / 3)]);
    return o;
  },
  ros19: s => {
    const o = [[0, 0]];
    for (let i = 0; i < 6; i++)
      o.push([1.8 * s * Math.cos(Math.PI * i / 3),
              1.8 * s * Math.sin(Math.PI * i / 3)]);
    for (let i = 0; i < 12; i++)
      o.push([3.4 * s * Math.cos(Math.PI * (i + .5) / 6),
              3.4 * s * Math.sin(Math.PI * (i + .5) / 6)]);
    return o;
  },
};

function makeField(c, pitch) {
  const n = c.n, per = 2 * Math.PI / n;
  const liner = (c.lgap || 0) > 0.5;
  const norm1 = 1 + Math.exp(-Math.pow(2 * c.split / Math.max(c.w1, .1), 2));
  // naalehol under voxelstorleiken gjev berre stoey: klem radien opp til
  // pitchen i grove pass (eksakt att i eksportpasset)
  const rMin = (pitch || 0) * 0.85;
  const pins = (c.pins || []).flatMap(p => {
    const r0 = p.r * (c.pinS != null ? c.pinS : 1);
    if (r0 < 0.35) return [];
    return [{ zp: p.zf * c.H, r: Math.max(r0, rMin),
              offs: PATTERNS[p.pat](p.s), ph: p.phase }];
  });
  const beads = (c.beads || []).map(b => ({
    zb: b.zf * c.H, r: b.r * (c.beadS != null ? c.beadS : 1),
  })).filter(b => b.r > 0.8);

  function prof(u) {          // veggprofil utan dekor
    const ub = Math.min(Math.max(u, 0), 1);
    return c.Rb + (c.Rt - c.Rb) * u + c.bulge * Math.sin(Math.PI * ub);
  }

  return function f(x, y, z) {
    const rho = Math.hypot(x, y);
    const th = Math.atan2(y, x);
    // same innpakking som krone.py: segmentsenter paa th = k*per,
    // saum paa th = (k + 1/2)*per
    const wrapA = t => ((t + per / 2) % per + per) % per - per / 2;
    const tc = rho * wrapA(th);                     // senterbasert
    const tp = rho * wrapA(th + per / 2);           // saumbasert

    const u = z / c.H, ub = Math.min(Math.max(u, 0), 1);
    let Rm = prof(u);
    const slope = (c.Rt - c.Rb) / c.H
      + c.bulge * Math.PI / c.H * Math.cos(Math.PI * ub);
    // panelpute og saumriller
    const cosw = Math.cos(tc / (Rm + 1e-9) * n / 2);
    Rm += c.pillow * cosw * cosw
      - c.groove * Math.exp(-Math.pow(tp / 1.7, 2));
    if (c.band_z != null)
      Rm -= c.groove * Math.exp(-Math.pow((z - c.band_z * c.H) / 1.7, 2));
    const stretch = Math.sqrt(1 + slope * slope);
    const cs = 1 / stretch;
    let g = Math.abs(rho - Rm) * cs - c.t / 2;

    // kronekant
    const ztop = c.H + c.h1 / norm1 * (
      Math.exp(-Math.pow((tp - c.split) / c.w1, 2))
      + Math.exp(-Math.pow((tp + c.split) / c.w1, 2)))
      + c.h2 * Math.exp(-Math.pow(tc / c.w2, 2));
    g = smax(g, z - ztop, c.ck);
    g = smax(g, -z, c.rim_k != null ? c.rim_k : 2.5);

    // vindauge (ujamn kapsel), mjukt subtrahert
    const zh = c.hz * c.H;
    const m = (z - zh) * stretch;
    const q = Math.min(Math.max(m / Math.max(c.hlen, .1), 0), 1);
    const rq = c.hr0 + (c.hr1 - c.hr0) * q;
    const mcl = m - Math.min(Math.max(m, 0), c.hlen);
    const dHole = Math.hypot(tc, mcl) - rq;
    if (rq > 0.3) g = smax(g, -dHole, c.hk);

    // naalehol
    for (const p of pins) {
      const aa = p.ph === "c" ? tc : tp;
      const mm = (z - p.zp) * stretch;
      let d = 1e9;
      for (const [du, dv] of p.offs) {
        const dd = Math.hypot(aa - du, mm - dv) - p.r;
        if (dd < d) d = dd;
      }
      g = smax(g, -d, 0.9);
    }

    // perler paa saumane
    for (const bd of beads) {
      const ubb = Math.min(Math.max(bd.zb / c.H, 0), 1);
      const Rmb = c.Rb + (c.Rt - c.Rb) * ubb
        + c.bulge * Math.sin(Math.PI * ubb);
      const dr = rho - (Rmb + c.t * 0.25);
      const d = Math.sqrt(tp * tp + (z - bd.zb) * (z - bd.zb) + dr * dr)
        - bd.r;
      g = smin(g, d, 2.4);
    }

    // liner
    if (liner) {
      const RbL = c.Rb - c.lgap, RtL = c.Rt - c.lgap, tL = 4.0;
      const RmL = RbL + (RtL - RbL) * u + c.bulge * Math.sin(Math.PI * ub);
      let gl = Math.abs(rho - RmL) * cs - tL / 2;
      gl = smax(gl, z - c.H * 0.97, c.ck);
      gl = smax(gl, -z, 2.5);
      const r0 = c.hr0 * 0.6, r1 = c.hr1 * 0.6, ln = c.hlen * 0.65;
      const q2 = Math.min(Math.max(m / Math.max(ln, .1), 0), 1);
      const rq2 = r0 + (r1 - r0) * q2;
      const mcl2 = m - Math.min(Math.max(m, 0), ln);
      const d2 = Math.hypot(tc, mcl2) - rq2;
      if (rq2 > 0.3) gl = smax(gl, -d2, c.hk * 0.8);
      g = Math.min(g, gl);
    }
    return g;
  };
}

function bounds(c) {
  const zcMax = c.H + c.h1 + c.h2 + c.ck + 10;
  const uTop = zcMax / c.H;
  const rTop = c.Rb + (c.Rt - c.Rb) * Math.max(uTop, 1);
  const rMax = Math.max(c.Rb, c.Rt, rTop) + Math.abs(c.bulge) + c.t + 8;
  return { rMax, zMin: -4, zMax: zcMax };
}

/* --------------------------------------- grind: graf av roer og kuler */
function grindLevels(c) {
  const per = 2 * Math.PI / c.n, out = [];
  for (let l = 0; l < c.L; l++) {
    const u = c.L === 1 ? 0.55 : l / (c.L - 1);
    const r = c.R * (c.f_bot + (c.f_top - c.f_bot) * u
      + 4 * c.buk * u * (1 - u));
    const z = c.L === 1 ? 0.55 * c.H : u * c.H;
    out.push([z, r, c.twist * per * l]);
  }
  return out;
}

function grindNode(lv, th) {
  const [z, r, ph] = lv;
  return [r * Math.cos(th + ph), r * Math.sin(th + ph), z];
}

function grindArc(p0, p1, bow, m) {
  const pts = [];
  for (let i = 0; i <= m; i++) {
    const t = i / m;
    const p = [p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t,
               p0[2] + (p1[2] - p0[2]) * t];
    const nrm = Math.hypot(p[0], p[1]);
    if (nrm > 1e-9 && bow) {
      const s = bow * Math.sin(Math.PI * t) / nrm;
      p[0] += p[0] * s; p[1] += p[1] * s;
    }
    pts.push(p);
  }
  return pts;
}

function grindElements(c) {
  const lv = grindLevels(c), n = c.n;
  const perN = 2 * Math.PI / n;
  const zig = c.zig || 0;
  const per = Math.abs(zig) > 0.05 ? 2 * perN : perN;
  const grow = c.grow || 1;
  const Lc = lv.length;
  const su = (i) => Math.pow(grow, Lc === 1 ? 0 : i / (Lc - 1));
  const subs = Math.abs(zig) > 0.05
    ? [[0, zig / 2], [perN, -zig / 2]] : [[0, 0]];
  const offs = () => Math.abs(zig) > 0.05 ? [0, per, -per] : [0];
  const caps = [], balls = [], tori = [], bores = [], loops = [];
  const tube = c.tube;

  function nod(i, th) {
    const p = grindNode(lv[i], th);
    if (subs.length > 1) p[2] += subs[Math.round(th / perN) & 1][1];
    return p;
  }

  for (const [th0] of subs) {
    for (let l = 0; l < Lc - 1; l++) {
      const p0 = nod(l, th0), p1 = nod(l + 1, th0);
      const rr = tube * (su(l) + su(l + 1)) / 2;
      const pts = grindArc(p0, p1, c.bow, 10);
      for (let i = 0; i < pts.length - 1; i++)
        caps.push([pts[i], pts[i + 1], rr, offs()]);
      if (c.diag > 0.01)
        for (const sgn of [1, -1]) {
          const q1 = nod(l + 1, th0 + sgn * perN);
          const qs = grindArc(p0, q1, c.bow * 0.5, 7);
          const dof = Math.abs(zig) > 0.05 ? offs() : [0, -sgn * perN];
          for (let i = 0; i < qs.length - 1; i++)
            caps.push([qs[i], qs[i + 1], rr * c.diag, dof]);
        }
    }
  }
  lv.forEach((l, i) => {
    if (c.rings === 2 || (c.rings === 1 && (i === 0 || i === Lc - 1)))
      tori.push([l[0], l[1], tube * su(i)]);
  });
  let zc = c.L > 1 ? c.H : c.H * 0.98;
  if ((c.cup_zf || 0) > 0.01) zc = c.cup_zf * c.H;
  if (c.cup > 0.5 && c.spokes)
    for (const [th0] of subs) {
      const p0 = nod(Lc - 1, th0);
      const ph = lv[Lc - 1][2];
      const p1 = [c.cup * 0.75 * Math.cos(th0 + ph),
                  c.cup * 0.75 * Math.sin(th0 + ph), zc];
      const pts = grindArc(p0, p1, 0, 3);
      const rr = tube * su(Lc - 1);
      for (let i = 0; i < pts.length - 1; i++)
        caps.push([pts[i], pts[i + 1], rr, offs()]);
    }
  for (const [th0] of subs)
    for (let i = 0; i < Lc; i++) {
      const l = lv[i];
      const p = nod(i, th0);
      if (c.ball > 0.3) balls.push([p, c.ball * su(i), offs()]);
      if (c.nub > 0.3) {
        const fk = (l[1] + tube * 1.25) / (l[1] + 1e-9);
        balls.push([[p[0] * fk, p[1] * fk, p[2]], c.nub * su(i), offs()]);
      }
    }
  if (c.mlen > 0.5)
    for (const [th0] of subs) {
      const p = nod(0, th0);
      const nrm = Math.hypot(p[0], p[1]) + 1e-9;
      const t = c.tilt * Math.PI / 180;
      const d = [p[0] / nrm * Math.sin(t), p[1] / nrm * Math.sin(t),
                 -Math.cos(t)];
      const q = [p[0] + d[0] * c.mlen, p[1] + d[1] * c.mlen,
                 p[2] + d[2] * c.mlen];
      caps.push([p, q, tube * 1.5 * su(0), offs()]);
      bores.push([[p[0] + d[0] * c.mlen * 0.3, p[1] + d[1] * c.mlen * 0.3,
                   p[2] + d[2] * c.mlen * 0.3], d, tube * 0.85 * su(0),
                  c.mlen * 0.9 + 6, offs()]);
    }
  if ((c.loop || 0) > 1) {
    const ti = (c.loop_tilt || 0) * Math.PI / 180;
    let N = [0, Math.cos(ti), Math.sin(ti)];
    let u1 = [1, 0, 0];
    let u2 = [0, N[2], -N[1]];
    const be = (c.loop_lean || 0) * Math.PI / 180;
    const cb = Math.cos(be), sb = Math.sin(be);
    const rot = (v) => [cb * v[0] - sb * v[2], v[1],
                        sb * v[0] + cb * v[2]];
    u1 = rot(u1); u2 = rot(u2); N = rot(N);
    for (const [th0, dz] of subs) {
      const C = [c.loop_out, 0, c.loop_zf * c.H + dz];
      loops.push([C, u1, u2, N, c.loop, c.loop_ell || 1, tube,
                  c.loop_drop || 0, offs()]);
    }
  }
  return { caps, balls, tori, bores, loops, zc, per };
}

function segDist(px, py, pz, a, b, r) {
  const abx = b[0] - a[0], aby = b[1] - a[1], abz = b[2] - a[2];
  const apx = px - a[0], apy = py - a[1], apz = pz - a[2];
  let t = (apx * abx + apy * aby + apz * abz)
    / (abx * abx + aby * aby + abz * abz + 1e-12);
  t = Math.min(Math.max(t, 0), 1);
  return Math.hypot(apx - t * abx, apy - t * aby, apz - t * abz) - r;
}

function makeGrindField(c) {
  const { caps, balls, tori, bores, loops, zc, per } = grindElements(c);
  const k = c.k;
  const rc = c.cup, hc = Math.max(c.cup * 1.05, 16);
  return function f(x, y, z) {
    const rho = Math.hypot(x, y);
    const th = Math.atan2(y, x);
    const thw = ((th + per / 2) % per + per) % per - per / 2;
    let g = 1e9;
    for (const [zt, rt, rr] of tori)
      g = smin(g, Math.hypot(rho - rt, z - zt) - rr, k);
    for (const [a, b, r, offs] of caps)
      for (const off of offs) {
        const tw = thw - off;
        g = smin(g, segDist(rho * Math.cos(tw), rho * Math.sin(tw), z,
                            a, b, r), k);
      }
    const px = rho * Math.cos(thw), py = rho * Math.sin(thw);
    for (const [p, r, boffs] of balls)
      for (const off of boffs) {
        const tw = thw - off;
        g = smin(g, Math.hypot(rho * Math.cos(tw) - p[0],
                               rho * Math.sin(tw) - p[1], z - p[2]) - r, k);
      }
    for (const [C, u1, u2, N, rl, ell, rr, drop, loffs] of loops)
      for (const off of new Set([...loffs, 0, per, -per])) {
        const tw = thw - off;
        const qx = rho * Math.cos(tw) - C[0],
              qy = rho * Math.sin(tw) - C[1], qz = z - C[2];
        let a1 = qx * u1[0] + qy * u1[1] + qz * u1[2];
        const a2 = (qx * u2[0] + qy * u2[1] + qz * u2[2]) / ell;
        const h = qx * N[0] + qy * N[1] + qz * N[2];
        let rrE = rr;
        if (drop > 0.01) {
          const t = Math.min(Math.max(-a2 / (rl + 1e-9), 0), 1);
          a1 = a1 / (1 - drop * t * 0.85 + 1e-9);
          rrE = rr * (1 - drop * 0.45 * t);
        }
        g = smin(g, Math.hypot(Math.hypot(a1, a2) - rl, h) - rrE, k);
      }
    if (rc > 0.5) {
      g = smin(g, Math.max(rho - rc, Math.abs(z - zc) - hc / 2), k);
      const db = Math.max(rho - rc * 0.68, zc + hc / 2 - 3 - z);
      g = smax(g, -db, 1.6);
    }
    for (const [p, d, r, ln, boffs] of bores)
      for (const off of boffs) {
        const tw = thw - off;
        const rx = rho * Math.cos(tw) - p[0], ry = rho * Math.sin(tw) - p[1],
              rz = z - p[2];
        const t = rx * d[0] + ry * d[1] + rz * d[2];
        const rad = Math.hypot(rx - t * d[0], ry - t * d[1], rz - t * d[2]);
        const db = Math.max(rad - r, Math.max(-t - 2, t - ln));
        g = smax(g, -db, 1.2);
      }
    return g;
  };
}

function grindBounds(c) {
  const lp = c.loop || 0, ell = c.loop_ell || 1;
  let rMax = c.R * Math.max(c.f_bot, c.f_top, 1 + Math.abs(c.buk))
    + c.bow + c.tube * 2 + c.ball + c.mlen + 10;
  rMax = Math.max(rMax, (c.loop_out || 0) + lp * ell + c.tube * 2 + 10);
  let zMin = -(c.mlen + Math.max(c.tube * 1.6, c.ball, c.nub)
               + Math.abs(c.zig || 0) / 2 + 8);
  let zMax = c.H + Math.max(c.cup * 1.2, 10) + c.ball
    + Math.abs(c.zig || 0) / 2 + 8;
  if (lp > 1) {
    zMin = Math.min(zMin, c.loop_zf * c.H - lp * ell - c.tube * 2 - 6);
    zMax = Math.max(zMax, c.loop_zf * c.H + lp * ell + c.tube * 2 + 6);
  }
  return { rMax, zMin, zMax };
}

/* ------------------------------------- naive SurfaceNets (Lysenko, MIT) */
const CUBE_EDGES = new Int32Array(24);
const EDGE_TABLE = new Int32Array(256);
(function () {
  let k = 0;
  for (let i = 0; i < 8; ++i)
    for (let j = 1; j <= 4; j <<= 1) {
      const p = i ^ j;
      if (i <= p) { CUBE_EDGES[k++] = i; CUBE_EDGES[k++] = p; }
    }
  for (let i = 0; i < 256; ++i) {
    let em = 0;
    for (let j = 0; j < 24; j += 2) {
      const a = !!(i & (1 << CUBE_EDGES[j]));
      const b = !!(i & (1 << CUBE_EDGES[j + 1]));
      em |= a !== b ? (1 << (j >> 1)) : 0;
    }
    EDGE_TABLE[i] = em;
  }
})();

function surfaceNets(data, dims, spacing, origin) {
  const [sx, sy, sz] = spacing, [ox, oy, oz] = origin;
  const verts = [], faces = [];
  const R = new Int32Array([1, dims[0] + 1, (dims[0] + 1) * (dims[1] + 1)]);
  const grid = new Float32Array(8);
  let bufNo = 1;
  let buffer = new Int32Array(R[2] * 2);
  const x = new Int32Array(3);

  for (x[2] = 0; x[2] < dims[2] - 1; ++x[2], bufNo ^= 1, R[2] = -R[2]) {
    let m = 1 + (dims[0] + 1) * (1 + bufNo * (dims[1] + 1));
    for (x[1] = 0; x[1] < dims[1] - 1; ++x[1], m += 2)
      for (x[0] = 0; x[0] < dims[0] - 1; ++x[0], ++m) {
        let mask = 0, g = 0;
        for (let k = 0; k < 2; ++k)
          for (let j = 0; j < 2; ++j)
            for (let i = 0; i < 2; ++i, ++g) {
              const p = data[(x[2] + k) * dims[0] * dims[1]
                + (x[1] + j) * dims[0] + (x[0] + i)];
              grid[g] = p;
              mask |= p < 0 ? (1 << g) : 0;
            }
        if (mask === 0 || mask === 0xff) continue;
        const em = EDGE_TABLE[mask];
        const v = [0.0, 0.0, 0.0];
        let eCount = 0;
        for (let i = 0; i < 12; ++i) {
          if (!(em & (1 << i))) continue;
          ++eCount;
          const e0 = CUBE_EDGES[i << 1], e1 = CUBE_EDGES[(i << 1) + 1];
          const g0 = grid[e0], g1 = grid[e1];
          let t = g0 - g1;
          if (Math.abs(t) > 1e-12) t = g0 / t; else continue;
          for (let j = 0, k = 1; j < 3; ++j, k <<= 1) {
            const a = e0 & k, b = e1 & k;
            if (a !== b) v[j] += a ? 1.0 - t : t;
            else v[j] += a ? 1.0 : 0;
          }
        }
        const s = 1.0 / eCount;
        v[0] = ox + sx * (x[0] + s * v[0]);
        v[1] = oy + sy * (x[1] + s * v[1]);
        v[2] = oz + sz * (x[2] + s * v[2]);
        buffer[m] = verts.length / 3;
        verts.push(v[0], v[1], v[2]);
        for (let i = 0; i < 3; ++i) {
          if (!(em & (1 << i))) continue;
          const iu = (i + 1) % 3, iv = (i + 2) % 3;
          if (x[iu] === 0 || x[iv] === 0) continue;
          const du = R[iu], dv = R[iv];
          const b0 = buffer[m], b1 = buffer[m - du],
                b2 = buffer[m - du - dv], b3 = buffer[m - dv];
          if (mask & 1) faces.push(b0, b3, b2, b0, b2, b1);
          else faces.push(b0, b1, b2, b0, b2, b3);
        }
      }
  }
  return { positions: new Float32Array(verts),
           indices: new Uint32Array(faces) };
}

/* --------------------------------------------------------------- eksport */
function toSTL(positions, indices) {
  const nt = indices.length / 3;
  const buf = new ArrayBuffer(84 + nt * 50);
  const dv = new DataView(buf);
  dv.setUint32(80, nt, true);
  let o = 84;
  for (let t = 0; t < nt; ++t) {
    const a = indices[3 * t] * 3, b = indices[3 * t + 1] * 3,
          c = indices[3 * t + 2] * 3;
    const ux = positions[b] - positions[a],
          uy = positions[b + 1] - positions[a + 1],
          uz = positions[b + 2] - positions[a + 2];
    const vx = positions[c] - positions[a],
          vy = positions[c + 1] - positions[a + 1],
          vz = positions[c + 2] - positions[a + 2];
    let nx = uy * vz - uz * vy, ny = uz * vx - ux * vz,
        nz = ux * vy - uy * vx;
    const l = Math.hypot(nx, ny, nz) || 1;
    dv.setFloat32(o, nx / l, true); dv.setFloat32(o + 4, ny / l, true);
    dv.setFloat32(o + 8, nz / l, true); o += 12;
    for (const idx of [a, b, c]) {
      dv.setFloat32(o, positions[idx], true);
      dv.setFloat32(o + 4, positions[idx + 1], true);
      dv.setFloat32(o + 8, positions[idx + 2], true);
      o += 12;
    }
    o += 2;
  }
  return buf;
}

/* ------------------------------------------------------------------ main */
self.onmessage = (ev) => {
  const { cfg, res, job, want } = ev.data;
  const grind = cfg.kind === "grind";
  const { rMax, zMin, zMax } = grind ? grindBounds(cfg) : bounds(cfg);
  const span = Math.max(2 * rMax, zMax - zMin);
  const pitch = span / res;
  const f = grind ? makeGrindField(cfg)
                  : makeField(cfg, want === "stl" ? 0 : pitch);
  const nx = Math.ceil(2 * rMax / pitch) + 3;
  const nz = Math.ceil((zMax - zMin) / pitch) + 3;
  const ox = -rMax - pitch, oz = zMin - pitch;
  const data = new Float32Array(nx * nx * nz);
  let i = 0;
  for (let k = 0; k < nz; ++k) {
    const z = oz + k * pitch;
    for (let j = 0; j < nx; ++j) {
      const y = ox + j * pitch;
      for (let ii = 0; ii < nx; ++ii, ++i)
        data[i] = f(ox + ii * pitch, y, z);
    }
  }
  const mesh = surfaceNets(data, [nx, nx, nz],
                           [pitch, pitch, pitch], [ox, ox, oz]);
  // konsistent orientering: signert volum skal vere positivt
  let vol6 = 0;
  const P = mesh.positions, I = mesh.indices;
  for (let t = 0; t < I.length; t += 3) {
    const a = I[t] * 3, b = I[t + 1] * 3, cc = I[t + 2] * 3;
    vol6 += P[a] * (P[b + 1] * P[cc + 2] - P[b + 2] * P[cc + 1])
          - P[a + 1] * (P[b] * P[cc + 2] - P[b + 2] * P[cc])
          + P[a + 2] * (P[b] * P[cc + 1] - P[b + 1] * P[cc]);
  }
  if (vol6 < 0)
    for (let t = 0; t < I.length; t += 3) {
      const tmp = I[t + 1]; I[t + 1] = I[t + 2]; I[t + 2] = tmp;
    }
  if (want === "stl") {
    const stl = toSTL(mesh.positions, mesh.indices);
    self.postMessage({ stl, job }, [stl]);
  } else {
    self.postMessage({ positions: mesh.positions, indices: mesh.indices,
                       job },
                     [mesh.positions.buffer, mesh.indices.buffer]);
  }
};
