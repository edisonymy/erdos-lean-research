#!/usr/bin/env node
"use strict";

// Independent Node.js parser/filter for McKay's complete order-10 catalogue.
const crypto = require("crypto");
const fs = require("fs");
const zlib = require("zlib");

const [catalogue, summaryPath, residualPath] = process.argv.slice(2);
if (!catalogue || !summaryPath) {
  throw new Error("usage: node independent_screen.js graph10.g6.gz summary.json");
}

const edges = [];
for (let v = 1; v < 10; ++v) for (let u = 0; u < v; ++u) edges.push([u, v]);

function decode(line) {
  if (line.length !== 9 || line.charCodeAt(0) !== 73) throw new Error("bad graph6 line");
  const present = new Uint8Array(45);
  let at = 0;
  for (let position = 1; position < 9; ++position) {
    const value = line.charCodeAt(position) - 63;
    if (value < 0 || value >= 64) throw new Error("bad graph6 byte");
    for (let shift = 5; shift >= 0; --shift, ++at) {
      if (at < 45 && (value & (1 << shift))) present[at] = 1;
    }
  }
  return present;
}

function isResidual(present) {
  let m = 0;
  for (const value of present) m += value;
  if (m <= 10) return true;
  if (m > 17) return false;
  const degree = new Int8Array(10);
  for (let i = 0; i < 45; ++i) if (present[i]) {
    degree[edges[i][0]]++;
    degree[edges[i][1]]++;
  }
  if (m <= 13) for (let v = 0; v < 10; ++v) {
    if (m - degree[v] <= 4) return true;
  }
  for (let u = 0; u < 10; ++u) for (let v = u + 1; v < 10; ++v) {
    let outside = 0;
    for (let i = 0; i < 45 && !outside; ++i) {
      if (present[i] && edges[i][0] !== u && edges[i][1] !== u &&
          edges[i][0] !== v && edges[i][1] !== v) outside = 1;
    }
    if (!outside) return true;
  }
  return false;
}

const compressedHash = crypto.createHash("sha256");
const uncompressedHash = crypto.createHash("sha256");
const residualHash = crypto.createHash("sha256");
let total = 0;
let selected = 0;
let pending = Buffer.alloc(0);
const residualOutput = residualPath ? fs.createWriteStream(residualPath) : null;

const input = fs.createReadStream(catalogue);
input.on("data", chunk => compressedHash.update(chunk));
const gunzip = zlib.createGunzip();
input.pipe(gunzip);
gunzip.on("data", chunk => {
  uncompressedHash.update(chunk);
  pending = Buffer.concat([pending, chunk]);
  let newline;
  while ((newline = pending.indexOf(10)) >= 0) {
    const raw = pending.subarray(0, newline + 1);
    pending = pending.subarray(newline + 1);
    const line = raw.subarray(0, raw.length - 1).toString("ascii");
    ++total;
    if (isResidual(decode(line))) {
      ++selected;
      residualHash.update(raw);
      if (residualOutput) residualOutput.write(raw);
    }
  }
});
gunzip.on("end", () => {
  if (pending.length) {
    ++total;
    const line = pending.toString("ascii");
    if (isResidual(decode(line))) {
      ++selected;
      residualHash.update(pending);
      if (residualOutput) residualOutput.write(pending);
    }
  }
  const summary = {
    schema: "tuza-order-10-independent-node-screen-v1",
    catalogue_records: total,
    residual_records: selected,
    catalogue_compressed_sha256: compressedHash.digest("hex"),
    catalogue_uncompressed_sha256: uncompressedHash.digest("hex"),
    residual_graph6_sha256: residualHash.digest("hex"),
  };
  if (residualOutput) residualOutput.end();
  fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2) + "\n");
  console.log(JSON.stringify(summary, null, 2));
});
