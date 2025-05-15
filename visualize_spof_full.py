
import json
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
from matplotlib.lines import Line2D

# Load graph data
with open("graph.json", "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = data["nodes"]
edges_by_stage = data["edges_by_stage"]
spof_levels = data.get("spof_result", {})
node_weights = data.get("node_weights", {})

# Create complete directed graph from all stages
G = nx.DiGraph()
G.add_nodes_from(nodes)
for edge_list in edges_by_stage.values():
    G.add_edges_from(edge_list)

# Generate a fixed layout using Graphviz (left to right)
pos = graphviz_layout(G, prog="dot", args="-Grankdir=LR")

# Define node styles based on SPOF levels
node_colors = []
node_shapes = {}
node_sizes = []
for node in G.nodes():
    level = spof_levels.get(node, "low")
    if level == "absolute":
        node_colors.append("#ff6666")
        node_shapes[node] = "s"
        node_sizes.append(2200)
    elif level == "relative":
        node_colors.append("#ffcc00")
        node_shapes[node] = "o"
        node_sizes.append(2000)
    elif level == "redundant":
        node_colors.append("#66ccff")
        node_shapes[node] = "d"
        node_sizes.append(1800)
    else:
        node_colors.append("#dddddd")
        node_shapes[node] = "o"
        node_sizes.append(1500)

# Define edge style per attack phase
stage_styles = {
    "Reconnaissance": ("solid", "black"),
    "Initial_Access": ("solid", "blue"),
    "Terminal_Access": ("dashed", "gray"),
    "Malware_Infection": ("dashed", "purple"),
    "Command_and_Control": ("solid", "red"),
}
stages = [s for s in ["Reconnaissance", "Initial_Access", "Terminal_Access", "Malware_Infection", "Command_and_Control"] if s in edges_by_stage]

# Static visualization
plt.figure(figsize=(22, 14))
for shape in set(node_shapes.values()):
    shaped_nodes = [n for n in G.nodes() if node_shapes[n] == shape]
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=shaped_nodes,
        node_shape=shape,
        node_color=[node_colors[i] for i, n in enumerate(G.nodes()) if node_shapes[n] == shape],
        node_size=[node_sizes[i] for i, n in enumerate(G.nodes()) if node_shapes[n] == shape]
    )
nx.draw_networkx_labels(G, pos, font_size=9)
for stage, (style, color) in stage_styles.items():
    edges = edges_by_stage.get(stage, [])
    nx.draw_networkx_edges(G, pos, edgelist=edges, style=style, edge_color=color, width=2, arrows=True, arrowsize=20)

# Add legend
legend_elements = [
    Line2D([0], [0], marker='s', color='w', label='SPOF: Absolute', markerfacecolor='#ff6666', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='SPOF: Relative', markerfacecolor='#ffcc00', markersize=15),
    Line2D([0], [0], marker='D', color='w', label='SPOF: Redundant', markerfacecolor='#66ccff', markersize=15),
    Line2D([0], [0], marker='o', color='w', label='SPOF: Low / Normal', markerfacecolor='#dddddd', markersize=15),
    Line2D([0], [0], color='black', lw=2, label='Reconnaissance'),
    Line2D([0], [0], color='blue', lw=2, label='Initial Access'),
    Line2D([0], [0], color='gray', lw=2, linestyle='--', label='Terminal Access'),
    Line2D([0], [0], color='purple', lw=2, linestyle='--', label='Malware Infection'),
    Line2D([0], [0], color='red', lw=2, label='Command & Control'),
]
plt.legend(handles=legend_elements, loc='lower left', fontsize=10)
plt.title("Attack Flow Visualization by Stage", fontsize=16)
plt.axis("off")
plt.tight_layout()
plt.savefig("spof_static_by_stage.png", dpi=300)
plt.show()

# Animated visualization
fig, ax = plt.subplots(figsize=(14, 8))
def draw_frame(i):
    ax.clear()
    G_stage = nx.DiGraph()
    G_stage.add_nodes_from(nodes)
    for j in range(i + 1):
        stage = stages[j]
        edges = edges_by_stage.get(stage, [])
        G_stage.add_edges_from(edges)

    nx.draw_networkx_labels(G_stage, pos, font_size=8, ax=ax)
    for shape in set(node_shapes.values()):
        shaped_nodes = [n for n in G_stage.nodes() if node_shapes[n] == shape]
        nx.draw_networkx_nodes(
            G_stage, pos,
            nodelist=shaped_nodes,
            node_shape=shape,
            node_color=[node_colors[i] for i, n in enumerate(G_stage.nodes()) if node_shapes[n] == shape],
            node_size=[node_sizes[i] for i, n in enumerate(G_stage.nodes()) if node_shapes[n] == shape],
            ax=ax
        )
    for j in range(i + 1):
        stage = stages[j]
        edges = edges_by_stage.get(stage, [])
        style, color = stage_styles.get(stage, ("solid", "black"))
        nx.draw_networkx_edges(
            G_stage, pos,
            edgelist=edges,
            style=style,
            edge_color=color,
            width=2,
            arrows=True,
            arrowsize=20,
            ax=ax
        )
    ax.set_title(f"Stage: {stages[i]}", fontsize=14)
    ax.axis("off")

ani = animation.FuncAnimation(fig, draw_frame, frames=len(stages), interval=1500, repeat=True)
ani.save("attack_stages_by_type_scaled.gif", writer='pillow', fps=1)
