import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from networkx.drawing.nx_agraph import graphviz_layout

# Load graph and SPOF result
with open("graph.json", "r", encoding="utf-8") as f:
    graph_data = json.load(f)

with open("spof_result.json", "r", encoding="utf-8") as f:
    spof_result = json.load(f)

# Style mappings
spof_styles = {
    "absolute": {"color": "#e74c3c", "size": 2800, "shape": "s"},  # red square
    "relative": {"color": "#e67e22", "size": 2400, "shape": "D"},  # orange diamond
    "redundant": {"color": "#f1c40f", "size": 2000, "shape": "o"}, # yellow circle
    "low": {"color": "#2ecc71", "size": 1600, "shape": "o"},       # green circle
}

stage_edge_colors = {
    "Reconnaissance": "#95a5a6",         # gray
    "Initial_Access": "#2980b9",         # blue
    "Malware_Infection": "#8e44ad",      # purple
    "Command_and_Control": "#c0392b"     # red
}

# Layout
G_full = nx.DiGraph()
for edges in graph_data["edges_by_stage"].values():
    G_full.add_edges_from(edges)
G_full.add_nodes_from(graph_data["nodes"])
pos = graphviz_layout(G_full, prog="dot", args="-Grankdir=LR")

# Stages
stages = list(graph_data["edges_by_stage"].keys())
fig, ax = plt.subplots(figsize=(20, 12))
plt.style.use('seaborn-v0_8')

def get_node_style(node):
    level = spof_result.get(node, "low")
    return spof_styles.get(level, spof_styles["low"])

def draw_stage(i):
    ax.clear()
    stage = stages[i]
    G_stage = nx.DiGraph()
    G_stage.add_nodes_from(graph_data["nodes"])
    for j in range(i + 1):
        G_stage.add_edges_from(graph_data["edges_by_stage"][stages[j]])

    # Draw nodes with per-node style
    for node in G_stage.nodes():
        style = get_node_style(node)
        nx.draw_networkx_nodes(G_stage, pos, nodelist=[node],
                               node_color=style["color"],
                               node_size=style["size"],
                               node_shape=style["shape"],
                               ax=ax)
    nx.draw_networkx_labels(G_stage, pos, font_size=11, font_weight='bold', ax=ax)

    # Draw edges with stage color
    for j in range(i + 1):
        stage_name = stages[j]
        color = stage_edge_colors.get(stage_name, "black")
        edges = graph_data["edges_by_stage"][stage_name]
        nx.draw_networkx_edges(G_stage, pos, edgelist=edges,
                               edge_color=color, width=2, arrows=True, ax=ax)

    ax.set_title(f"Attack Phase: {stage}", fontsize=18, fontweight='bold', color="#34495e")
    ax.axis("off")

ani = animation.FuncAnimation(fig, draw_stage, frames=len(stages), interval=1500, repeat=True)

# Save GIF
ani.save("spof_animation.gif", writer="pillow", fps=1)
print("Saved styled animation: spof_animation.gif")

plt.show()
