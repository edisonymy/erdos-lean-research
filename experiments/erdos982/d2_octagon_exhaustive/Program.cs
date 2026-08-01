using System.Collections.Concurrent;
using System.Diagnostics;
using System.Text.Json;

// Exact search in the D2-symmetric octagon family
//
//   (+/-a,0), (0,+/-c), (+/-b,+/-d).
//
// Swapping the coordinate axes lets us assume a >= c.  Strict convexity in
// the displayed angular order is equivalent to a>b, c>d, ad+bc>ac.

record Parameters(int A, int B, int C, int D, int[] Profile);

class Local
{
    public long ParameterTriples;
    public long SquareDCandidates;
    public long StrictlyConvexCandidates;
    public long BothAxialAtMostThree;
    public long Counterexamples;
    public int BestMaximum = 8;
    public Parameters? Best;
    public Parameters? Counterexample;
}

sealed class Totals : Local { }

static class Search
{
    static bool IsSquare(long value, out int root)
    {
        if (value <= 0)
        {
            root = 0;
            return false;
        }
        long r = (long)Math.Sqrt(value);
        while (r * r < value) ++r;
        while (r * r > value) --r;
        root = (int)r;
        return r * r == value;
    }

    static int Distinct(params long[] values) => values.Distinct().Count();

    static int Compare(Parameters x, Parameters y)
    {
        int maximumX = x.Profile.Max(), maximumY = y.Profile.Max();
        if (maximumX != maximumY) return maximumX.CompareTo(maximumY);
        int sumX = x.Profile.Sum(), sumY = y.Profile.Sum();
        if (sumX != sumY) return sumX.CompareTo(sumY);
        int[] xx = [x.A, x.B, x.C, x.D], yy = [y.A, y.B, y.C, y.D];
        for (int i = 0; i < 4; ++i)
            if (xx[i] != yy[i]) return xx[i].CompareTo(yy[i]);
        return 0;
    }

    static void Consider(Local local, int a, int b, int c, int d)
    {
        long aa = (long)a * a, bb = (long)b * b;
        long cc = (long)c * c, dd = (long)d * d;
        long nearX = (long)(a - b) * (a - b) + dd;
        long farX = (long)(a + b) * (a + b) + dd;
        int countX = Distinct(4 * aa, aa + cc, nearX, farX);
        if (countX > 3)
            throw new InvalidOperationException("candidate generation missed its promised A collision");

        long nearY = bb + (long)(c - d) * (c - d);
        long farY = bb + (long)(c + d) * (c + d);
        int countY = Distinct(4 * cc, aa + cc, nearY, farY);
        int countDiagonal = Distinct(
            4 * bb, 4 * dd, 4 * (bb + dd), nearX, farX, nearY, farY);
        int[] profile = [countX, countY, countDiagonal];
        var parameters = new Parameters(a, b, c, d, profile);
        int maximum = profile.Max();
        if (local.Best is null || Compare(parameters, local.Best) < 0)
        {
            local.Best = parameters;
            local.BestMaximum = maximum;
        }
        if (countY <= 3) ++local.BothAxialAtMostThree;
        if (maximum < 4)
        {
            ++local.Counterexamples;
            local.Counterexample ??= parameters;
        }
    }

    static Local RunA(int a, int bound)
    {
        var local = new Local();
        long[] possibleD2 = new long[4];
        int[] seenD = new int[4];
        long aa = (long)a * a;
        for (int c = 1; c <= a; ++c)
        {
            long cc = (long)c * c;
            for (int b = 1; b < a; ++b)
            {
                ++local.ParameterTriples;
                long near = (long)(a - b) * (a - b);
                long far = (long)(a + b) * (a + b);
                possibleD2[0] = 4 * aa - near;
                possibleD2[1] = 4 * aa - far;
                possibleD2[2] = aa + cc - near;
                possibleD2[3] = aa + cc - far;
                int seenCount = 0;
                foreach (long d2 in possibleD2)
                {
                    if (!IsSquare(d2, out int d) || d <= 0 || d >= c || d > bound)
                        continue;
                    bool duplicate = false;
                    for (int i = 0; i < seenCount; ++i) duplicate |= seenD[i] == d;
                    if (duplicate) continue;
                    seenD[seenCount++] = d;
                    ++local.SquareDCandidates;
                    if ((long)a * d + (long)b * c <= (long)a * c) continue;
                    ++local.StrictlyConvexCandidates;
                    Consider(local, a, b, c, d);
                }
            }
        }
        return local;
    }

    public static Totals Run(int bound, int threads)
    {
        var totals = new Totals();
        var options = new ParallelOptions { MaxDegreeOfParallelism = threads };
        Parallel.ForEach(Partitioner.Create(2, bound + 1), options, range =>
        {
            var subtotal = new Local();
            for (int a = range.Item1; a < range.Item2; ++a)
            {
                Local local = RunA(a, bound);
                subtotal.ParameterTriples += local.ParameterTriples;
                subtotal.SquareDCandidates += local.SquareDCandidates;
                subtotal.StrictlyConvexCandidates += local.StrictlyConvexCandidates;
                subtotal.BothAxialAtMostThree += local.BothAxialAtMostThree;
                subtotal.Counterexamples += local.Counterexamples;
                if (local.Best is not null &&
                    (subtotal.Best is null || Compare(local.Best, subtotal.Best) < 0))
                {
                    subtotal.Best = local.Best;
                    subtotal.BestMaximum = local.BestMaximum;
                }
                subtotal.Counterexample ??= local.Counterexample;
            }
            lock (totals)
            {
                totals.ParameterTriples += subtotal.ParameterTriples;
                totals.SquareDCandidates += subtotal.SquareDCandidates;
                totals.StrictlyConvexCandidates += subtotal.StrictlyConvexCandidates;
                totals.BothAxialAtMostThree += subtotal.BothAxialAtMostThree;
                totals.Counterexamples += subtotal.Counterexamples;
                if (subtotal.Best is not null &&
                    (totals.Best is null || Compare(subtotal.Best, totals.Best) < 0))
                {
                    totals.Best = subtotal.Best;
                    totals.BestMaximum = subtotal.BestMaximum;
                }
                totals.Counterexample ??= subtotal.Counterexample;
            }
        });
        return totals;
    }
}

static class Program
{
    public static void Main(string[] args)
    {
        int bound = 1000;
        int threads = Environment.ProcessorCount;
        string output = "d2_octagon_bound1000.json";
        for (int i = 0; i < args.Length; ++i)
        {
            if (args[i] == "--bound") bound = int.Parse(args[++i]);
            else if (args[i] == "--threads") threads = int.Parse(args[++i]);
            else if (args[i] == "--output") output = args[++i];
            else throw new ArgumentException($"unknown argument {args[i]}");
        }
        if (bound < 2) throw new ArgumentOutOfRangeException(nameof(bound));

        var stopwatch = Stopwatch.StartNew();
        Totals totals = Search.Run(bound, threads);
        var payload = new
        {
            problem = "Erdos 982, n=8",
            exact = true,
            family = "(+/-a,0), (0,+/-c), (+/-b,+/-d)",
            normalization = "positive integers a,b,c,d <= bound; coordinate-axis interchange fixes a>=c",
            strict_convexity = "a>b, c>d, ad+bc>ac",
            completeness_note = "a counterexample needs <=3 distances at (a,0); its four possible values force d^2 to one of the four enumerated expressions (the remaining possibility c^2=3a^2 has no positive integer solutions)",
            bound,
            threads,
            elapsed_seconds = stopwatch.Elapsed.TotalSeconds,
            parameter_triples = totals.ParameterTriples,
            square_d_candidates = totals.SquareDCandidates,
            strictly_convex_candidates = totals.StrictlyConvexCandidates,
            both_axial_orbits_at_most_three = totals.BothAxialAtMostThree,
            counterexamples = totals.Counterexamples,
            best = totals.Best,
            counterexample = totals.Counterexample
        };
        string json = JsonSerializer
            .Serialize(payload, new JsonSerializerOptions { WriteIndented = true })
            .Replace("\r\n", "\n");
        File.WriteAllText(output, json + "\n");
        Console.WriteLine(json);
    }
}
