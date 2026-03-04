import torch
import os
from models.gnn_model import RecommenderGNN


def build():

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    graph = torch.load("graph/video_graph.pt", weights_only=False)
    graph = graph.to(device)

    model = RecommenderGNN(hidden_dim=128).to(device)
    model.load_state_dict(torch.load("models/gnn_model.pt"))
    model.eval()

    with torch.no_grad():
        out = model(graph.x_dict, graph.edge_index_dict)
        video_emb = out['video']

    os.makedirs("embeddings", exist_ok=True)

    torch.save(video_emb.cpu(), "embeddings/video_embeddings.pt")
    print("Video embeddings saved to embeddings/video_embeddings.pt")


if __name__ == "__main__":
    build()