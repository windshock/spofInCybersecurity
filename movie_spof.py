import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 단계 순서 지정
stages = ["Reconnaissance", "Initial_Access", "Command_and_Control"]

# 데이터 로드
with open("graph.json", "r", encoding="utf-8") as f:
    data = json.load(f)

nodes = data["nodes"]
edges_by_stage = data["edges_by_stage"]

# 전체 그래프 생성 (위치 고정용)
full_G = nx.DiGraph()
full_G.add_nodes_from(nodes)
for stage_edges in edges_by_stage.values():
    full_G.add_edges_from(stage_edges)

from networkx.drawing.nx_agraph import graphviz_layout
pos = graphviz_layout(full_G, prog="dot", args="-Grankdir=LR")

# 애니메이션 준비
fig, ax = plt.subplots(figsize=(18, 10))

def draw_stage(i):
    ax.clear()
    stage = stages[i]
    G = nx.DiGraph()
    G.add_nodes_from(nodes)

    # 현재까지의 모든 간선 누적
    for j in range(i + 1):
        G.add_edges_from(edges_by_stage[stages[j]])

    # 색상 정의
    nx.draw_networkx_nodes(G, pos, node_color="#b0e57c", node_size=1500, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)
    nx.draw_networkx_edges(G, pos, arrows=True, ax=ax)

    ax.set_title(f"공격 단계: {stage}", fontsize=16)
    ax.axis("off")

ani = animation.FuncAnimation(fig, draw_stage, frames=len(stages), interval=1500, repeat=True)

# 파일 저장 (MP4와 GIF 중 선택)
ani.save("attack_stages.mp4", writer='ffmpeg', fps=1)
# ani.save("attack_stages.gif", writer='pillow')

plt.show()
