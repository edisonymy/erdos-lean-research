using System.Diagnostics;
using System.Numerics;
using System.Security.Cryptography;
using System.Text.Json;

const int N = 11;
const int M = 55;

if (args.Length != 2)
{
    Console.Error.WriteLine("usage: IndependentVerify RESIDUAL.g6 SUMMARY.json");
    return 2;
}

static int EdgeIndex(int u, int v)
{
    if (u > v) (u, v) = (v, u);
    return u * (2 * N - u - 1) / 2 + v - u - 1;
}

static (int[] ComplementAdjacency, int Edges) Decode(string line)
{
    if (line.Length != 11 || line[0] != 63 + N) throw new InvalidDataException("bad graph6 record");
    var adjacency = new int[N];
    var position = 0;
    var edges = 0;
    foreach (var ch in line.AsSpan(1))
    {
        var value = ch - 63;
        if (value is < 0 or >= 64) throw new InvalidDataException("bad graph6 byte");
        for (var shift = 5; shift >= 0 && position < M; --shift, ++position)
        {
            if ((value & (1 << shift)) == 0) continue;
            var cursor = 0;
            for (var v = 1; v < N; ++v)
            for (var u = 0; u < v; ++u, ++cursor)
            {
                if (cursor != position) continue;
                adjacency[u] |= 1 << v;
                adjacency[v] |= 1 << u;
                ++edges;
            }
        }
    }
    return (adjacency, edges);
}

static bool IsPuleoResidual(int[] complement, int edgeCount)
{
    if (edgeCount <= 16) return true;
    for (var v = 0; v < N; ++v)
        if (edgeCount - BitOperations.PopCount((uint)complement[v]) <= 10) return true;
    for (var u = 0; u < N; ++u)
    for (var v = u + 1; v < N; ++v)
    {
        var remaining = edgeCount - BitOperations.PopCount((uint)complement[u])
                                  - BitOperations.PopCount((uint)complement[v])
                                  + ((complement[u] >> v) & 1);
        if (remaining <= 4) return true;
    }
    for (var a = 0; a < N; ++a)
    for (var b = a + 1; b < N; ++b)
    for (var c = b + 1; c < N; ++c)
    {
        var internalEdges = ((complement[a] >> b) & 1) +
                            ((complement[a] >> c) & 1) +
                            ((complement[b] >> c) & 1);
        var remaining = edgeCount - BitOperations.PopCount((uint)complement[a])
                                  - BitOperations.PopCount((uint)complement[b])
                                  - BitOperations.PopCount((uint)complement[c])
                                  + internalEdges;
        if (remaining == 0) return true;
    }
    return false;
}

static (int A, int B, int C, ulong Edges)[] TriangleOrder(int multiplier, int shift, bool reverse)
{
    var permutation = Enumerable.Range(0, N).Select(x => (multiplier * x + shift) % N).ToArray();
    var list = new List<(int, int, int, ulong)>();
    for (var ai = 0; ai < N; ++ai)
    for (var bi = ai + 1; bi < N; ++bi)
    for (var ci = bi + 1; ci < N; ++ci)
    {
        var values = new[] { permutation[ai], permutation[bi], permutation[ci] };
        Array.Sort(values);
        var (a, b, c) = (values[0], values[1], values[2]);
        var mask = (1UL << EdgeIndex(a, b)) | (1UL << EdgeIndex(a, c)) | (1UL << EdgeIndex(b, c));
        list.Add((a, b, c, mask));
    }
    if (reverse) list.Reverse();
    return list.ToArray();
}

static int Packing(int[] graphAdjacency, (int A, int B, int C, ulong Edges)[] order)
{
    ulong used = 0;
    var count = 0;
    foreach (var (a, b, c, edges) in order)
    {
        if (((graphAdjacency[a] >> b) & 1) == 0 ||
            ((graphAdjacency[a] >> c) & 1) == 0 ||
            ((graphAdjacency[b] >> c) & 1) == 0 || (used & edges) != 0) continue;
        used |= edges;
        ++count;
    }
    return count;
}

static int CutCover(int[] graph, int graphEdges)
{
    var degree = new int[N];
    for (var v = 0; v < N; ++v) degree[v] = BitOperations.PopCount((uint)graph[v]);
    var side = 0;
    var priorGray = 0;
    var cut = 0;
    var bestCut = 0;
    for (var step = 1; step < (1 << (N - 1)); ++step)
    {
        var gray = step ^ (step >> 1);
        var changed = gray ^ priorGray;
        var vertex = BitOperations.TrailingZeroCount((uint)changed);
        var wasInside = (side & (1 << vertex)) != 0;
        var insideNeighbors = BitOperations.PopCount((uint)(graph[vertex] & side));
        if (!wasInside)
        {
            cut += degree[vertex] - 2 * insideNeighbors;
            side |= 1 << vertex;
        }
        else
        {
            cut += -degree[vertex] + 2 * insideNeighbors;
            side &= ~(1 << vertex);
        }
        bestCut = Math.Max(bestCut, cut);
        priorGray = gray;
    }
    return graphEdges - bestCut;
}

var orders = new[]
{
    TriangleOrder(1, 0, false),
    TriangleOrder(1, 3, true),
    TriangleOrder(2, 1, false),
    TriangleOrder(7, 4, true)
};
var timer = Stopwatch.StartNew();
long records = 0, unresolved = 0, outsideResidual = 0;
var minimumSlack = int.MaxValue;
var counts = new SortedDictionary<int, long>();
string? previous = null;
using var hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
foreach (var raw in File.ReadLines(args[0]))
{
    var line = raw.TrimEnd('\r');
    if (line.Length == 0 || line.StartsWith(">>")) continue;
    if (previous is not null && StringComparer.Ordinal.Compare(previous, line) >= 0)
        throw new InvalidDataException("residual is not strictly ordinal-sorted");
    previous = line;
    hash.AppendData(System.Text.Encoding.ASCII.GetBytes(line + "\n"));
    var (complement, missing) = Decode(line);
    if (!IsPuleoResidual(complement, missing)) ++outsideResidual;
    var graph = new int[N];
    var allVertices = (1 << N) - 1;
    for (var v = 0; v < N; ++v) graph[v] = allVertices & ~(1 << v) & ~complement[v];
    var packing = 0;
    foreach (var order in orders) packing = Math.Max(packing, Packing(graph, order));
    var cover = CutCover(graph, M - missing);
    var slack = 2 * packing - cover;
    minimumSlack = Math.Min(minimumSlack, slack);
    if (slack < 0) ++unresolved;
    ++records;
    counts[missing] = counts.GetValueOrDefault(missing) + 1;
}
timer.Stop();
var digest = Convert.ToHexString(hash.GetHashAndReset()).ToLowerInvariant();
var summary = new
{
    schema = "tuza-order-11-independent-witness-verifier-v1",
    records,
    residual_sha256 = digest,
    outside_puleo_residual = outsideResidual,
    unresolved,
    minimum_slack_2p_minus_c = minimumSlack,
    records_by_complement_edges = counts,
    elapsed_seconds = timer.Elapsed.TotalSeconds,
    method = "independent graph6 decoder; four affine vertex-order greedy packings; Gray-code maximum cut"
};
File.WriteAllText(args[1], JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }) + "\n");
Console.Error.WriteLine($"verified {records}; outside {outsideResidual}; unresolved {unresolved}; min slack {minimumSlack}; seconds {timer.Elapsed.TotalSeconds:F3}");
return 0;
