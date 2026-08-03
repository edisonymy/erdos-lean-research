#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

#define NOMINMAX
#include <windows.h>
#include <bcrypt.h>
#pragma comment(lib, "bcrypt.lib")

// Exhaustive nauty filter for the threshold-7 local-core bottleneck in
// Erdos #151.  The K4 link type is excluded before generation: a vertex with
// K4 link lies in a K5, contradicting omega(Q) <= 4.  Hence every surviving
// vertex has one of the other three exact links and degree 5 or 6.

struct Sha256 {
    BCRYPT_ALG_HANDLE alg = nullptr;
    BCRYPT_HASH_HANDLE hash = nullptr;
    std::vector<unsigned char> object;
    DWORD hash_len = 0;

    Sha256() {
        if (BCryptOpenAlgorithmProvider(&alg, BCRYPT_SHA256_ALGORITHM, nullptr, 0) != 0)
            throw std::runtime_error("BCryptOpenAlgorithmProvider failed");
        DWORD bytes = 0, object_len = 0;
        if (BCryptGetProperty(alg, BCRYPT_OBJECT_LENGTH,
                              reinterpret_cast<PUCHAR>(&object_len), sizeof(object_len),
                              &bytes, 0) != 0)
            throw std::runtime_error("BCryptGetProperty object length failed");
        if (BCryptGetProperty(alg, BCRYPT_HASH_LENGTH,
                              reinterpret_cast<PUCHAR>(&hash_len), sizeof(hash_len),
                              &bytes, 0) != 0)
            throw std::runtime_error("BCryptGetProperty hash length failed");
        object.resize(object_len);
        if (BCryptCreateHash(alg, &hash, object.data(), object_len, nullptr, 0, 0) != 0)
            throw std::runtime_error("BCryptCreateHash failed");
    }

    void update(const std::string& value) {
        if (BCryptHashData(hash,
                           reinterpret_cast<PUCHAR>(const_cast<char*>(value.data())),
                           static_cast<ULONG>(value.size()), 0) != 0)
            throw std::runtime_error("BCryptHashData failed");
    }

    std::string finish() {
        std::vector<unsigned char> digest(hash_len);
        if (BCryptFinishHash(hash, digest.data(), hash_len, 0) != 0)
            throw std::runtime_error("BCryptFinishHash failed");
        std::ostringstream out;
        out << std::hex << std::setfill('0');
        for (unsigned char byte : digest) out << std::setw(2) << static_cast<int>(byte);
        BCryptDestroyHash(hash);
        BCryptCloseAlgorithmProvider(alg, 0);
        hash = nullptr;
        alg = nullptr;
        return out.str();
    }

    ~Sha256() {
        if (hash) BCryptDestroyHash(hash);
        if (alg) BCryptCloseAlgorithmProvider(alg, 0);
    }
};

struct Graph {
    int n = 0;
    std::array<uint16_t, 16> adj{};
};

Graph parse_graph6(const std::string& line) {
    if (line.empty() || static_cast<unsigned char>(line[0]) == 126)
        throw std::runtime_error("only short graph6 records are supported");
    Graph graph;
    graph.n = static_cast<unsigned char>(line[0]) - 63;
    int bit = 0;
    for (int v = 1; v < graph.n; ++v) {
        for (int u = 0; u < v; ++u, ++bit) {
            int payload = static_cast<unsigned char>(line[1 + bit / 6]) - 63;
            int present = (payload >> (5 - bit % 6)) & 1;
            if (present) {
                graph.adj[u] |= static_cast<uint16_t>(1u << v);
                graph.adj[v] |= static_cast<uint16_t>(1u << u);
            }
        }
    }
    return graph;
}

int edge_count(const Graph& graph) {
    int degree_sum = 0;
    for (int v = 0; v < graph.n; ++v) degree_sum += std::popcount(graph.adj[v]);
    return degree_sum / 2;
}

int local_triangle_count(const Graph& graph, const std::vector<int>& vertices) {
    int count = 0;
    for (size_t i = 0; i < vertices.size(); ++i)
        for (size_t j = i + 1; j < vertices.size(); ++j)
            for (size_t k = j + 1; k < vertices.size(); ++k) {
                int a = vertices[i], b = vertices[j], c = vertices[k];
                if (((graph.adj[a] >> b) & 1u) && ((graph.adj[a] >> c) & 1u) &&
                    ((graph.adj[b] >> c) & 1u))
                    ++count;
            }
    return count;
}

uint32_t labelled_code(const std::vector<uint16_t>& local_adj,
                       const std::vector<int>& permutation) {
    int n = static_cast<int>(local_adj.size());
    uint32_t code = 0;
    int bit = 0;
    for (int j = 1; j < n; ++j) {
        for (int i = 0; i < j; ++i, ++bit) {
            int old_i = permutation[i], old_j = permutation[j];
            if ((local_adj[old_i] >> old_j) & 1u) code |= (1u << bit);
        }
    }
    return code;
}

uint32_t canonical_code(const std::vector<uint16_t>& local_adj) {
    std::vector<int> permutation(local_adj.size());
    for (size_t i = 0; i < permutation.size(); ++i) permutation[i] = static_cast<int>(i);
    uint32_t best = UINT32_MAX;
    do {
        best = std::min(best, labelled_code(local_adj, permutation));
    } while (std::next_permutation(permutation.begin(), permutation.end()));
    return best;
}

std::vector<uint16_t> make_local_graph(int n,
                                       const std::vector<std::pair<int, int>>& edges) {
    std::vector<uint16_t> adj(n, 0);
    for (auto [a, b] : edges) {
        adj[a] |= static_cast<uint16_t>(1u << b);
        adj[b] |= static_cast<uint16_t>(1u << a);
    }
    return adj;
}

const uint32_t BOWTIE_CANON = canonical_code(make_local_graph(
    5, {{0, 1}, {0, 4}, {1, 4}, {2, 3}, {2, 4}, {3, 4}}));
const uint32_t DJS_CANON = canonical_code(make_local_graph(
    5, {{0, 1}, {0, 4}, {1, 2}, {1, 3}, {1, 4}, {2, 3}, {3, 4}}));
const uint32_t DUMBBELL_CANON = canonical_code(make_local_graph(
    6, {{0, 1}, {0, 2}, {0, 3}, {1, 2}, {3, 4}, {3, 5}, {4, 5}}));

char classify_link(const Graph& graph, int v) {
    std::vector<int> neighbors;
    for (int u = 0; u < graph.n; ++u)
        if ((graph.adj[v] >> u) & 1u) neighbors.push_back(u);
    const int degree = static_cast<int>(neighbors.size());
    if (degree != 5 && degree != 6) return 0;

    std::vector<int> link_degrees;
    int degree_sum = 0;
    for (int u : neighbors) {
        int common = std::popcount(static_cast<uint16_t>(graph.adj[v] & graph.adj[u]));
        if (common < 2) return 0;
        link_degrees.push_back(common);
        degree_sum += common;
    }
    std::sort(link_degrees.begin(), link_degrees.end(), std::greater<int>());
    const int link_edges = degree_sum / 2;
    const int link_triangles = local_triangle_count(graph, neighbors);

    char tentative = 0;
    if (degree == 5 && link_edges == 6 && link_triangles == 2 &&
        link_degrees == std::vector<int>({4, 2, 2, 2, 2}))
        tentative = 'B';
    else if (degree == 5 && link_edges == 7 && link_triangles == 3 &&
             link_degrees == std::vector<int>({4, 3, 3, 2, 2}))
        tentative = 'J';
    else if (degree == 6 && link_edges == 7 && link_triangles == 2 &&
             link_degrees == std::vector<int>({3, 3, 2, 2, 2, 2}))
        tentative = 'D';
    else
        return 0;

    // Exact isomorphism check, independent of the degree/triangle invariant.
    std::vector<uint16_t> local_adj(degree, 0);
    for (int i = 0; i < degree; ++i)
        for (int j = i + 1; j < degree; ++j)
            if ((graph.adj[neighbors[i]] >> neighbors[j]) & 1u) {
                local_adj[i] |= static_cast<uint16_t>(1u << j);
                local_adj[j] |= static_cast<uint16_t>(1u << i);
            }
    uint32_t canonical = canonical_code(local_adj);
    if ((tentative == 'B' && canonical != BOWTIE_CANON) ||
        (tentative == 'J' && canonical != DJS_CANON) ||
        (tentative == 'D' && canonical != DUMBBELL_CANON))
        throw std::runtime_error("local invariant admitted a non-template graph");
    return tentative;
}

bool has_k5(const Graph& graph) {
    const uint16_t limit = static_cast<uint16_t>(1u << graph.n);
    for (uint16_t set = 0; set < limit; ++set) {
        if (std::popcount(set) != 5) continue;
        bool clique = true;
        for (int v = 0; v < graph.n && clique; ++v) {
            if (!((set >> v) & 1u)) continue;
            uint16_t others = static_cast<uint16_t>(set & ~(1u << v));
            if ((graph.adj[v] & others) != others) clique = false;
        }
        if (clique) return true;
    }
    return false;
}

std::string classify_graph(const Graph& graph) {
    std::string profile;
    for (int v = 0; v < graph.n; ++v) {
        char type = classify_link(graph, v);
        if (!type) return "";
        profile.push_back(type);
    }
    if (has_k5(graph))
        throw std::runtime_error("exact allowed links unexpectedly admitted a K5");
    return profile;
}

std::set<int> allowed_edge_counts(int n) {
    std::set<int> counts;
    for (int b = 0; b <= n; ++b) {
        for (int j = 0; j <= n - b; ++j) {
            int d = n - b - j;
            if ((b + j) % 2 != 0) continue;                // degree handshake
            if ((6 * b + 7 * j + 7 * d) % 3 != 0) continue; // triangle incidence
            if ((2 * b + 3 * j + 2 * d) % 4 != 0) continue; // K4 incidence
            counts.insert((5 * (b + j) + 6 * d) / 2);
        }
    }
    return counts;
}

std::string json_escape(const std::string& value) {
    std::ostringstream out;
    for (char c : value) {
        if (c == '\\' || c == '"') out << '\\' << c;
        else if (c == '\n') out << "\\n";
        else if (c == '\r') out << "\\r";
        else out << c;
    }
    return out.str();
}

struct Survivor {
    int n;
    int m;
    std::string graph6;
    std::string vertex_types;
};

int run_main(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "usage: scan_local_cores.exe GENG_PATH MAX_ORDER OUTPUT_JSON\n";
        return 2;
    }
    const std::string geng = argv[1];
    const int max_order = std::stoi(argv[2]);
    const std::string output = argv[3];
    Sha256 stream_hash;
    std::map<std::pair<int, int>, uint64_t> generated;
    std::map<int, uint64_t> generated_by_order;
    std::map<int, uint64_t> survivors_by_order;
    std::vector<Survivor> survivors;

    ULONGLONG started = GetTickCount64();
    for (int n = 6; n <= max_order; ++n) {
        for (int m : allowed_edge_counts(n)) {
            if (m < (5 * n + 1) / 2 || m > 3 * n || m > n * (n - 1) / 2) continue;
            std::ostringstream command;
            command << '"' << geng << '"' << " -cq -d5 -D6 " << n << ' ' << m << ':' << m
                    << " 2>NUL";
            FILE* pipe = _popen(command.str().c_str(), "r");
            if (!pipe) throw std::runtime_error("_popen failed for geng");
            char buffer[256];
            while (std::fgets(buffer, sizeof(buffer), pipe)) {
                std::string raw(buffer);
                while (!raw.empty() && (raw.back() == '\n' || raw.back() == '\r')) raw.pop_back();
                if (raw.empty() || raw[0] == '>') continue;
                stream_hash.update(raw + "\n");
                ++generated[{n, m}];
                ++generated_by_order[n];
                Graph graph = parse_graph6(raw);
                if (graph.n != n || edge_count(graph) != m)
                    throw std::runtime_error("graph6 parse/order/size mismatch");
                std::string profile = classify_graph(graph);
                if (!profile.empty()) {
                    survivors.push_back({n, m, raw, profile});
                    ++survivors_by_order[n];
                }
            }
            int code = _pclose(pipe);
            if (code != 0) throw std::runtime_error("geng returned nonzero status");
        }
        std::cerr << "order " << n << ": generated " << generated_by_order[n]
                  << ", local cores " << survivors_by_order[n] << "\n";
    }
    const std::string digest = stream_hash.finish();
    double elapsed = (GetTickCount64() - started) / 1000.0;

    std::ofstream out(output, std::ios::binary);
    if (!out) throw std::runtime_error("could not open output JSON");
    out << "{\n"
        << "  \"schema\": \"erdos151-threshold7-local-core-scan-v1\",\n"
        << "  \"status\": \"COMPLETE\",\n"
        << "  \"order_min\": 6,\n"
        << "  \"order_max\": " << max_order << ",\n"
        << "  \"geng_path\": \"" << json_escape(geng) << "\",\n"
        << "  \"normalized_graph6_stream_sha256\": \"" << digest << "\",\n"
        << "  \"analytic_preprocessing\": \"K4 links imply a K5 and are excluded by omega<=4; remaining exact link types force degree 5 or 6; handshake, triangle-incidence, and K4-incidence congruences restrict edge counts\",\n"
        << "  \"generated_by_order_and_edges\": {\n";
    bool first = true;
    for (const auto& [key, count] : generated) {
        if (!first) out << ",\n";
        first = false;
        out << "    \"" << key.first << ":" << key.second << "\": " << count;
    }
    out << "\n  },\n  \"generated_by_order\": {";
    first = true;
    for (int n = 6; n <= max_order; ++n) {
        if (!first) out << ',';
        first = false;
        out << "\n    \"" << n << "\": " << generated_by_order[n];
    }
    out << "\n  },\n  \"survivors_by_order\": {";
    first = true;
    for (int n = 6; n <= max_order; ++n) {
        if (!first) out << ',';
        first = false;
        out << "\n    \"" << n << "\": " << survivors_by_order[n];
    }
    out << "\n  },\n  \"survivors\": [";
    for (size_t i = 0; i < survivors.size(); ++i) {
        const auto& row = survivors[i];
        if (i) out << ',';
        out << "\n    {\"n\": " << row.n << ", \"m\": " << row.m
            << ", \"graph6\": \"" << row.graph6 << "\", \"vertex_types\": \""
            << row.vertex_types << "\"}";
    }
    out << "\n  ],\n  \"survivor_count\": " << survivors.size()
        << ",\n  \"elapsed_seconds\": " << std::fixed << std::setprecision(3) << elapsed << "\n}\n";
    std::cout << "generated=";
    uint64_t total = 0;
    for (auto [n, count] : generated_by_order) total += count;
    std::cout << total << " survivors=" << survivors.size() << " sha256=" << digest
              << " elapsed=" << elapsed << "\n";
    return 0;
}

int main(int argc, char** argv) {
    try {
        return run_main(argc, argv);
    } catch (const std::exception& error) {
        std::cerr << "fatal: " << error.what() << "\n";
        return 1;
    }
}
