import torch
import os
from dotenv import load_dotenv
from database.neo4j_service import Neo4jGraphService
 
load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")

GRAPH_PATH = "graph/video_graph.pt"

print("Loading graph...")
graph = torch.load(GRAPH_PATH, weights_only=False)

print("Connecting to:", URI)

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