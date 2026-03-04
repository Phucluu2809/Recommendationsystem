import torch
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, SAGEConv


class RecommenderGNN(torch.nn.Module):
    def __init__(self, hidden_dim=128):
        super().__init__()

        self.conv1 = HeteroConv({
            ('video','has_tag','tag'): SAGEConv((-1, -1), hidden_dim),
            ('video','in_category','category'): SAGEConv((-1, -1), hidden_dim),
            ('video','uploaded_by','channel'): SAGEConv((-1, -1), hidden_dim),
            ('video','published_in','time'): SAGEConv((-1, -1), hidden_dim),
            ('video','similar_to','video'): SAGEConv((-1, -1), hidden_dim),
        }, aggr='sum')

        self.conv2 = HeteroConv({
            key: SAGEConv((-1, -1), hidden_dim)
            for key in self.conv1.convs.keys()
        }, aggr='sum')

    def forward(self, x_dict, edge_index_dict):

        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {k: F.relu(v) for k, v in x_dict.items()}
        x_dict = self.conv2(x_dict, edge_index_dict)

        return x_dict