
import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D
from networkx.drawing.nx_agraph import graphviz_layout

# Set default font (AppleGothic for macOS to support Korean)
plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# Load graph structure and SPOF results
with open("graph.json", "r", encoding="utf-8") as f:
    graph_data = json.load(f)

with open("spof_result.json", "r", encoding="utf-8") as f:
    spof_result = json.load(f)

# Merge all edges for static view
full_G = nx.DiGraph()
full_G.add_nodes_from(graph_data["nodes"])
for edge_list in graph_data["edges_by_stage"].values():
    full_G.add_edges_from(edge_list)

# Define layout (left to right)
pos = graphviz_layout(full_G, prog="dot", args="-Grankdir=LR")

# Color map based on SPOF result
spof_color_map = {
    "absolute": "#ff3333",
    "relative": "#ffcc00",
    "redundant": "#99ccff",
    "low": "#d3d3d3"
}

# Node size map
spof_size_map = {
    "absolute": 2600,
    "relative": 2200,
    "redundant": 1800,
    "low": 1500
}

# Node shape map (currently only affects legend styling)
spof_marker_map = {
    "absolute": "o",
    "relative": "s",
    "redundant": "^",
    "low": "d"
}

def draw_static_graph():
    """Draw the full network with SPOF node highlighting."""
    plt.figure(figsize=(22, 12))
    node_colors = []
    node_sizes = []

    for node in full_G.nodes():
        level = spof_result.get(node, "low")
        node_colors.append(spof_color_map[level])
        node_sizes.append(spof_size_map[level])

    nx.draw_networkx_nodes(full_G, pos, node_color=node_colors, node_size=node_sizes)
    nx.draw_networkx_labels(full_G, pos, font_size=10)

    # Draw edges with distinct styles for terminal, C2, and normal edges
    all_terminal = set(tuple(edge) for edge in graph_data.get("edges_terminal", []))
    cmd_stage = graph_data["edges_by_stage"].get("Command_and_Control", [])
    all_cmd = set(tuple(edge) for edge in cmd_stage)

    for u, v in full_G.edges():
        if (u, v) in all_terminal:
            style, color = "dashed", "gray"
        elif (u, v) in all_cmd:
            style, color = "solid", "red"
        else:
            style, color = "solid", "black"
        nx.draw_networkx_edges(
            full_G, pos,
            edgelist=[(u, v)],
            style=style,
            edge_color=color,
            width=2,
            arrows=True,
            arrowsize=20
        )

    # Legend
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='SPOF: Absolute', markerfacecolor=spof_color_map["absolute"], markersize=15),
        Line2D([0], [0], marker='s', color='w', label='SPOF: Relative', markerfacecolor=spof_color_map["relative"], markersize=15),
        Line2D([0], [0], marker='^', color='w', label='SPOF: Redundant', markerfacecolor=spof_color_map["redundant"], markersize=15),
        Line2D([0], [0], marker='d', color='w', label='SPOF: Low', markerfacecolor=spof_color_map["low"], markersize=15),
        Line2D([0], [0], color='black', lw=2, label='Normal flow'),
        Line2D([0], [0], color='gray', lw=2, linestyle='--', label='Terminal connection'),
        Line2D([0], [0], color='red', lw=2, linestyle='-', label='Command and Control')
    ]
    plt.legend(handles=legend_elements, loc='lower left')
    plt.title("SPOF-Aware Network Visualization (with Terminal Links)", fontsize=16)
    plt.axis('off')
    plt.tight_layout()

    # Save to file
    plt.savefig("spof_static_terminal.png", dpi=300)
    plt.savefig("spof_static_terminal.svg")
    plt.show()

def draw_animated_graph():
    """Draw the animation showing progression across attack stages."""
    stages = list(graph_data["edges_by_stage"].keys())
    fig, ax = plt.subplots(figsize=(22, 12))

    def update(i):
        ax.clear()
        stage = stages[i]
        G = nx.DiGraph()
        G.add_nodes_from(graph_data["nodes"])

        # Add edges for all stages up to current
        for j in range(i + 1):
            G.add_edges_from(graph_data["edges_by_stage"][stages[j]])

        node_colors = []
        node_sizes = []
        for node in G.nodes():
            level = spof_result.get(node, "low")
            node_colors.append(spof_color_map[level])
            node_sizes.append(spof_size_map[level])

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)
        nx.draw_networkx_edges(G, pos, arrows=True, ax=ax)
        ax.set_title(f"Attack Stage: {stage}", fontsize=16)
        ax.axis("off")

    ani = animation.FuncAnimation(fig, update, frames=len(stages), interval=1500, repeat=True)
    ani.save("spof_animated_stages.mp4", writer='ffmpeg', fps=1)
    # ani.save("spof_animated_stages.gif", writer='pillow')
    plt.show()


if __name__ == "__main__":
    draw_static_graph()
    draw_animated_graph()
