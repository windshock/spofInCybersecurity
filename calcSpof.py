import json
import networkx as nx
from collections import Counter

def load_graph_from_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    G = nx.DiGraph()
    G.add_nodes_from(data["nodes"])
    G.add_edges_from(data["edges"])
    return G

def analyze_spof(G, source, target, top_n=5):
    paths = list(nx.all_simple_paths(G, source=source, target=target))
    print(f"총 경로 수: {len(paths)}")

    intermediate_nodes = [node for path in paths for node in path[1:-1]]
    counter = Counter(intermediate_nodes)

    print("\n경로상 핵심 노드 (빈도순):")
    top_nodes = counter.most_common(top_n)
    for node, count in top_nodes:
        print(f"  {node}: {count}회 등장 ({count / len(paths) * 100:.1f}%)")

    for node, _ in top_nodes:
        G_temp = G.copy()
        if node in G_temp:
            G_temp.remove_node(node)
            new_paths = list(nx.all_simple_paths(G_temp, source=source, target=target))
            print(f"\n⛔️ '{node}' 제거 시 남는 경로 수: {len(new_paths)} (↓ {(1 - len(new_paths)/len(paths))*100:.1f}%)")

if __name__ == "__main__":
    graph_path = "graph.json"
    source = "VPN_PC"
    target = "Hacker"
    
    G = load_graph_from_json(graph_path)
    analyze_spof(G, source, target)
