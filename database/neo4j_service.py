from neo4j import GraphDatabase


class Neo4jGraphService:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # -------------------------
    # CLEAR DATABASE
    # -------------------------

    def clear_database(self):
        print("Clearing old graph...")
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared.")

    # -------------------------
    # CREATE CONSTRAINTS
    # -------------------------

    def create_constraints(self):

        print("Creating constraints...")

        queries = [
            "CREATE CONSTRAINT video_id IF NOT EXISTS FOR (v:Video) REQUIRE v.id IS UNIQUE",
            "CREATE CONSTRAINT channel_id IF NOT EXISTS FOR (c:Channel) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT tag_id IF NOT EXISTS FOR (t:Tag) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT category_id IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT time_id IF NOT EXISTS FOR (t:Time) REQUIRE t.id IS UNIQUE",
        ]

        with self.driver.session() as session:
            for q in queries:
                session.run(q)

        print("Constraints ready.")

    # -------------------------
    # PUSH GRAPH
    # -------------------------

    def push_graph(self, graph):

        print("Pushing graph to Neo4j...")

        with self.driver.session() as session:

            # -------------------------
            # VIDEO NODES
            # -------------------------

            videos = []

            for i, video in enumerate(graph["video"].raw_data):

                vid = graph["video"].video_ids[i]

                if vid is None:
                    continue

                videos.append({
                    "id": str(vid),
                    "title": video.get("title"),
                    "channel_id": video.get("channel_id"),
                    "channel_title": video.get("channel_title"),
                    "category_id": video.get("category_id", "unknown"),
                    "published_at": video.get("published_at"),
                    "tags": video.get("tags", [])
                })

            session.run("""
            UNWIND $videos AS v
            MERGE (vid:Video {id:v.id})
            SET vid.title = v.title,
                vid.channel_id = v.channel_id,
                vid.channel_title = v.channel_title,
                vid.category_id = v.category_id,
                vid.published_at = v.published_at,
                vid.tags = v.tags
            """, videos=videos)

            # -------------------------
            # CHANNEL NODES
            # -------------------------

            session.run("""
            UNWIND $ids AS id
            MERGE (:Channel {id:id})
            """, ids=[str(i) for i in graph["channel"].channel_ids])

            # -------------------------
            # TAG NODES
            # -------------------------

            session.run("""
            UNWIND $ids AS id
            MERGE (:Tag {id:id})
            """, ids=[str(i) for i in graph["tag"].tag_names])

            # -------------------------
            # CATEGORY NODES
            # -------------------------

            session.run("""
            UNWIND $ids AS id
            MERGE (:Category {id:id})
            """, ids=[str(i) for i in graph["category"].category_ids])

            # -------------------------
            # TIME NODES
            # -------------------------

            session.run("""
            UNWIND $ids AS id
            MERGE (:Time {id:id})
            """, ids=[str(i) for i in graph["time"].time_buckets])

            # -------------------------
            # EDGE CREATOR
            # -------------------------

            def create_edges(edge_index, rel, src_label, dst_label, src_ids, dst_ids):

                if edge_index is None:
                    return

                src, dst = edge_index

                edges = []

                for s, d in zip(src.tolist(), dst.tolist()):

                    if s >= len(src_ids) or d >= len(dst_ids):
                        continue

                    edges.append({
                        "src": str(src_ids[s]),
                        "dst": str(dst_ids[d])
                    })

                session.run(f"""
                UNWIND $edges AS e
                MATCH (a:{src_label} {{id:e.src}})
                MATCH (b:{dst_label} {{id:e.dst}})
                MERGE (a)-[:{rel}]->(b)
                """, edges=edges)

            # -------------------------
            # RELATIONSHIPS
            # -------------------------

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

    # -------------------------
    # QUERY FUNCTIONS
    # -------------------------

    def video_exists(self, video_id):

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