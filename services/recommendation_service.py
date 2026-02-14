class RecommendationService:

    def __init__(self, neo4j_service):
        self.db = neo4j_service

    def recommend_for_user(self, username, limit=5): 
        query = """
        MATCH (u:User {username:$username})-[:WATCHED]->(v:Video)

        MATCH (v)-[:HAS_TAG|IN_CATEGORY|SIMILAR_TO]->(rec:Video)

        WHERE NOT (u)-[:WATCHED]->(rec)
          AND v <> rec

        RETURN rec.id AS video_id, COUNT(*) AS score
        ORDER BY score DESC
        LIMIT $limit
        """

        with self.db.driver.session() as session:
            result = session.run(
                query,
                username=username,
                limit=limit
            )

            return [(record["video_id"], record["score"]) for record in result]
