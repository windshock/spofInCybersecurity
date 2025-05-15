
import json

def convert_graph_to_cytoscape(graph_path, output_path):
    with open(graph_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)

    nodes = graph_data.get("nodes", [])
    edges_by_stage = graph_data.get("edges_by_stage", {})
    weights = graph_data.get("node_weights", {})

    cy_nodes = [{"data": {"id": n, "weight": weights.get(n, 1.0)}} for n in nodes]

    cy_edges = []
    for stage, edges in edges_by_stage.items():
        for source, target in edges:
            cy_edges.append({
                "data": {
                    "source": source,
                    "target": target,
                    "stage": stage
                }
            })

    cy_graph = {
        "nodes": cy_nodes,
        "edges": cy_edges
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cy_graph, f, indent=2, ensure_ascii=False)

    print(f"변환 완료 → {output_path}")

if __name__ == "__main__":
    convert_graph_to_cytoscape("graph.json", "cyto_graph.json")
