import hashlib


class UserService:

    def __init__(self, neo4j_service):
        self.db = neo4j_service

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        hashed = self.hash_password(password)

        query = """
        MERGE (u:User {username:$username})
        ON CREATE SET u.password = $password
        """

        with self.db.driver.session() as session:
            session.run(query, username=username, password=hashed)

        print("User registered.")

    def login(self, username, password):
        hashed = self.hash_password(password)

        query = """
        MATCH (u:User {username:$username, password:$password})
        RETURN u
        """

        with self.db.driver.session() as session:
            result = session.run(query, username=username, password=hashed)
            return result.single() is not None

    def add_watch(self, username, video_id):
        query = """
        MATCH (u:User {username:$username})
        MATCH (v:Video {id:$video_id})
        MERGE (u)-[r:WATCHED]->(v)
        SET r.last_watched = datetime()
        """

        with self.db.driver.session() as session:
            session.run(query, username=username, video_id=str(video_id))

        print("Watch recorded.")
    def get_watch_history(self, username):
        query = """
        MATCH (u:User {username:$username})
        OPTIONAL MATCH (u)-[:WATCHED]->(v:Video)
        RETURN v.id AS video_id
        """

        with self.db.driver.session() as session:
            result = session.run(query, username=username)
            return [record["video_id"] for record in result if record["video_id"] is not None]
    
    def get_recent_watched(self, username, limit=20):
        query = """
        MATCH (u:User {username:$username})-[r:WATCHED]->(v:Video)
        RETURN v.id AS id
        ORDER BY r.last_watched DESC
        LIMIT $limit
        """

        with self.db.driver.session() as session:
            result = session.run(query, username=username, limit=limit)
            return [record["id"] for record in result]