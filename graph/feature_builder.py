import torch
from sentence_transformers import SentenceTransformer


class FeatureBuilder:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def build_video_features(self, titles):
        print("Encoding titles...")
        emb = self.model.encode(titles, show_progress_bar=True)
        return torch.tensor(emb, dtype=torch.float)

    def build_dummy_features(self, size):
        return torch.ones((size, 1))
