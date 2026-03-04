import torch
from torch_geometric.data import HeteroData

from graph.node_builder import NodeBuilder
from graph.feature_builder import FeatureBuilder
from graph.edge_builder import EdgeBuilder


class GraphBuilder:

    def __init__(self, data_path):
        self.data_path = data_path
        self.graph = HeteroData()

    def build(self):

        # node
        node_builder = NodeBuilder(self.data_path)
        node_data = node_builder.build()

        # feature
        feature_builder = FeatureBuilder()

        video_x = feature_builder.build_video_features(
            node_data["titles"]
        )

        self.graph["video"].x = video_x
        self.graph["channel"].x = feature_builder.build_dummy_features(
            len(node_data["channel_map"])
        )
        self.graph["tag"].x = feature_builder.build_dummy_features(
            len(node_data["tag_map"])
        )
        self.graph["category"].x = feature_builder.build_dummy_features(
            len(node_data["category_map"])
        )
        self.graph["time"].x = feature_builder.build_dummy_features(
            len(node_data["time_map"])
        )

        #edge
        edge_builder = EdgeBuilder(node_data)

        metadata_edges = edge_builder.build_metadata_edges(node_data)

        self.graph["video", "uploaded_by", "channel"].edge_index = metadata_edges["uploaded_by"]
        self.graph["video", "has_tag", "tag"].edge_index = metadata_edges["has_tag"]
        self.graph["video", "in_category", "category"].edge_index = metadata_edges["in_category"]
        self.graph["video", "published_in", "time"].edge_index = metadata_edges["published_in"]

        similarity_edges = edge_builder.build_similarity_edges(
            video_x.numpy()
        )

        if similarity_edges is not None:
            self.graph["video", "similar_to", "video"].edge_index = similarity_edges
 
        self.graph["video"].raw_data = node_data["videos"]
        self.graph["video"].video_ids = node_data["video_ids"]

        self.graph["channel"].channel_ids = list(node_data["channel_map"].keys())
        self.graph["tag"].tag_names = list(node_data["tag_map"].keys())
        self.graph["category"].category_ids = list(node_data["category_map"].keys())
        self.graph["time"].time_buckets = list(node_data["time_map"].keys())
 
        torch.save(self.graph, "graph/video_graph.pt")

        print("\n🔥 GRAPH BUILT SUCCESSFULLY!")
        print(self.graph)

        return self.graph
    def build_user_edges(self, watched_data):

        u_src, u_dst = [], []

        for username, video_id in watched_data:
            if username in self.user_map and video_id in self.video_map:
                u_src.append(self.user_map[username])
                u_dst.append(self.video_map[video_id])

        return {
            ('user','watched','video'):
                torch.tensor([u_src, u_dst])
        }