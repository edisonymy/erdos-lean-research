using System.Collections.Concurrent;
using System.Diagnostics;
using System.Text.Json;

// Exact exhaustive search for noncocircular convex 8-subsets of a lattice box.
// Translation and interchange of the coordinate axes normalize every searched
// configuration so min x=min y=0 and max x=side >= max y.

record Point(int X, int Y);

sealed class Totals
{
    public long NormalizedSubsets;
    public long StrictlyConvex;
    public long Noncocircular;
    public long[] MaximumHistogram = new long[8];
    public int BestMaximum = 8;
    public Point[]? BestPolygon;
    public Point[]? Counterexample;
}

sealed class Local
{
    public long NormalizedSubsets;
    public long StrictlyConvex;
    public long Noncocircular;
    public long[] MaximumHistogram = new long[8];
    public int BestMaximum = 8;
    public Point[]? BestPolygon;
    public Point[]? Counterexample;
    public int[] Ids = new int[8];
    public int[] Lower = new int[8];
    public int[] Upper = new int[8];
    public long[] Distances = new long[7];
}

static class Search
{
    static long Cross(int a, int b, int c, int width)
    {
        int ax = a / width, ay = a % width;
        int bx = b / width, by = b % width;
        int cx = c / width, cy = c % width;
        return (long)(bx - ax) * (cy - ay) - (long)(by - ay) * (cx - ax);
    }

    static bool AllEightOnStrictHull(Local local, int width)
    {
        int lowerCount = 0;
        foreach (int p in local.Ids)
        {
            while (lowerCount >= 2 && Cross(local.Lower[lowerCount - 2], local.Lower[lowerCount - 1], p, width) <= 0)
                --lowerCount;
            local.Lower[lowerCount++] = p;
        }
        int upperCount = 0;
        for (int k = 7; k >= 0; --k)
        {
            int p = local.Ids[k];
            while (upperCount >= 2 && Cross(local.Upper[upperCount - 2], local.Upper[upperCount - 1], p, width) <= 0)
                --upperCount;
            local.Upper[upperCount++] = p;
        }
        return lowerCount + upperCount - 2 == 8;
    }

    static Point[] HullOrder(Local local, int width)
    {
        // Recompute the two chains and concatenate them in CCW order.
        var ids = local.Ids.Select(id => new Point(id / width, id % width)).ToArray();
        var lower = new List<Point>();
        foreach (Point p in ids)
        {
            while (lower.Count >= 2 && CrossPoint(lower[^2], lower[^1], p) <= 0) lower.RemoveAt(lower.Count - 1);
            lower.Add(p);
        }
        var upper = new List<Point>();
        for (int i = ids.Length - 1; i >= 0; --i)
        {
            Point p = ids[i];
            while (upper.Count >= 2 && CrossPoint(upper[^2], upper[^1], p) <= 0) upper.RemoveAt(upper.Count - 1);
            upper.Add(p);
        }
        return lower.Take(lower.Count - 1).Concat(upper.Take(upper.Count - 1)).ToArray();
    }

    static long CrossPoint(Point a, Point b, Point c) =>
        (long)(b.X - a.X) * (c.Y - a.Y) - (long)(b.Y - a.Y) * (c.X - a.X);

    static long InCircle(Point a, Point b, Point c, Point d)
    {
        long ax = a.X - d.X, ay = a.Y - d.Y;
        long bx = b.X - d.X, by = b.Y - d.Y;
        long cx = c.X - d.X, cy = c.Y - d.Y;
        return (ax * ax + ay * ay) * (bx * cy - by * cx)
             - (bx * bx + by * by) * (ax * cy - ay * cx)
             + (cx * cx + cy * cy) * (ax * by - ay * bx);
    }

    static bool IsCocircular(Point[] polygon)
    {
        for (int i = 3; i < polygon.Length; ++i)
            if (InCircle(polygon[0], polygon[1], polygon[2], polygon[i]) != 0)
                return false;
        return true;
    }

    static int MaximumDistinct(Point[] polygon, Local local)
    {
        int maximum = 0;
        for (int i = 0; i < 8; ++i)
        {
            int k = 0;
            for (int j = 0; j < 8; ++j)
            {
                if (i == j) continue;
                long dx = polygon[i].X - polygon[j].X;
                long dy = polygon[i].Y - polygon[j].Y;
                local.Distances[k++] = dx * dx + dy * dy;
            }
            Array.Sort(local.Distances);
            int distinct = 1;
            for (k = 1; k < 7; ++k)
                if (local.Distances[k] != local.Distances[k - 1]) ++distinct;
            maximum = Math.Max(maximum, distinct);
        }
        return maximum;
    }

    static void Process(Local local, int side)
    {
        int width = side + 1;
        // min x=0 follows from i0 < width; max x=side is imposed by i7.
        // Require min y=0. Axis interchange then lets max x be the larger span.
        bool hasYZero = false;
        foreach (int id in local.Ids)
            hasYZero |= id % width == 0;
        if (!hasYZero || local.Ids[7] / width != side) return;
        ++local.NormalizedSubsets;
        if (!AllEightOnStrictHull(local, width)) return;
        ++local.StrictlyConvex;
        Point[] polygon = HullOrder(local, width);
        if (IsCocircular(polygon)) return;
        ++local.Noncocircular;
        int maximum = MaximumDistinct(polygon, local);
        ++local.MaximumHistogram[maximum];
        if (maximum < local.BestMaximum)
        {
            local.BestMaximum = maximum;
            local.BestPolygon = polygon;
        }
        if (maximum < 4 && local.Counterexample is null)
            local.Counterexample = polygon;
    }

    public static Totals RunSide(int side, int threads)
    {
        int width = side + 1;
        int count = width * width;
        var totals = new Totals();
        var options = new ParallelOptions { MaxDegreeOfParallelism = threads };
        Parallel.For(0, width, options, () => new Local(), (i0, _, local) =>
        {
            int[] a = local.Ids;
            a[0] = i0;
            for (a[1] = i0 + 1; a[1] <= count - 7; ++a[1])
            for (a[2] = a[1] + 1; a[2] <= count - 6; ++a[2])
            for (a[3] = a[2] + 1; a[3] <= count - 5; ++a[3])
            for (a[4] = a[3] + 1; a[4] <= count - 4; ++a[4])
            for (a[5] = a[4] + 1; a[5] <= count - 3; ++a[5])
            for (a[6] = a[5] + 1; a[6] <= count - 2; ++a[6])
            for (a[7] = Math.Max(a[6] + 1, side * width); a[7] < count; ++a[7])
                Process(local, side);
            return local;
        }, local =>
        {
            lock (totals)
            {
                totals.NormalizedSubsets += local.NormalizedSubsets;
                totals.StrictlyConvex += local.StrictlyConvex;
                totals.Noncocircular += local.Noncocircular;
                for (int i = 0; i < 8; ++i) totals.MaximumHistogram[i] += local.MaximumHistogram[i];
                if (local.BestMaximum < totals.BestMaximum)
                {
                    totals.BestMaximum = local.BestMaximum;
                    totals.BestPolygon = local.BestPolygon;
                }
                totals.Counterexample ??= local.Counterexample;
            }
        });
        return totals;
    }
}

static class Program
{
    public static void Main(string[] args)
    {
        int maximumSide = 6;
        int minimumSide = 2;
        int threads = Environment.ProcessorCount;
        string output = "lattice8_span6.json";
        for (int i = 0; i < args.Length; ++i)
        {
            if (args[i] == "--max-side") maximumSide = int.Parse(args[++i]);
            else if (args[i] == "--min-side") minimumSide = int.Parse(args[++i]);
            else if (args[i] == "--threads") threads = int.Parse(args[++i]);
            else if (args[i] == "--output") output = args[++i];
            else throw new ArgumentException($"unknown argument {args[i]}");
        }

        var stopwatch = Stopwatch.StartNew();
        var records = new List<object>();
        bool found = false;
        for (int side = minimumSide; side <= maximumSide && !found; ++side)
        {
            Totals totals = Search.RunSide(side, threads);
            found = totals.Counterexample is not null;
            records.Add(new
            {
                side,
                normalized_subsets = totals.NormalizedSubsets,
                strictly_convex = totals.StrictlyConvex,
                noncocircular = totals.Noncocircular,
                maximum_histogram = totals.MaximumHistogram
                    .Select((count, maximum) => new { maximum, count })
                    .Where(item => item.count != 0),
                best_maximum = totals.BestMaximum,
                best_margin = totals.BestMaximum - 4,
                best_polygon = totals.BestPolygon,
                counterexample = totals.Counterexample
            });
            Console.Error.WriteLine($"side={side}: normalized={totals.NormalizedSubsets:N0}, convex={totals.StrictlyConvex:N0}, noncyclic={totals.Noncocircular:N0}, best={totals.BestMaximum}");
        }

        var result = new
        {
            problem = "Erdos 982, n=8",
            exact = true,
            scope = $"all integer 8-point configurations whose larger coordinate span is at most {maximumSide}, up to translation and coordinate-axis interchange",
            normalization = $"min x=min y=0; max x=side>=max y; sides {minimumSide}..max_side",
            threshold = 4,
            threads,
            elapsed_seconds = stopwatch.Elapsed.TotalSeconds,
            found_counterexample = found,
            sides = records
        };
        var json = JsonSerializer.Serialize(result, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(output, json + Environment.NewLine);
        Console.WriteLine(json);
    }
}
