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
            "CREATE CONSTRAINT time_id IF NOT EXISTS FOR (t:Time) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT user_username IF NOT EXISTS FOR (u:User) REQUIRE u.username IS UNIQUE"
        ]

        with self.driver.session() as session:
            for q in queries:
                session.run(q)

        print("Constraints ready.")
 

    def push_graph(self, graph):

        print("Pushing graph to Neo4j...")

        with self.driver.session() as session:
#video node 
            for video in graph["video"].raw_data:

                session.run(
                    """
                    MERGE (v:Video {id:$id})
                    SET v.title=$title,
                        v.channel_id=$channel_id,
                        v.channel_title=$channel_title,
                        v.category_id=$category_id,
                        v.published_at=$published_at,
                        v.tags=$tags
                    """,
                    id=video["id"],
                    title=video.get("title"),
                    channel_id=video.get("channel_id"),
                    channel_title=video.get("channel_title"),
                    category_id=video.get("category_id", "unknown"),
                    published_at=video.get("published_at"),
                    tags=video.get("tags", [])
                )
        #channel node
            for cid in graph["channel"].channel_ids:
                session.run(
                    """
                    MERGE (c:Channel {id:$id})
                    """,
                    id=cid
                )
            #tag node
            for tag in graph["tag"].tag_names:
                session.run(
                    """
                    MERGE (t:Tag {id:$id})
                    """,
                    id=tag
                )
        #category node
            for cat in graph["category"].category_ids:
                session.run(
                    """
                    MERGE (c:Category {id:$id})
                    """,
                    id=cat
                )

        #time node
            for t in graph["time"].time_buckets:
                session.run(
                    """
                    MERGE (t:Time {id:$id})
                    """,
                    id=t
                )
        
        #create relationship 
            def create_edges(edge_index, rel, src_label, dst_label, src_ids, dst_ids):

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
                        src=str(src_ids[s]),
                        dst=str(dst_ids[d])
                    )

            create_edges(
                graph["video", "uploaded_by", "channel"].edge_index,
                "UPLOADED_BY",
                "Video",
                "Channel",
                graph["video"].video_ids,
                graph["channel"].channel_ids
            )

            create_edges(
                graph["video", "has_tag", "tag"].edge_index,
                "HAS_TAG",
                "Video",
                "Tag",
                graph["video"].video_ids,
                graph["tag"].tag_names
            )

            create_edges(
                graph["video", "in_category", "category"].edge_index,
                "IN_CATEGORY",
                "Video",
                "Category",
                graph["video"].video_ids,
                graph["category"].category_ids
            )

            create_edges(
                graph["video", "published_in", "time"].edge_index,
                "PUBLISHED_IN",
                "Video",
                "Time",
                graph["video"].video_ids,
                graph["time"].time_buckets
            )

            if ("video", "similar_to", "video") in graph.edge_types:
                create_edges(
                    graph["video", "similar_to", "video"].edge_index,
                    "SIMILAR_TO",
                    "Video",
                    "Video",
                    graph["video"].video_ids,
                    graph["video"].video_ids
                )

        print("GRAPH PUSHED SUCCESSFULLY!")

    def video_exists(self, video_id: str) -> bool:
        query = """
        MATCH (v:Video {id:$vid})
        RETURN count(v) > 0 AS exists
        """
        with self.driver.session() as session:
            result = session.run(query, vid=video_id)
            return result.single()["exists"]
    def get_all_videos(self):
        query = """
        MATCH (v:Video)
        RETURN v.id AS id, v.title AS title
        """

        with self.driver.session() as session:
            result = session.run(query)
            return [{"id": r["id"], "title": r["title"]} for r in result]
    def get_videos_by_ids(self, video_ids):
        query = """
        MATCH (v:Video)
        WHERE v.id IN $ids
        RETURN v.id AS id, v.title AS title
        """

        with self.driver.session() as session:
            result = session.run(query, ids=video_ids)
            return [{"id": r["id"], "title": r["title"]} for r in result]

 
 