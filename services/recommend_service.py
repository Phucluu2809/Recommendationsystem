import torch
import json
import os
from services.gnn_recommender import GNNRecommender

HISTORY_PATH = os.path.join("data", "history_api.json")


def recommend_videos(graph_path, history):

    os.makedirs("data", exist_ok=True)

    history_data = {"api_user": history}

    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history_data, f)

    recommender = GNNRecommender(graph_path)

    results = recommender.recommend("api_user")

    return results