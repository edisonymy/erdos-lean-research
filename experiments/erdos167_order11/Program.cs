using System.Diagnostics;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

const int N = 11;
const int M = 55;
const ulong Full = (1UL << M) - 1;

if (args.Length is not (2 or 3))
{
    Console.Error.WriteLine("usage: DenseScreen UNRESOLVED.g6 SUMMARY.json [RESIDUAL.g6]");
    return 2;
}

var edges = new (int U, int V)[M];
var edgeIndex = new int[N, N];
var cursor = 0;
for (var u = 0; u < N; ++u)
for (var v = u + 1; v < N; ++v)
{
    edges[cursor] = (u, v);
    edgeIndex[u, v] = edgeIndex[v, u] = cursor++;
}

var triangleVertices = new (int A, int B, int C)[165];
var triangleMasks = new ulong[165];
cursor = 0;
for (var a = 0; a < N; ++a)
for (var b = a + 1; b < N; ++b)
for (var c = b + 1; c < N; ++c)
{
    triangleVertices[cursor] = (a, b, c);
    triangleMasks[cursor++] = (1UL << edgeIndex[a, b]) |
                              (1UL << edgeIndex[a, c]) |
                              (1UL << edgeIndex[b, c]);
}

static ulong DecodeGraph6(string line, int[,] edgeIndex)
{
    if (line.Length != 11 || line[0] != 63 + N)
        throw new InvalidDataException($"unexpected order-11 graph6 record {line}");
    ulong result = 0;
    var position = 0;
    foreach (var ch in line.AsSpan(1))
    {
        var value = ch - 63;
        if (value is < 0 or >= 64) throw new InvalidDataException("invalid graph6 byte");
        for (var shift = 5; shift >= 0 && position < M; --shift, ++position)
        {
            if ((value & (1 << shift)) == 0) continue;
            var k = 0;
            for (var v = 1; v < N; ++v)
            for (var u = 0; u < v; ++u, ++k)
                if (k == position) result |= 1UL << edgeIndex[u, v];
        }
    }
    return result;
}

static int Greedy(ulong graph, ulong[] triangles, int[] order)
{
    ulong used = 0;
    var packed = 0;
    foreach (var index in order)
    {
        var triangle = triangles[index];
        if ((graph & triangle) != triangle || (used & triangle) != 0) continue;
        used |= triangle;
        ++packed;
    }
    return packed;
}

static int CutCover(ulong graph, (int U, int V)[] edges)
{
    Span<int> adjacency = stackalloc int[N];
    Span<int> degree = stackalloc int[N];
    for (var i = 0; i < M; ++i)
    {
        if ((graph & (1UL << i)) == 0) continue;
        var (u, v) = edges[i];
        adjacency[u] |= 1 << v;
        adjacency[v] |= 1 << u;
        ++degree[u];
        ++degree[v];
    }
    Span<byte> leastVertex = stackalloc byte[1 << (N - 1)];
    for (var v = 0; v < N - 1; ++v) leastVertex[1 << v] = (byte)v;
    for (var mask = 1; mask < leastVertex.Length; ++mask)
        if (leastVertex[mask] == 0 && (mask & 1) == 0)
            leastVertex[mask] = (byte)BitOperations.TrailingZeroCount((uint)mask);

    Span<byte> cut = stackalloc byte[1 << (N - 1)];
    var best = 0;
    for (var side = 1; side < cut.Length; ++side)
    {
        var bit = side & -side;
        var v = leastVertex[bit];
        var rest = side ^ bit;
        cut[side] = (byte)(cut[rest] + degree[v] -
                           2 * BitOperations.PopCount((uint)(adjacency[v] & rest)));
        if (cut[side] > best) best = cut[side];
    }
    return BitOperations.PopCount(graph) - best;
}

var lex = Enumerable.Range(0, 165).ToArray();
var reverse = lex.Reverse().ToArray();
var spread = lex.OrderBy(i =>
{
    var (a, b, c) = triangleVertices[i];
    return ((a * 7 + b * 3 + c * 5) % 11, a, b, c);
}).ToArray();
var spreadReverse = spread.Reverse().ToArray();
var orders = new[] { lex, reverse, spread, spreadReverse };

var counts = new SortedDictionary<int, long>();
var unresolvedCounts = new SortedDictionary<int, long>();
long records = 0, closed = 0, unresolved = 0;
var minimumSlack = int.MaxValue;
var timer = Stopwatch.StartNew();
using var inputHash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
using var output = new StreamWriter(args[0], false, new System.Text.UTF8Encoding(false));
using var inputFile = args.Length == 3 ? new StreamReader(args[2], Encoding.ASCII) : null;
var input = inputFile ?? Console.In;
string? line;
while ((line = input.ReadLine()) is not null)
{
    line = line.TrimEnd('\r');
    if (line.Length == 0 || line.StartsWith(">>")) continue;
    inputHash.AppendData(Encoding.ASCII.GetBytes(line + "\n"));
    var complement = DecodeGraph6(line, edgeIndex);
    var missing = BitOperations.PopCount(complement);
    if (missing > 27) throw new InvalidDataException("input outside Puleo residual edge range");
    var graph = Full ^ complement;
    var packing = 0;
    foreach (var order in orders) packing = Math.Max(packing, Greedy(graph, triangleMasks, order));
    var cover = CutCover(graph, edges);
    var slack = 2 * packing - cover;
    minimumSlack = Math.Min(minimumSlack, slack);
    ++records;
    counts[missing] = counts.GetValueOrDefault(missing) + 1;
    if (slack >= 0) ++closed;
    else
    {
        ++unresolved;
        unresolvedCounts[missing] = unresolvedCounts.GetValueOrDefault(missing) + 1;
        output.WriteLine(line);
    }
}
output.Close();
timer.Stop();
var residualDigest = Convert.ToHexString(inputHash.GetHashAndReset()).ToLowerInvariant();
var summary = new
{
    schema = "tuza-order-11-primary-witness-screen-v1",
    records,
    residual_sha256 = residualDigest,
    closed_by_witnesses = closed,
    unresolved,
    minimum_slack_2p_minus_c = minimumSlack,
    elapsed_seconds = timer.Elapsed.TotalSeconds,
    records_by_complement_edges = counts,
    unresolved_by_complement_edges = unresolvedCounts,
    method = "best of four deterministic greedy edge-disjoint triangle packings; exact maximum bipartite cut cover"
};
File.WriteAllText(args[1], JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }) + "\n");
Console.Error.WriteLine($"screened {records}; closed {closed}; unresolved {unresolved}; min slack {minimumSlack}; seconds {timer.Elapsed.TotalSeconds:F3}");
return 0;
