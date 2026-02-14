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
        MERGE (u)-[:WATCHED]->(v)
        """

        with self.db.driver.session() as session:
            session.run(query, username=username, video_id=str(video_id))

        print("Watch recorded.")
    