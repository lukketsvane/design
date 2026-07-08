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
  const { rMax, zMin, zMax } = bounds(cfg);
  const span = Math.max(2 * rMax, zMax - zMin);
  const pitch = span / res;
  const f = makeField(cfg, want === "stl" ? 0 : pitch);
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
