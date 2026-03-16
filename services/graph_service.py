import os
import json
import torch
from graph.graph_builder import GraphBuilder

RAW_PATH = "data/raw/crawled_data.json"
GRAPH_PATH = "graph/video_graph.pt"


def build_graph_file(data):

    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("graph", exist_ok=True)

    # lưu JSON client gửi
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)

    print("Building graph...")

    builder = GraphBuilder(RAW_PATH)
    graph = builder.build()

    print("Saving graph...")

    torch.save(graph, GRAPH_PATH)

    print("Graph saved at:", GRAPH_PATH)

    return GRAPH_PATH