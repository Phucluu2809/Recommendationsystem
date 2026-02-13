from graph.graph_builder import GraphBuilder
import torch

RAW_PATH = "data/raw/crawled_data.json"
SAVE_PATH = "graph/video_graph.pt"

print("Building graph...")

builder = GraphBuilder(RAW_PATH)
graph = builder.build()

print("Saving graph...")
torch.save(graph, SAVE_PATH)

print("Graph saved at:", SAVE_PATH)
