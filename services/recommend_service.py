import torch
import io
import json
import os
from services.gnn_recommender import GNNRecommender


GRAPH_PATH = "graph/video_graph.pt"
HISTORY_PATH = os.path.join("data", "history_api.json")


def recommend_videos(graph_bytes, history):

    os.makedirs("graph", exist_ok=True)
    os.makedirs("data", exist_ok=True)
 
    with open(GRAPH_PATH, "wb") as f:
        f.write(graph_bytes)
 
    history_data = {"api_user": history}

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history_data, f)

    recommender = GNNRecommender()

    results = recommender.recommend("api_user")

    return results