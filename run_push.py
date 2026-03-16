import torch
from database.neo4j_service import Neo4jGraphService


URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "22228888"

GRAPH_PATH = "graph/video_graph.pt"


print("Loading graph...")
graph = torch.load(GRAPH_PATH, weights_only=False)


neo = Neo4jGraphService(
    uri=URI,
    user=USER,
    password=PASSWORD
)

neo.clear_database()
neo.create_constraints()
neo.push_graph(graph)
neo.close()

print("Graph pushed to Neo4j successfully!")
