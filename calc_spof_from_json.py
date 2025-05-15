import json
import networkx as nx
from collections import Counter

def load_graph_from_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    G = nx.DiGraph()
    all_edges = []
    for edge_list in data["edges_by_stage"].values():
        all_edges.extend(edge_list)
    G.add_nodes_from(data["nodes"])
    G.add_edges_from(all_edges)
    return G, data.get("node_weights", {})

def print_table(rows, headers):
    row_format = "{:<25} {:>12} {:>18} {:>18} {:>12}"
    print(row_format.format(*headers))
    print("-" * 90)
    for r in rows:
        print(row_format.format(*r))

def analyze_spof(G, node_weights, sources, target):
    all_paths = []
    for s in sources:
        if s in G and target in G:
            all_paths.extend(list(nx.all_simple_paths(G, source=s, target=target)))
    total_paths = len(all_paths)
    print(f"Total path count: {total_paths}")

    intermediate_nodes = [node for path in all_paths for node in path[1:-1]]
    counter = Counter(intermediate_nodes)

    weighted_map = {}
    for node, count in counter.items():
        weight = node_weights.get(node, 1.0)
        weighted_count = count * weight
        weighted_map[node] = weighted_count

    top_nodes = sorted(weighted_map.items(), key=lambda x: x[1], reverse=True)
    print("\nTop Nodes by Weighted Path Appearance:")
    print_table(
        [(node, f"{counter[node]}", f"{weighted_map[node]:.2f}", f"{(weighted_map[node] / total_paths * 100):.1f}%", "") for node, _ in top_nodes],
        ["Node", "Raw Count", "Weighted Count", "Weighted Ratio", ""]
    )

    spof_result = {}
    table_results = []
    for node, _ in top_nodes:
        G_temp = G.copy()
        if node in G_temp:
            G_temp.remove_node(node)
            new_paths = []
            for s in sources:
                if s in G_temp and target in G_temp:
                    new_paths.extend(list(nx.all_simple_paths(G_temp, source=s, target=target)))
            drop_ratio = (1 - len(new_paths) / total_paths) * 100 if total_paths else 0
            weight_ratio = (weighted_map.get(node, 0) / total_paths) * 100 if total_paths else 0

            if drop_ratio >= 80 or weight_ratio >= 30:
                level = "absolute"
            elif drop_ratio >= 40 or weight_ratio >= 15:
                level = "relative"
            elif drop_ratio >= 10 or weight_ratio >= 5:
                level = "redundant"
            else:
                level = "low"
            spof_result[node] = level

            table_results.append((
                node,
                f"{len(new_paths)}",
                f"↓ {drop_ratio:.1f}%",
                f"{weight_ratio:.1f}%",
                level.upper()
            ))

    print("\nSPOF Impact Analysis (after node removal):")
    print_table(
        table_results,
        ["Node", "Paths Left", "Drop Rate", "Weighted %", "SPOF Level"]
    )

    with open("spof_result.json", "w", encoding="utf-8") as f:
        json.dump(spof_result, f, indent=2, ensure_ascii=False)
    print("\nResult saved to: spof_result.json")

if __name__ == "__main__":
    graph_path = "graph.json"
    sources = ["Hacker_Attacker", "VPN_PC", "OA_PC", "OA_VDI", "firstfloor_pc"]
    target = "Hacker_Internet_forLeak"

    G, weights = load_graph_from_json(graph_path)
    analyze_spof(G, weights, sources, target)
