using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

const int TargetN = 11;

static int EdgeIndex(int n, int u, int v)
{
    if (u > v) (u, v) = (v, u);
    return u * (2 * n - u - 1) / 2 + v - u - 1;
}

static ulong Decode(string line, int n)
{
    var edgeCount = n * (n - 1) / 2;
    var expected = 1 + (edgeCount + 5) / 6;
    if (line.Length != expected || line[0] != n + 63)
        throw new InvalidDataException($"unexpected order-{n} graph6 record");
    ulong mask = 0;
    var position = 0;
    foreach (var ch in line.AsSpan(1))
    {
        var value = ch - 63;
        if (value is < 0 or >= 64) throw new InvalidDataException("bad graph6 byte");
        for (var shift = 5; shift >= 0 && position < edgeCount; --shift, ++position)
        {
            if ((value & (1 << shift)) == 0) continue;
            var cursor = 0;
            for (var v = 1; v < n; ++v)
            for (var u = 0; u < v; ++u, ++cursor)
                if (cursor == position) mask |= 1UL << EdgeIndex(n, u, v);
        }
    }
    return mask;
}

static string Encode(ulong mask)
{
    const int n = TargetN;
    const int edgeCount = n * (n - 1) / 2;
    Span<char> output = stackalloc char[1 + (edgeCount + 5) / 6];
    output[0] = (char)(n + 63);
    var position = 0;
    for (var block = 1; block < output.Length; ++block)
    {
        var value = 0;
        for (var shift = 5; shift >= 0; --shift, ++position)
        {
            if (position >= edgeCount) continue;
            var cursor = 0;
            for (var v = 1; v < n; ++v)
            for (var u = 0; u < v; ++u, ++cursor)
                if (cursor == position && (mask & (1UL << EdgeIndex(n, u, v))) != 0)
                    value |= 1 << shift;
        }
        output[block] = (char)(value + 63);
    }
    return new string(output);
}

static ulong LiftBase(ulong baseMask, int baseN)
{
    ulong lifted = 0;
    for (var u = 0; u < baseN; ++u)
    for (var v = u + 1; v < baseN; ++v)
        if ((baseMask & (1UL << EdgeIndex(baseN, u, v))) != 0)
            lifted |= 1UL << EdgeIndex(TargetN, u, v);
    return lifted;
}

static void ExpandDeleteOne(TextReader input, TextWriter output)
{
    string? line;
    while ((line = input.ReadLine()) is not null)
    {
        line = line.TrimEnd('\r');
        if (line.Length == 0 || line.StartsWith(">>")) continue;
        var baseMask = LiftBase(Decode(line, 10), 10);
        for (var neighborhood = 0; neighborhood < (1 << 10); ++neighborhood)
        {
            var mask = baseMask;
            for (var u = 0; u < 10; ++u)
                if ((neighborhood & (1 << u)) != 0)
                    mask |= 1UL << EdgeIndex(TargetN, u, 10);
            output.WriteLine(Encode(mask));
        }
    }
}

static void ExpandDeleteTwo(TextReader input, TextWriter output)
{
    string? line;
    while ((line = input.ReadLine()) is not null)
    {
        line = line.TrimEnd('\r');
        if (line.Length == 0 || line.StartsWith(">>")) continue;
        var baseMask = LiftBase(Decode(line, 9), 9);
        for (var incident = 0; incident < (1 << 19); ++incident)
        {
            var mask = baseMask;
            for (var u = 0; u < 9; ++u)
            {
                if ((incident & (1 << u)) != 0)
                    mask |= 1UL << EdgeIndex(TargetN, u, 9);
                if ((incident & (1 << (9 + u))) != 0)
                    mask |= 1UL << EdgeIndex(TargetN, u, 10);
            }
            if ((incident & (1 << 18)) != 0)
                mask |= 1UL << EdgeIndex(TargetN, 9, 10);
            output.WriteLine(Encode(mask));
        }
    }
}

static IEnumerable<int[]> Multisets(int length, int types, int minimum = 0, int[]? prefix = null, int depth = 0)
{
    prefix ??= new int[length];
    if (depth == length)
    {
        yield return (int[])prefix.Clone();
        yield break;
    }
    for (var value = minimum; value < types; ++value)
    {
        prefix[depth] = value;
        foreach (var result in Multisets(length, types, value, prefix, depth + 1))
            yield return result;
    }
}

static void ExpandThreeVertexCover(TextWriter output)
{
    foreach (var columns in Multisets(8, 8))
    for (var internalMask = 0; internalMask < 8; ++internalMask)
    {
        ulong mask = 0;
        for (var u = 0; u < 8; ++u)
        for (var outside = 0; outside < 3; ++outside)
            if ((columns[u] & (1 << outside)) != 0)
                mask |= 1UL << EdgeIndex(TargetN, u, 8 + outside);
        if ((internalMask & 1) != 0) mask |= 1UL << EdgeIndex(TargetN, 8, 9);
        if ((internalMask & 2) != 0) mask |= 1UL << EdgeIndex(TargetN, 8, 10);
        if ((internalMask & 4) != 0) mask |= 1UL << EdgeIndex(TargetN, 9, 10);
        output.WriteLine(Encode(mask));
    }
}

static void Union(string output, string summaryPath, string[] inputs)
{
    var all = new HashSet<string>(StringComparer.Ordinal);
    var inputCounts = new Dictionary<string, long>(StringComparer.Ordinal);
    foreach (var input in inputs)
    {
        long count = 0;
        foreach (var raw in File.ReadLines(input))
        {
            var line = raw.TrimEnd('\r');
            if (line.Length == 0 || line.StartsWith(">>")) continue;
            if (line.Length != 11 || line[0] != TargetN + 63)
                throw new InvalidDataException($"bad canonical record in {input}");
            all.Add(line);
            ++count;
        }
        inputCounts[Path.GetFileName(input)] = count;
    }
    var ordered = all.Order(StringComparer.Ordinal).ToArray();
    using (var writer = new StreamWriter(output, false, new UTF8Encoding(false)))
        foreach (var line in ordered)
        {
            writer.Write(line);
            writer.Write('\n');
        }
    using var sha = SHA256.Create();
    using var stream = File.OpenRead(output);
    var digest = Convert.ToHexString(sha.ComputeHash(stream)).ToLowerInvariant();
    var summary = new
    {
        schema = "tuza-order-11-puleo-residual-union-v1",
        canonical_input_records = inputCounts,
        union_records = ordered.LongLength,
        union_sha256 = digest,
        order = "ordinal graph6"
    };
    File.WriteAllText(summaryPath, JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }) + "\n");
}

static void Normalize(string input, string output)
{
    using var writer = new StreamWriter(output, false, new UTF8Encoding(false));
    foreach (var raw in File.ReadLines(input))
    {
        var line = raw.TrimEnd('\r');
        if (line.Length == 0 || line.StartsWith(">>")) continue;
        writer.Write(line);
        writer.Write('\n');
    }
}

static void ExpandFile(string mode, string? inputPath, string outputPath)
{
    using var output = new StreamWriter(outputPath, false, new UTF8Encoding(false)) { NewLine = "\n" };
    if (mode == "cover-three")
    {
        ExpandThreeVertexCover(output);
        return;
    }
    if (inputPath is null) throw new ArgumentNullException(nameof(inputPath));
    using var input = new StreamReader(inputPath, Encoding.ASCII);
    if (mode == "delete-one") ExpandDeleteOne(input, output);
    else if (mode == "delete-two") ExpandDeleteTwo(input, output);
    else throw new ArgumentOutOfRangeException(nameof(mode));
}

if (args.Length == 1 && args[0] == "delete-one") ExpandDeleteOne(Console.In, Console.Out);
else if (args.Length == 1 && args[0] == "delete-two") ExpandDeleteTwo(Console.In, Console.Out);
else if (args.Length == 1 && args[0] == "cover-three") ExpandThreeVertexCover(Console.Out);
else if (args.Length == 4 && args[0] == "expand-file") ExpandFile(args[1], args[2] == "-" ? null : args[2], args[3]);
else if (args.Length == 3 && args[0] == "normalize") Normalize(args[1], args[2]);
else if (args.Length >= 4 && args[0] == "union") Union(args[1], args[2], args[3..]);
else
{
    Console.Error.WriteLine("usage: ResidualTools delete-one|delete-two|cover-three");
    Console.Error.WriteLine("   or: ResidualTools normalize INPUT OUTPUT");
    Console.Error.WriteLine("   or: ResidualTools expand-file delete-one|delete-two INPUT OUTPUT");
    Console.Error.WriteLine("   or: ResidualTools expand-file cover-three - OUTPUT");
    Console.Error.WriteLine("   or: ResidualTools union OUTPUT SUMMARY INPUT...");
    return 2;
}
return 0;
