// Exact Kummer-theorem search for Erdos Problem 699.
//
// A prime p divides C(n,k) iff a borrow occurs while subtracting k from n
// in base p, equivalently iff k mod p^a > n mod p^a for some a >= 1.
// This program uses that criterion only; verify_exact.py is an independent
// arbitrary-precision binomial/gcd implementation.

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <string>
#include <tuple>
#include <vector>

static std::vector<int> primes_through(int n) {
  std::vector<bool> is_prime(n + 1, true);
  if (n >= 0) is_prime[0] = false;
  if (n >= 1) is_prime[1] = false;
  for (int p = 2; static_cast<std::int64_t>(p) * p <= n; ++p) {
    if (!is_prime[p]) continue;
    for (int q = p * p; q <= n; q += p) is_prime[q] = false;
  }
  std::vector<int> result;
  for (int p = 2; p <= n; ++p) {
    if (is_prime[p]) result.push_back(p);
  }
  return result;
}

static bool divides_choose(int n, int k, int p) {
  std::int64_t power = p;
  while (power <= n) {
    if (k % power > n % power) return true;
    if (power > n / p) break;
    power *= p;
  }
  return false;
}

int main(int argc, char** argv) {
  const int max_n = argc >= 2 ? std::stoi(argv[1]) : 2000;
  const auto primes = primes_through(max_n);
  std::uint64_t pairs = 0;
  std::vector<std::tuple<int, int, int>> strong_exceptions;
  const auto started = std::chrono::steady_clock::now();

  for (int n = 1; n <= max_n; ++n) {
    const int half = n / 2;
    std::vector<std::vector<unsigned char>> divides(
        primes.size(), std::vector<unsigned char>(half + 1, 0));
    for (std::size_t pi = 0; pi < primes.size() && primes[pi] <= n; ++pi) {
      const int p = primes[pi];
      for (int k = 1; k <= half; ++k) {
        divides[pi][k] = divides_choose(n, k, p);
      }
    }

    for (int i = 1; i < half; ++i) {
      for (int j = i + 1; j <= half; ++j) {
        ++pairs;
        bool weak = false;
        bool strong = false;
        for (std::size_t pi = 0; pi < primes.size() && primes[pi] <= n; ++pi) {
          const int p = primes[pi];
          if (p < i || !divides[pi][i] || !divides[pi][j]) continue;
          weak = true;
          if (p > i) strong = true;
          if (strong) break;
        }
        if (!weak) {
          std::cout << "COUNTEREXAMPLE " << n << ' ' << i << ' ' << j
                    << " after_pairs=" << pairs << '\n';
          return EXIT_FAILURE;
        }
        if (!strong) strong_exceptions.emplace_back(n, i, j);
      }
    }
    if (n % 250 == 0) {
      std::cerr << "checked n=" << n << " pairs=" << pairs << '\n';
    }
  }

  const double elapsed = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - started).count();
  std::cout << "CERT max_n=" << max_n << " pairs=" << pairs
            << " weak_counterexamples=0 strong_exceptions="
            << strong_exceptions.size() << " elapsed_seconds=" << elapsed << '\n';
  for (const auto& [n, i, j] : strong_exceptions) {
    std::cout << "STRONG_EXCEPTION " << n << ' ' << i << ' ' << j << '\n';
  }
  return EXIT_SUCCESS;
}
