// Incremental min-conflicts search for a balanced 5-coloring of K_26.
//
// Objective: the number of pairs (six-set S, color c) for which S contains
// no c-colored edge.  A move recolors one edge.  Scores are maintained as
// break[e] - make[e][new_color], exactly as in WalkSAT.

#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <random>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

static constexpr int N = 26;
static constexpr int C = 5;
static constexpr int E = N * (N - 1) / 2;
static constexpr int K = 15;

struct Search {
  mt19937_64 rng;
  vector<array<int, K>> sets;
  vector<vector<int>> incident;
  array<array<int, N>, N> edge_id{};
  array<pair<int, int>, E> endpoints{};
  array<uint8_t, E> color{};
  array<int, C> color_edges{};
  vector<array<uint8_t, C>> count;
  array<int, E> break_count{};
  array<array<int, C>, E> make_count{};
  vector<int> bad;
  vector<int> bad_pos;
  vector<int> weight;
  long long bad_cost = 0;
  long long steps = 0;

  explicit Search(uint64_t seed) : rng(seed), incident(E) {
    for (auto &row : edge_id) row.fill(-1);
    int ei = 0;
    for (int u = 0; u < N; ++u) for (int v = u + 1; v < N; ++v) {
      edge_id[u][v] = edge_id[v][u] = ei;
      endpoints[ei++] = {u, v};
    }
    array<int, 6> vs{};
    for (vs[0] = 0; vs[0] < N; ++vs[0])
    for (vs[1] = vs[0] + 1; vs[1] < N; ++vs[1])
    for (vs[2] = vs[1] + 1; vs[2] < N; ++vs[2])
    for (vs[3] = vs[2] + 1; vs[3] < N; ++vs[3])
    for (vs[4] = vs[3] + 1; vs[4] < N; ++vs[4])
    for (vs[5] = vs[4] + 1; vs[5] < N; ++vs[5]) {
      array<int, K> es{};
      int p = 0;
      for (int i = 0; i < 6; ++i) for (int j = i + 1; j < 6; ++j)
        es[p++] = edge_id[vs[i]][vs[j]];
      int si = static_cast<int>(sets.size());
      sets.push_back(es);
      for (int e : es) incident[e].push_back(si);
    }
    count.resize(sets.size());
    bad_pos.resize(sets.size() * C, -1);
    weight.resize(sets.size() * C, 1);
  }

  int random_int(int n) { return uniform_int_distribution<int>(0, n - 1)(rng); }
  double random_real() { return uniform_real_distribution<double>(0.0, 1.0)(rng); }

  void initialize(bool affine, bool balanced_init) {
    if (!affine) {
      for (int e = 0; e < E; ++e) color[e] = static_cast<uint8_t>(random_int(C));
    } else {
      // Standard affine plane on vertices (x,y) = divmod(v,5), with all
      // vertical and new-vertex edges randomized.
      vector<int> flexible;
      for (int e = 0; e < E; ++e) {
        auto [u, v] = endpoints[e];
        if (v == 25) {
          flexible.push_back(e);
          continue;
        }
        int x1 = u / 5, y1 = u % 5, x2 = v / 5, y2 = v % 5;
        if (x1 == x2) flexible.push_back(e);
        else {
          int dx = (x2 - x1 + 5) % 5, dy = (y2 - y1 + 5) % 5;
          static constexpr int inv[5] = {0, 1, 3, 2, 4};
          color[e] = static_cast<uint8_t>((dy * inv[dx]) % 5);
        }
      }
      if (balanced_init) {
        shuffle(flexible.begin(), flexible.end(), rng);
        for (int i = 0; i < static_cast<int>(flexible.size()); ++i)
          color[flexible[i]] = static_cast<uint8_t>(i / 15);
      } else {
        for (int e : flexible) color[e] = static_cast<uint8_t>(random_int(C));
      }
    }
    rebuild();
  }

  void add_bad(int code) {
    if (bad_pos[code] != -1) return;
    bad_pos[code] = static_cast<int>(bad.size());
    bad.push_back(code);
    bad_cost += weight[code];
  }
  void remove_bad(int code) {
    int p = bad_pos[code];
    if (p == -1) return;
    int last = bad.back();
    bad[p] = last;
    bad_pos[last] = p;
    bad.pop_back();
    bad_pos[code] = -1;
    bad_cost -= weight[code];
  }

  void rebuild() {
    fill(break_count.begin(), break_count.end(), 0);
    for (auto &a : make_count) a.fill(0);
    fill(bad_pos.begin(), bad_pos.end(), -1);
    bad.clear();
    color_edges.fill(0);
    for (int e = 0; e < E; ++e) ++color_edges[color[e]];
    fill(weight.begin(), weight.end(), 1);
    bad_cost = 0;
    for (int si = 0; si < static_cast<int>(sets.size()); ++si) {
      count[si].fill(0);
      for (int e : sets[si]) ++count[si][color[e]];
      for (int c = 0; c < C; ++c) {
        if (count[si][c] == 0) {
          add_bad(si * C + c);
          for (int e : sets[si]) make_count[e][c] += weight[si * C + c];
        } else if (count[si][c] == 1) {
          for (int e : sets[si]) if (color[e] == c) { break_count[e] += weight[si * C + c]; break; }
        }
      }
    }
  }

  int unique_edge(int si, int c, int except = -1) const {
    for (int e : sets[si]) if (e != except && color[e] == c) return e;
    return -1;
  }

  void move_edge(int e, int nc) {
    int oc = color[e];
    if (oc == nc) return;
    // Changes are expressed relative to the old coloring.  make updates on
    // zero constraints touch all 15 edges and break updates touch the unique
    // edge, keeping each move far cheaper than rescoring candidates.
    for (int si : incident[e]) {
      int ko = count[si][oc], kn = count[si][nc];
      int wo = weight[si * C + oc], wn = weight[si * C + nc];
      if (ko == 1) {
        break_count[e] -= wo;
        add_bad(si * C + oc);
        // After recoloring e, every edge in the set is eligible to make oc.
        for (int f : sets[si]) make_count[f][oc] += wo;
      } else if (ko == 2) {
        int f = unique_edge(si, oc, e);
        if (f < 0) abort();
        break_count[f] += wo;
      }
      if (kn == 0) {
        remove_bad(si * C + nc);
        // Before recoloring e, every edge in the set was eligible to make nc.
        for (int f : sets[si]) make_count[f][nc] -= wn;
        break_count[e] += wn;
      } else if (kn == 1) {
        int f = unique_edge(si, nc, e);
        if (f < 0) abort();
        break_count[f] -= wn;
      }
      --count[si][oc];
      ++count[si][nc];
    }
    color[e] = static_cast<uint8_t>(nc);
    --color_edges[oc];
    ++color_edges[nc];
    ++steps;
  }

  void breakout_bump() {
    // Increase every currently violated clause's weight.  Only make scores
    // are affected because violated clauses have no unique colored edge.
    for (int code : bad) {
      ++weight[code];
      ++bad_cost;
      int si = code / C, c = code % C;
      for (int e : sets[si]) ++make_count[e][c];
    }
  }

  void save_json(const string &path, uint64_t seed, int restart) const {
    ofstream out(path);
    out << "{\n  \"n\": 26,\n  \"colors\": 5,\n  \"seed\": " << seed
        << ",\n  \"restart\": " << restart << ",\n  \"steps\": " << steps << ",\n  \"matrix\": [\n";
    for (int u = 0; u < N; ++u) {
      out << "    [";
      for (int v = 0; v < N; ++v) {
        int x = (u == v ? -1 : static_cast<int>(color[edge_id[u][v]]));
        if (v) out << ", ";
        out << x;
      }
      out << "]" << (u + 1 == N ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
  }
};

int main(int argc, char **argv) {
  uint64_t seed = 617;
  long long max_steps = 2000000;
  int restarts = 50;
  double noise = 0.03;
  bool affine = true;
  bool breakout = false;
  bool swap_moves = false;
  bool balanced_init = false;
  int min_edges = 0;
  string output = "candidate.json";
  for (int i = 1; i < argc; ++i) {
    string a = argv[i];
    auto need = [&]() -> string { if (++i >= argc) { cerr << "missing value\n"; exit(2); } return argv[i]; };
    if (a == "--seed") seed = stoull(need());
    else if (a == "--steps") max_steps = stoll(need());
    else if (a == "--restarts") restarts = stoi(need());
    else if (a == "--noise") noise = stod(need());
    else if (a == "--random-init") affine = false;
    else if (a == "--breakout") breakout = true;
    else if (a == "--swap") swap_moves = true;
    else if (a == "--balanced-init") balanced_init = true;
    else if (a == "--min-edges") min_edges = stoi(need());
    else if (a == "--output") output = need();
    else { cerr << "unknown argument: " << a << "\n"; return 2; }
  }
  Search s(seed);
  cout << "seed=" << seed << " max_steps=" << max_steps << " restarts=" << restarts
       << " noise=" << noise << " init=" << (affine ? "affine" : "random")
       << " breakout=" << breakout
       << " swap=" << swap_moves
       << " balanced_init=" << balanced_init << " min_edges=" << min_edges
       << " six_sets=" << s.sets.size() << "\n" << flush;
  int global_best = 1000000000;
  auto start = chrono::steady_clock::now();
  for (int r = 0; r < restarts; ++r) {
    s.initialize(affine, balanced_init);
    int restart_best = static_cast<int>(s.bad.size());
    if (restart_best < global_best) {
      global_best = restart_best;
      s.save_json(output, seed, r);
      cout << "best=" << global_best << " restart=" << r << " step=0\n" << flush;
    }
    for (long long step = 0; step < max_steps && !s.bad.empty(); ++step) {
      int chosen = -1, best_delta = 1000000000, ties = 0;
      int target = -1;
      bool random_walk = s.random_real() < noise;
      if (breakout) {
        // Search all 1300 genuine recolorings.  A negative score strictly
        // reduces weighted violation cost.  At a local minimum, breakout
        // weights reshape the landscape before choosing again.
        for (int e = 0; e < E; ++e) for (int c = 0; c < C; ++c)
          if (c != s.color[e] && s.color_edges[s.color[e]] > min_edges) {
          int delta = s.break_count[e] - s.make_count[e][c];
          if (delta < best_delta) { best_delta = delta; chosen = e; target = c; ties = 1; }
          else if (delta == best_delta && s.random_int(++ties) == 0) { chosen = e; target = c; }
        }
        if (best_delta >= 0) {
          s.breakout_bump();
          chosen = -1; best_delta = 1000000000; ties = 0;
          for (int e = 0; e < E; ++e) for (int c = 0; c < C; ++c)
            if (c != s.color[e] && s.color_edges[s.color[e]] > min_edges) {
            int delta = s.break_count[e] - s.make_count[e][c];
            if (delta < best_delta) { best_delta = delta; chosen = e; target = c; ties = 1; }
            else if (delta == best_delta && s.random_int(++ties) == 0) { chosen = e; target = c; }
          }
        }
        if (random_walk) {
          int code = s.bad[s.random_int(static_cast<int>(s.bad.size()))];
          int si = code / C;
          target = code % C;
          vector<int> eligible;
          for (int e : s.sets[si]) if (s.color_edges[s.color[e]] > min_edges) eligible.push_back(e);
          if (eligible.empty()) continue;
          chosen = eligible[s.random_int(static_cast<int>(eligible.size()))];
        }
      } else {
        int code = s.bad[s.random_int(static_cast<int>(s.bad.size()))];
        int si = code / C;
        target = code % C;
        if (random_walk) {
          vector<int> eligible;
          for (int e : s.sets[si]) if (s.color_edges[s.color[e]] > min_edges) eligible.push_back(e);
          if (eligible.empty()) continue;
          chosen = eligible[s.random_int(static_cast<int>(eligible.size()))];
        }
        else {
          for (int e : s.sets[si]) {
            if (s.color_edges[s.color[e]] <= min_edges) continue;
            int delta = s.break_count[e] - s.make_count[e][target];
            if (delta < best_delta) { best_delta = delta; chosen = e; ties = 1; }
            else if (delta == best_delta && s.random_int(++ties) == 0) chosen = e;
          }
        }
      }
      if (chosen < 0) continue;
      if (!swap_moves) {
        s.move_edge(chosen, target);
      } else {
        // Preserve all five global color counts: first make the selected
        // missing color, then recolor a different edge of that color back to
        // the displaced color.  The second score is exact in the intermediate
        // state.
        int displaced = s.color[chosen];
        s.move_edge(chosen, target);
        int second = -1, second_delta = 1000000000, second_ties = 0;
        for (int f = 0; f < E; ++f) if (f != chosen && s.color[f] == target) {
          int delta = s.break_count[f] - s.make_count[f][displaced];
          if (delta < second_delta) { second_delta = delta; second = f; second_ties = 1; }
          else if (delta == second_delta && s.random_int(++second_ties) == 0) second = f;
        }
        if (second < 0) abort();
        s.move_edge(second, displaced);
      }
      int now = static_cast<int>(s.bad.size());
      if (now < restart_best) restart_best = now;
      if (now < global_best) {
        global_best = now;
        s.save_json(output, seed, r);
        auto sec = chrono::duration<double>(chrono::steady_clock::now() - start).count();
        cout << "best=" << global_best << " restart=" << r << " step=" << step + 1
             << " total_steps=" << s.steps << " seconds=" << fixed << setprecision(3) << sec << "\n" << flush;
      }
    }
    cout << "restart_done=" << r << " restart_best=" << restart_best
         << " final=" << s.bad.size() << " total_steps=" << s.steps << "\n" << flush;
    if (s.bad.empty()) {
      s.save_json(output, seed, r);
      cout << "FOUND output=" << output << "\n";
      return 0;
    }
  }
  cout << "NOT_FOUND global_best=" << global_best << " total_steps=" << s.steps << "\n";
  return 1;
}
