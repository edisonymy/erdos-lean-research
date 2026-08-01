// Exact search for perfect-cube and perfect-fourth-power subfamilies of
// Erdos problem 366.
//
// Search x <= X for n = x^j - 1 powerful, j=3 or 4. Then n+1=x^j is
// automatically 3-full. We avoid constructing x^j (which may exceed 64 bits)
// by using cyclotomic factorizations.
//
//   x^3 - 1 = (x-1)(x^2+x+1),
//   gcd(x-1, x^2+x+1) = gcd(x-1, 3).
//
// Candidate x-1 values are generated exhaustively from the canonical
// representation of a powerful integer as a^2 b^3 with b squarefree, with
// exact special-prime valuation handling. All residual factorizations are
// exact, using deterministic 64-bit Miller-Rabin and Pollard rho.

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>
#include <intrin.h>

using u64 = std::uint64_t;

static u64 mul_mod(u64 a, u64 b, u64 m) {
  u64 high, remainder;
  u64 low = _umul128(a, b, &high);
  (void)_udiv128(high, low, m, &remainder);
  return remainder;
}

static u64 pow_mod(u64 a, u64 e, u64 m) {
  u64 r = 1;
  while (e) {
    if (e & 1) r = mul_mod(r, a, m);
    a = mul_mod(a, a, m);
    e >>= 1;
  }
  return r;
}

static bool is_prime(u64 n) {
  if (n < 2) return false;
  for (u64 p : {2ULL, 3ULL, 5ULL, 7ULL, 11ULL, 13ULL, 17ULL, 19ULL,
                23ULL, 29ULL, 31ULL, 37ULL}) {
    if (n % p == 0) return n == p;
  }
  u64 d = n - 1, s = 0;
  while ((d & 1) == 0) { d >>= 1; ++s; }
  // Deterministic for all unsigned 64-bit integers.
  for (u64 a : {2ULL, 325ULL, 9375ULL, 28178ULL, 450775ULL,
                9780504ULL, 1795265022ULL}) {
    if (a % n == 0) continue;
    u64 x = pow_mod(a % n, d, n);
    if (x == 1 || x == n - 1) continue;
    bool witness = true;
    for (u64 r = 1; r < s; ++r) {
      x = mul_mod(x, x, n);
      if (x == n - 1) { witness = false; break; }
    }
    if (witness) return false;
  }
  return true;
}

static u64 pollard(u64 n, std::mt19937_64 &rng) {
  if ((n & 1) == 0) return 2;
  if (n % 3 == 0) return 3;
  for (;;) {
    u64 c = std::uniform_int_distribution<u64>(1, n - 1)(rng);
    u64 x = std::uniform_int_distribution<u64>(0, n - 1)(rng);
    u64 y = x, d = 1;
    auto f = [&](u64 z) {
      u64 square = mul_mod(z, z, n);
      return square >= n - c ? square - (n - c) : square + c;
    };
    while (d == 1) {
      x = f(x);
      y = f(f(y));
      u64 delta = x > y ? x - y : y - x;
      d = std::gcd(delta, n);
    }
    if (d != n) return d;
  }
}

static void factor_rec(u64 n, std::vector<u64> &out, std::mt19937_64 &rng) {
  if (n == 1) return;
  if (is_prime(n)) { out.push_back(n); return; }
  u64 d = pollard(n, rng);
  factor_rec(d, out, rng);
  factor_rec(n / d, out, rng);
}

static std::vector<int> small_primes(int bound) {
  std::vector<bool> composite(bound + 1, false);
  std::vector<int> ps;
  for (int p = 2; p <= bound; ++p) if (!composite[p]) {
    ps.push_back(p);
    if (static_cast<long long>(p) * p <= bound)
      for (int q = p * p; q <= bound; q += p) composite[q] = true;
  }
  return ps;
}

static bool powerful(u64 n, const std::vector<int> &trial, std::mt19937_64 &rng) {
  if (n == 1) return true;
  for (u64 p : trial) {
    if (n % p != 0) continue;
    int e = 0;
    do { n /= p; ++e; } while (n % p == 0);
    if (e == 1) return false;
  }
  if (n == 1) return true;
  if (is_prime(n)) return false;
  std::vector<u64> fs;
  factor_rec(n, fs, rng);
  std::sort(fs.begin(), fs.end());
  for (std::size_t i = 0; i < fs.size();) {
    std::size_t j = i + 1;
    while (j < fs.size() && fs[j] == fs[i]) ++j;
    if (j - i == 1) return false;
    i = j;
  }
  return true;
}

static u64 floor_sqrt(u64 n) {
  u64 x = static_cast<u64>(std::sqrt(static_cast<long double>(n)));
  while (x + 1 <= n / (x + 1)) ++x;
  while (x > n / x) --x;
  return x;
}

static u64 floor_cuberoot(u64 n) {
  u64 x = static_cast<u64>(std::cbrt(static_cast<long double>(n)));
  auto cube = [](u64 z) { return z * z * z; };
  while (cube(x + 1) <= n) ++x;
  while (cube(x) > n) --x;
  return x;
}

static std::vector<u64> powerful_up_to(u64 limit) {
  u64 bmax = floor_cuberoot(limit);
  std::vector<bool> squarefree(bmax + 1, true);
  squarefree[0] = false;
  for (u64 p = 2; p * p <= bmax; ++p) {
    u64 p2 = p * p;
    for (u64 b = p2; b <= bmax; b += p2) squarefree[b] = false;
  }
  std::vector<u64> values;
  for (u64 b = 1; b <= bmax; ++b) if (squarefree[b]) {
    u64 b3 = b * b * b;
    u64 amax = floor_sqrt(limit / b3);
    for (u64 a = 1; a <= amax; ++a)
      values.push_back(a * a * b3);
  }
  std::sort(values.begin(), values.end());
  values.erase(std::unique(values.begin(), values.end()), values.end());
  return values;
}

int main(int argc, char **argv) {
  u64 xmax = 4000000000ULL;
  u64 seed = 366;
  int power = 3;
  std::string hits_path = "cube_subfamily_hits.txt";
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    auto need = [&]() -> std::string {
      if (++i >= argc) { std::cerr << "missing argument value\n"; std::exit(2); }
      return argv[i];
    };
    if (a == "--xmax") xmax = std::stoull(need());
    else if (a == "--seed") seed = std::stoull(need());
    else if (a == "--power") power = std::stoi(need());
    else if (a == "--hits") hits_path = need();
    else { std::cerr << "unknown argument " << a << "\n"; return 2; }
  }
  if (xmax > 4294967295ULL) {
    std::cerr << "xmax makes a required quadratic factor overflow uint64\n";
    return 2;
  }
  if (xmax < 2) {
    std::cerr << "xmax must be at least 2\n";
    return 2;
  }

  auto start = std::chrono::steady_clock::now();
  auto base = powerful_up_to(xmax - 1);
  std::vector<u64> candidates;
  if (power == 3) {
    candidates = base;
    // If v_3(x-1)=1, x-1 itself is not powerful but the extra factor 3 in
    // x^2+x+1 repairs it. These are 3*u with u powerful and 3 not dividing u.
    auto third = powerful_up_to((xmax - 1) / 3);
    for (u64 u : third) if (u % 3 != 0) candidates.push_back(3 * u);
  } else if (power == 4) {
    // x^4-1=(x-1)(x+1)(x^2+1). The three factors are coprime away from 2.
    // Thus the odd part of each must be powerful. Generate exactly the x-1
    // whose odd part is powerful.
    for (u64 u : base) if (u & 1) {
      for (u64 a = u; a <= xmax - 1;) {
        candidates.push_back(a);
        if (a > (xmax - 1) / 2) break;
        a *= 2;
      }
    }
  } else {
    std::cerr << "--power must be 3 or 4\n";
    return 2;
  }
  std::sort(candidates.begin(), candidates.end());
  candidates.erase(std::unique(candidates.begin(), candidates.end()), candidates.end());

  auto trial = small_primes(1000);
  std::mt19937_64 rng(seed);
  std::ofstream hits(hits_path);
  if (!hits) {
    std::cerr << "could not open hits output: " << hits_path << "\n";
    return 2;
  }
  u64 checked = 0, found = 0;
  for (u64 xm1 : candidates) {
    u64 x = xm1 + 1;
    if (x > xmax) continue;
    ++checked;
    bool ok = false;
    u64 q = 0, target = 0;
    if (power == 3) {
      q = x * x + x + 1;
      target = (xm1 % 3 == 0) ? q / 3 : q;
      ok = powerful(target, trial, rng);
    } else {
      u64 xp1 = x + 1;
      while ((xp1 & 1) == 0) xp1 >>= 1;
      if (powerful(xp1, trial, rng)) {
        q = x * x + 1;
        target = q;
        while ((target & 1) == 0) target >>= 1;
        ok = powerful(target, trial, rng);
      }
    }
    if (ok) {
      ++found;
      hits << "power=" << power << " x=" << x << " x_minus_1=" << xm1
           << " q=" << q << " adjusted_q=" << target << "\n";
      hits.flush();
    }
  }
  double elapsed = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - start).count();
  std::cout << "power=" << power << " xmax=" << xmax << " seed=" << seed
            << " canonical_powerful_count=" << base.size()
            << " candidates_checked=" << checked << " hits=" << found
            << " elapsed_seconds=" << elapsed << "\n";
  std::cout << "This exhausts only n+1=x^" << power << ", with x<=" << xmax << ".\n";
  return found ? 1 : 0;
}
