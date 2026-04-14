import os
import json
import torch
from graph.graph_builder import GraphBuilder


def build_graph_file(data, user_id):

    raw_dir = "data/raw"
    graph_dir = "graph"

    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(graph_dir, exist_ok=True)

    raw_path = f"{raw_dir}/{user_id}.json"
    graph_path = f"{graph_dir}/{user_id}.pt"
 
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    print("Building graph...")

    builder = GraphBuilder(raw_path)
    graph = builder.build()

    print("Saving graph...")

    torch.save(graph, graph_path)

    print("Graph saved:", graph_path)