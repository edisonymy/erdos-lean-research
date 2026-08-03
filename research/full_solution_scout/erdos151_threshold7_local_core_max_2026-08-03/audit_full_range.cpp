#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Independent exhaustive filter.  Unlike scan_local_cores.cpp, this scans
// every edge count compatible with degree 5..6, uses no incidence congruence
// pruning, and recognizes links by direct permutation isomorphism rather than
// canonical codes/triangle invariants.

struct Graph {
    int n = 0;
    std::array<uint16_t, 16> adj{};
};

Graph decode_graph6(const std::string& text) {
    Graph graph;
    if (text.empty() || static_cast<unsigned char>(text[0]) == 126)
        throw std::runtime_error("unexpected graph6 header/order");
    graph.n = static_cast<unsigned char>(text[0]) - 63;
    int position = 0;
    for (int column = 1; column < graph.n; ++column) {
        for (int row = 0; row < column; ++row) {
            unsigned char chunk = static_cast<unsigned char>(text[1 + position / 6]) - 63;
            if ((chunk >> (5 - position % 6)) & 1u) {
                graph.adj[row] |= static_cast<uint16_t>(1u << column);
                graph.adj[column] |= static_cast<uint16_t>(1u << row);
            }
            ++position;
        }
    }
    return graph;
}

std::vector<uint16_t> template_graph(int n, const std::vector<std::pair<int, int>>& edges) {
    std::vector<uint16_t> adjacency(n, 0);
    for (auto [a, b] : edges) {
        adjacency[a] |= static_cast<uint16_t>(1u << b);
        adjacency[b] |= static_cast<uint16_t>(1u << a);
    }
    return adjacency;
}

const std::vector<uint16_t> BOWTIE = template_graph(
    5, {{0, 1}, {0, 4}, {1, 4}, {2, 3}, {2, 4}, {3, 4}});
const std::vector<uint16_t> DJS = template_graph(
    5, {{0, 1}, {0, 4}, {1, 2}, {1, 3}, {1, 4}, {2, 3}, {3, 4}});
const std::vector<uint16_t> DUMBBELL = template_graph(
    6, {{0, 1}, {0, 2}, {0, 3}, {1, 2}, {3, 4}, {3, 5}, {4, 5}});

bool isomorphic_by_permutations(const std::vector<uint16_t>& left,
                                const std::vector<uint16_t>& right) {
    if (left.size() != right.size()) return false;
    std::vector<int> image(left.size());
    for (size_t i = 0; i < image.size(); ++i) image[i] = static_cast<int>(i);
    do {
        bool okay = true;
        for (size_t i = 0; i < left.size() && okay; ++i)
            for (size_t j = i + 1; j < left.size(); ++j) {
                bool a = (left[i] >> j) & 1u;
                bool b = (right[image[i]] >> image[j]) & 1u;
                if (a != b) {
                    okay = false;
                    break;
                }
            }
        if (okay) return true;
    } while (std::next_permutation(image.begin(), image.end()));
    return false;
}

char independent_link_type(const Graph& graph, int vertex) {
    std::vector<int> neighbors;
    for (int other = 0; other < graph.n; ++other)
        if ((graph.adj[vertex] >> other) & 1u) neighbors.push_back(other);
    const int order = static_cast<int>(neighbors.size());
    if (order != 5 && order != 6) return 0;
    std::vector<uint16_t> link(order, 0);
    for (int i = 0; i < order; ++i)
        for (int j = i + 1; j < order; ++j)
            if ((graph.adj[neighbors[i]] >> neighbors[j]) & 1u) {
                link[i] |= static_cast<uint16_t>(1u << j);
                link[j] |= static_cast<uint16_t>(1u << i);
            }
    std::vector<int> degree_sequence;
    int degree_sum = 0;
    for (uint16_t row : link) {
        int degree = std::popcount(row);
        degree_sequence.push_back(degree);
        degree_sum += degree;
    }
    std::sort(degree_sequence.begin(), degree_sequence.end(), std::greater<int>());
    const int edges = degree_sum / 2;
    if (order == 5 && edges == 6 &&
        degree_sequence == std::vector<int>({4, 2, 2, 2, 2}) &&
        isomorphic_by_permutations(link, BOWTIE))
        return 'B';
    if (order == 5 && edges == 7 &&
        degree_sequence == std::vector<int>({4, 3, 3, 2, 2}) &&
        isomorphic_by_permutations(link, DJS))
        return 'J';
    if (order == 6 && edges == 7 &&
        degree_sequence == std::vector<int>({3, 3, 2, 2, 2, 2}) &&
        isomorphic_by_permutations(link, DUMBBELL))
        return 'D';
    return 0;
}

bool contains_k5(const Graph& graph) {
    for (uint16_t subset = 0; subset < (1u << graph.n); ++subset) {
        if (std::popcount(subset) != 5) continue;
        bool complete = true;
        for (int v = 0; v < graph.n && complete; ++v) {
            if (!((subset >> v) & 1u)) continue;
            uint16_t rest = static_cast<uint16_t>(subset & ~(1u << v));
            complete = (graph.adj[v] & rest) == rest;
        }
        if (complete) return true;
    }
    return false;
}

std::string independently_classify(const Graph& graph) {
    std::string types;
    for (int v = 0; v < graph.n; ++v) {
        char type = independent_link_type(graph, v);
        if (!type) return "";
        types.push_back(type);
    }
    if (contains_k5(graph)) return "";
    return types;
}

std::string escape_json(const std::string& value) {
    std::string out;
    for (char c : value) {
        if (c == '\\' || c == '"') out.push_back('\\');
        out.push_back(c);
    }
    return out;
}

struct Survivor {
    int n;
    int m;
    std::string graph6;
    std::string types;
};

int run(int argc, char** argv) {
    if (argc != 4) {
        std::cerr << "usage: audit_full_range.exe GENG_PATH MAX_ORDER OUTPUT_JSON\n";
        return 2;
    }
    std::string geng = argv[1];
    int max_order = std::stoi(argv[2]);
    std::string output = argv[3];
    std::map<int, uint64_t> counts_by_order;
    std::map<std::pair<int, int>, uint64_t> counts_by_order_edges;
    std::vector<Survivor> survivors;
    uint64_t fnv = 1469598103934665603ull;

    auto started = std::chrono::steady_clock::now();
    for (int n = 6; n <= max_order; ++n) {
        int min_edges = (5 * n + 1) / 2;
        int max_edges = std::min(3 * n, n * (n - 1) / 2);
        std::ostringstream command;
        command << '"' << geng << '"' << " -cq -d5 -D6 " << n << ' '
                << min_edges << ':' << max_edges << " 2>NUL";
        FILE* pipe = _popen(command.str().c_str(), "r");
        if (!pipe) throw std::runtime_error("could not start geng");
        char buffer[256];
        while (std::fgets(buffer, sizeof(buffer), pipe)) {
            std::string raw(buffer);
            while (!raw.empty() && (raw.back() == '\r' || raw.back() == '\n')) raw.pop_back();
            if (raw.empty() || raw[0] == '>') continue;
            for (unsigned char byte : raw + "\n") {
                fnv ^= byte;
                fnv *= 1099511628211ull;
            }
            Graph graph = decode_graph6(raw);
            int degree_sum = 0;
            for (int v = 0; v < graph.n; ++v) degree_sum += std::popcount(graph.adj[v]);
            int m = degree_sum / 2;
            ++counts_by_order[n];
            ++counts_by_order_edges[{n, m}];
            std::string types = independently_classify(graph);
            if (!types.empty()) survivors.push_back({n, m, raw, types});
        }
        if (_pclose(pipe) != 0) throw std::runtime_error("geng returned nonzero");
        std::cerr << "audit order " << n << ": generated " << counts_by_order[n] << "\n";
    }

    std::ofstream out(output, std::ios::binary);
    out << "{\n  \"schema\": \"erdos151-threshold7-full-range-independent-audit-v1\",\n"
        << "  \"status\": \"COMPLETE\",\n  \"order_min\": 6,\n  \"order_max\": "
        << max_order << ",\n  \"geng_path\": \"" << escape_json(geng) << "\",\n"
        << "  \"method\": \"full degree-5..6 edge ranges; direct permutation link isomorphism; no incidence pruning\",\n"
        << "  \"normalized_graph6_stream_fnv1a64\": \"" << std::hex << fnv << std::dec << "\",\n"
        << "  \"generated_by_order_and_edges\": {";
    bool first = true;
    for (const auto& [key, count] : counts_by_order_edges) {
        if (!first) out << ',';
        first = false;
        out << "\n    \"" << key.first << ':' << key.second << "\": " << count;
    }
    out << "\n  },\n  \"generated_by_order\": {";
    first = true;
    for (const auto& [n, count] : counts_by_order) {
        if (!first) out << ',';
        first = false;
        out << "\n    \"" << n << "\": " << count;
    }
    out << "\n  },\n  \"survivors\": [";
    for (size_t i = 0; i < survivors.size(); ++i) {
        if (i) out << ',';
        out << "\n    {\"n\": " << survivors[i].n << ", \"m\": " << survivors[i].m
            << ", \"graph6\": \"" << survivors[i].graph6 << "\", \"vertex_types\": \""
            << survivors[i].types << "\"}";
    }
    out << "\n  ],\n  \"survivor_count\": " << survivors.size()
        << ",\n  \"elapsed_seconds\": "
        << std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count()
        << "\n}\n";
    std::cout << "audit_generated=";
    uint64_t total = 0;
    for (auto [n, count] : counts_by_order) total += count;
    std::cout << total << " survivors=" << survivors.size() << "\n";
    return 0;
}

int main(int argc, char** argv) {
    try {
        return run(argc, argv);
    } catch (const std::exception& error) {
        std::cerr << "fatal: " << error.what() << "\n";
        return 1;
    }
}
