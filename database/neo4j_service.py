from neo4j import GraphDatabase


class Neo4jGraphService:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    def close(self):
        self.driver.close()
 
    def clear_database(self):
        print("Clearing old graph...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared.")
 
    def create_constraints(self):

        print("Creating constraints...")

        queries = [
            "CREATE CONSTRAINT video_id IF NOT EXISTS FOR (v:Video) REQUIRE v.id IS UNIQUE",
            "CREATE CONSTRAINT channel_id IF NOT EXISTS FOR (c:Channel) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT tag_id IF NOT EXISTS FOR (t:Tag) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT category_id IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT time_id IF NOT EXISTS FOR (t:Time) REQUIRE t.id IS UNIQUE"
        ]

        with self.driver.session() as session:
            for q in queries:
                session.run(q)

        print("Constraints ready.")
 
    def push_graph(self, graph):

        print("Pushing graph to Neo4j...")

        with self.driver.session() as session:
 
            print("Creating Video nodes...")
            for i in range(graph["video"].num_nodes):
                session.run("MERGE (v:Video {id:$id})", id=str(i))

            print("Creating Channel nodes...")
            for i in range(graph["channel"].num_nodes):
                session.run("MERGE (c:Channel {id:$id})", id=str(i))

            print("Creating Tag nodes...")
            for i in range(graph["tag"].num_nodes):
                session.run("MERGE (t:Tag {id:$id})", id=str(i))

            print("Creating Category nodes...")
            for i in range(graph["category"].num_nodes):
                session.run("MERGE (c:Category {id:$id})", id=str(i))

            print("Creating Time nodes...")
            for i in range(graph["time"].num_nodes):
                session.run("MERGE (t:Time {id:$id})", id=str(i))
 
            def create_edges(edge_index, rel, src_label, dst_label):

                if edge_index is None:
                    return

                src, dst = edge_index

                for s, d in zip(src.tolist(), dst.tolist()):
                    session.run(
                        f"""
                        MATCH (a:{src_label} {{id:$src}})
                        MATCH (b:{dst_label} {{id:$dst}})
                        MERGE (a)-[:{rel}]->(b)
                        """,
                        src=str(s),
                        dst=str(d)
                    )

            print("Creating relationships...")

            create_edges(
                graph["video", "uploaded_by", "channel"].edge_index,
                "UPLOADED_BY",
                "Video",
                "Channel"
            )

            create_edges(
                graph["video", "has_tag", "tag"].edge_index,
                "HAS_TAG",
                "Video",
                "Tag"
            )

            create_edges(
                graph["video", "in_category", "category"].edge_index,
                "IN_CATEGORY",
                "Video",
                "Category"
            )

            create_edges(
                graph["video", "published_in", "time"].edge_index,
                "PUBLISHED_IN",
                "Video",
                "Time"
            )

            if ("video", "similar_to", "video") in graph.edge_types:
                create_edges(
                    graph["video", "similar_to", "video"].edge_index,
                    "SIMILAR_TO",
                    "Video",
                    "Video"
                )

        print("GRAPH PUSHED SUCCESSFULLY!")
