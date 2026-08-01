#!/usr/bin/env node
// Independent exact replay of the optimized D2 collision search.
// IEEE-754 integers are exact here: at the retained bound every intermediate
// is far below 2^53.  This implementation shares no code with the C# search.

import fs from "node:fs";

if (process.argv.length < 3 || process.argv.length > 4) {
  throw new Error("usage: node independent_d2_candidate_audit.mjs RUN.json [AUDIT.json]");
}
const reference = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const bound = reference.bound;
if (bound > 100000) throw new Error("integer-safety guard exceeded");

function distinctCount(values) {
  let count = 0;
  for (let i = 0; i < values.length; ++i) {
    let seen = false;
    for (let j = 0; j < i; ++j) seen ||= values[i] === values[j];
    if (!seen) ++count;
  }
  return count;
}

function better(x, y) {
  if (y === null) return true;
  const mx = Math.max(...x.Profile), my = Math.max(...y.Profile);
  if (mx !== my) return mx < my;
  const sx = x.Profile.reduce((a, b) => a + b, 0);
  const sy = y.Profile.reduce((a, b) => a + b, 0);
  if (sx !== sy) return sx < sy;
  for (const key of ["A", "B", "C", "D"]) {
    if (x[key] !== y[key]) return x[key] < y[key];
  }
  return false;
}

let triples = 0;
let squareCandidates = 0;
let convexCandidates = 0;
let bothAxial = 0;
let counterexamples = 0;
let best = null;

for (let a = 2; a <= bound; ++a) {
  const aa = a * a;
  for (let c = 1; c <= a; ++c) {
    const cc = c * c;
    for (let b = 1; b < a; ++b) {
      ++triples;
      const bb = b * b;
      const nearBase = (a - b) ** 2;
      const farBase = (a + b) ** 2;
      const d2s = [
        4 * aa - nearBase,
        4 * aa - farBase,
        aa + cc - nearBase,
        aa + cc - farBase,
      ];
      const roots = [];
      for (const d2 of d2s) {
        if (d2 <= 0) continue;
        const d = Math.round(Math.sqrt(d2));
        if (d * d !== d2 || d <= 0 || d >= c || d > bound || roots.includes(d)) continue;
        roots.push(d);
        ++squareCandidates;
        if (a * d + b * c <= a * c) continue;
        ++convexCandidates;
        const dd = d * d;
        const nearX = nearBase + dd, farX = farBase + dd;
        const nearY = bb + (c - d) ** 2, farY = bb + (c + d) ** 2;
        const profile = [
          distinctCount([4 * aa, aa + cc, nearX, farX]),
          distinctCount([4 * cc, aa + cc, nearY, farY]),
          distinctCount([4 * bb, 4 * dd, 4 * (bb + dd), nearX, farX, nearY, farY]),
        ];
        if (profile[0] > 3) throw new Error("candidate reduction mismatch");
        if (profile[1] <= 3) ++bothAxial;
        if (Math.max(...profile) < 4) ++counterexamples;
        const item = { A: a, B: b, C: c, D: d, Profile: profile };
        if (better(item, best)) best = item;
      }
    }
  }
}

const result = {
  bound,
  parameter_triples: triples,
  square_d_candidates: squareCandidates,
  strictly_convex_candidates: convexCandidates,
  both_axial_orbits_at_most_three: bothAxial,
  counterexamples,
  best,
};
for (const key of Object.keys(result)) {
  if (JSON.stringify(result[key]) !== JSON.stringify(reference[key])) {
    throw new Error(`${key}: ${JSON.stringify(result[key])} != ${JSON.stringify(reference[key])}`);
  }
}
const report = {
  reference: process.argv[2],
  implementation: "independent_d2_candidate_audit.mjs",
  matches: true,
  audit: result,
};
const reportText = `${JSON.stringify(report, null, 2)}\n`;
if (process.argv[3]) fs.writeFileSync(process.argv[3], reportText);
process.stdout.write(reportText);
