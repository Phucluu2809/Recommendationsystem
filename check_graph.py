import torch

GRAPH_PATH = "graph/video_graph.pt"


def check_single_relation(data, edge_type, expected_max=1):
    print(f"\nChecking {edge_type} ...")
    edge = data[edge_type].edge_index
    src = edge[0]

    unique, counts = torch.unique(src, return_counts=True)

    print("Min per source:", counts.min().item())
    print("Max per source:", counts.max().item())

    if counts.max().item() > expected_max:
        print("❌ Cardinality ERROR")
    else:
        print("✔ Cardinality OK")


def check_tags(data):
    print("\nChecking tag distribution ...")
    edge = data['video', 'has_tag', 'tag'].edge_index
    video_ids = edge[0]

    unique, counts = torch.unique(video_ids, return_counts=True)

    print("Max tags per video:", counts.max().item())
    print("Mean tags per video:", counts.float().mean().item())

    used_tags = torch.unique(edge[1])
    total_tags = data['tag'].num_nodes

    print("Unused tags:", total_tags - len(used_tags))


def check_similar(data):
    print("\nChecking similar_to ...")
    edge = data['video', 'similar_to', 'video'].edge_index

    # Self-loop
    self_loop = (edge[0] == edge[1]).sum().item()
    print("Self loop count:", self_loop)

    # Reverse edge check
    edges = set()
    for i in range(edge.shape[1]):
        u = int(edge[0][i])
        v = int(edge[1][i])
        edges.add((u, v))

    missing_reverse = 0
    for (u, v) in edges:
        if (v, u) not in edges:
            missing_reverse += 1

    print("Missing reverse edges:", missing_reverse)

    if self_loop == 0:
        print("✔ No self-loop")
    else:
        print("❌ Self-loop found")

    if missing_reverse == 0:
        print("✔ Symmetric")
    else:
        print("⚠ Not fully symmetric")


def check_channel_distribution(data):
    print("\nChecking channel distribution ...")
    edge = data['video', 'uploaded_by', 'channel'].edge_index
    channel_ids = edge[1]

    unique, counts = torch.unique(channel_ids, return_counts=True)

    print("Max videos per channel:", counts.max().item())
    print("Mean videos per channel:", counts.float().mean().item())


def main():
    print("===== LOADING GRAPH =====")
    data = torch.load(GRAPH_PATH, weights_only=False)

    print("\n===== NODE SUMMARY =====")
    for node_type in data.node_types:
        print(node_type, ":", data[node_type].num_nodes)

    print("\n===== EDGE SUMMARY =====")
    for edge_type in data.edge_types:
        print(edge_type, ":", data[edge_type].edge_index.shape[1])

    # Logic checks
    check_single_relation(data, ('video', 'uploaded_by', 'channel'), expected_max=1)
    check_single_relation(data, ('video', 'in_category', 'category'), expected_max=1)
    check_single_relation(data, ('video', 'published_in', 'time'), expected_max=1)

    check_tags(data)
    check_similar(data)
    check_channel_distribution(data)

    print("\n===== CHECK DONE =====")


if __name__ == "__main__":
    main()