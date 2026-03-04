import torch
import torch.nn.functional as F
from models.gnn_model import RecommenderGNN


def train():

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    print("=== Loading Graph ===")
    graph = torch.load("graph/video_graph.pt", weights_only=False)
    graph = graph.to(device)

    model = RecommenderGNN(hidden_dim=128).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    edge_type = ('video','similar_to','video')

    if edge_type not in graph.edge_index_dict:
        raise ValueError("No similar_to edge found in graph!")

    edge_index = graph[edge_type].edge_index
    src, dst = edge_index

    print("Training on:", edge_type)
    print("Num edges:", edge_index.shape[1])

    for epoch in range(50):

        model.train()
        optimizer.zero_grad()

        out = model(graph.x_dict, graph.edge_index_dict)
        video_emb = out['video']

        pos_score = F.cosine_similarity(
            video_emb[src],
            video_emb[dst]
        )

        loss = -torch.log(torch.sigmoid(pos_score)).mean()

        loss.backward()
        optimizer.step()

        print(f"Epoch [{epoch+1}/50] Loss: {loss.item():.4f}")

    torch.save(model.state_dict(), "models/gnn_model.pt")
    print("Model saved to models/gnn_model.pt")


if __name__ == "__main__":
    train()