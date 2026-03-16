import json
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.nn import SAGEConv
import networkx as nx
import os
from sklearn.feature_extraction.text import TfidfVectorizer


VIDEO_PATH = os.path.join("data", "raw", "crawled_data.json")
HISTORY_PATH = os.path.join("data", "user_history.json")


def load_videos():
    with open(VIDEO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    if not os.path.exists(HISTORY_PATH) or os.path.getsize(HISTORY_PATH) == 0:
        return {}

    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


class GNN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = SAGEConv(in_channels, hidden_channels)
        self.conv2 = SAGEConv(hidden_channels, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.conv2(x, edge_index)
        return x


class GNNRecommender:

    def __init__(self):
        torch.manual_seed(42)

    def build_graph(self):

        videos = load_videos()
        history = load_history()

        G = nx.Graph()

        for v in videos:
            vid = v["video_id"]
            G.add_node(vid, type="video")

            for tag in v.get("tags", []):
                G.add_node(tag, type="tag")
                G.add_edge(vid, tag)

            if v.get("channel_id"):
                G.add_node(v["channel_id"], type="channel")
                G.add_edge(vid, v["channel_id"])

            if v.get("category_id"):
                G.add_node(v["category_id"], type="category")
                G.add_edge(vid, v["category_id"])

        for user, watched in history.items():
            G.add_node(user, type="user")
            for vid in watched:
                if G.has_node(vid):
                    G.add_edge(user, vid)

        return G

    def create_features(self, G):

        videos = load_videos()

        texts = []
        node_list = list(G.nodes())

        video_text_map = {}

        for v in videos:
            # ghép video với tag lại để tạo nội dung đại diện cho video 
            text = v["title"] + " " + " ".join(v.get("tags", []))
            video_text_map[v["video_id"]] = text

        for node in node_list:
            if node in video_text_map:
                texts.append(video_text_map[node])
            else:
                texts.append("")

        vectorizer = TfidfVectorizer(max_features=128)
        tfidf = vectorizer.fit_transform(texts).toarray()

        return torch.tensor(tfidf, dtype=torch.float32)

    def nx_to_pyg(self, G):

        mapping = {node: i for i, node in enumerate(G.nodes())}
        edges = []

        for u, v in G.edges():
            edges.append([mapping[u], mapping[v]])
            edges.append([mapping[v], mapping[u]])

        if len(edges) == 0:
            return None, None, None

        edge_index = torch.tensor(edges).t().contiguous()
        x = self.create_features(G)

        return Data(x=x, edge_index=edge_index), mapping, list(G.nodes())

    def recommend(self, username, top_k=20, per_video_k=5):

        G = self.build_graph()
        data, mapping, _ = self.nx_to_pyg(G)

        if data is None:
            return []

        model = GNN(data.x.shape[1], 128, 64)
        embeddings = model(data.x, data.edge_index)

        history = load_history().get(username, [])
        if not history:
            return []
        # history = history[-10:0]
        videos = load_videos()
        video_map = {v["video_id"]: v["title"] for v in videos}

        stack = []
 
        for vid in reversed(history):  

            if vid not in mapping:
                continue

            vid_idx = mapping[vid]
            vid_embedding = embeddings[vid_idx]
            scores = []

            for node, idx in mapping.items():
                if G.nodes[node]["type"] == "video" and node != vid:
                    score = F.cosine_similarity(
                        vid_embedding.unsqueeze(0),
                        embeddings[idx].unsqueeze(0)
                    )

                    scores.append((node, score.item()))

            scores.sort(key=lambda x: x[1], reverse=True)
 
            for candidate, _ in scores[:per_video_k]:
                stack.append(candidate)

        cleaned = []
        seen = set()

        for vid in stack:
            if vid in history:
                continue    

            if vid not in seen:
                cleaned.append(vid)
                seen.add(vid)

            if len(cleaned) == top_k:
                break

        return [
            {
                "video_id": vid,
                "title": video_map.get(vid, "")
            }
            for vid in cleaned
        ]