import torch
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from utils.helpers import time_bucket

class EdgeBuilder:

    def __init__(self, node_data):
        self.videos = node_data["videos"]
        self.video_map = node_data["video_map"]
        self.channel_map = node_data["channel_map"]
        self.tag_map = node_data["tag_map"]
        self.category_map = node_data["category_map"]
        self.time_map = node_data["time_map"]
 
    def build_metadata_edges(self, data):

        vc_src, vc_dst = [], []
        vt_src, vt_dst = [], []
        vcat_src, vcat_dst = [], []
        vtime_src, vtime_dst = [], []

        for v in tqdm(self.videos):

            vid = self.video_map[v["video_id"]]

            # Video → Channel
            vc_src.append(vid)
            vc_dst.append(self.channel_map[v["channel_id"]])

            # Video → Tag
            for t in v.get("tags", []):
                t = t.lower()
                if t in self.tag_map:
                    vt_src.append(vid)
                    vt_dst.append(self.tag_map[t])

            # Video → Category
            vcat_src.append(vid)
            vcat_dst.append(self.category_map[v.get("category_id", "unknown")])

            # Video → Time
            year = int(v["published_at"][:4])
            bucket = time_bucket(year)
            vtime_src.append(vid)
            vtime_dst.append(self.time_map[bucket])

        return {
            "uploaded_by": torch.tensor([vc_src, vc_dst]),
            "has_tag": torch.tensor([vt_src, vt_dst]),
            "in_category": torch.tensor([vcat_src, vcat_dst]),
            "published_in": torch.tensor([vtime_src, vtime_dst]),
        }

    def build_similarity_edges(self, embeddings, threshold=0.8):

        print("Building similarity edges...")
        sim = cosine_similarity(embeddings)

        src, dst = [], []

        for i in range(len(sim)):
            for j in range(i + 1, len(sim)):
                if sim[i][j] > threshold:
                    src.append(i)
                    dst.append(j)

        print("Similarity edges:", len(src))

        if not src:
            return None

        return torch.tensor([src, dst])
