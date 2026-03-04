"""
Neo4j graph database operations for YouTube video graph.
"""
from typing import Dict, Any, List
from neo4j import GraphDatabase, Driver, ManagedTransaction


class GraphNodes:
 
    def __init__(self, uri: str, user: str, password: str):
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_video(self, video_data: Dict[str, Any]): 
        with self.driver.session() as session:
            session.execute_write(self._create_video_tx, video_data)

    @staticmethod
    def _create_video_tx(tx: ManagedTransaction, video_data: Dict[str, Any]):
        query = (
            "MERGE (v:Video {videoId: $video_id}) "
            "SET v.title = $title, "
            "    v.description = $description, "
            "    v.publishedAt = $published_at, "
            "    v.duration = $duration, "
            "    v.viewCount = $view_count, "
            "    v.likeCount = $like_count, "
            "    v.commentCount = $comment_count"
        )
        tx.run(query,
               video_id=video_data.get('id'),
               title=video_data.get('title'),
               description=video_data.get('description'),
               published_at=video_data.get('publishedAt'),
               duration=video_data.get('duration'),
               view_count=video_data.get('viewCount'),
               like_count=video_data.get('likeCount'),
               comment_count=video_data.get('commentCount'))

    def create_channel(self, channel_data: Dict[str, Any]): 
        with self.driver.session() as session:
            session.execute_write(self._create_channel_tx, channel_data)

    @staticmethod
    def _create_channel_tx(tx: ManagedTransaction, channel_data: Dict[str, Any]):
        query = (
            "MERGE (c:Channel {channelId: $channel_id}) "
            "SET c.name = $name, "
            "    c.subscriberCount = $subscriber_count"
        )
        tx.run(query,
               channel_id=channel_data.get('id'),
               name=channel_data.get('title'),
               subscriber_count=channel_data.get('subscriberCount'))

    def create_topic(self, topic_name: str): 
        with self.driver.session() as session:
            session.execute_write(self._create_topic_tx, topic_name)

    @staticmethod
    def _create_topic_tx(tx: ManagedTransaction, topic_name: str):
        query = "MERGE (t:Topic {name: $name})"
        tx.run(query, name=topic_name)

    def create_tag(self, tag_name: str): 
        with self.driver.session() as session:
            session.execute_write(self._create_tag_tx, tag_name)

    @staticmethod
    def _create_tag_tx(tx: ManagedTransaction, tag_name: str):
        query = "MERGE (t:Tag {name: $name})"
        tx.run(query, name=tag_name)

    def connect_channel_video(self, channel_id: str, video_id: str): 
        with self.driver.session() as session:
            session.execute_write(self._connect_channel_video_tx, channel_id, video_id)

    @staticmethod
    def _connect_channel_video_tx(tx: ManagedTransaction, channel_id: str, video_id: str):
        query = (
            "MATCH (c:Channel {channelId: $channel_id}) "
            "MATCH (v:Video {videoId: $video_id}) "
            "MERGE (c)-[:POSTED]->(v)"
        )
        tx.run(query, channel_id=channel_id, video_id=video_id)

    def connect_video_topic(self, video_id: str, topic: str): 
        with self.driver.session() as session:
            session.execute_write(self._connect_video_topic_tx, video_id, topic)

    @staticmethod
    def _connect_video_topic_tx(tx: ManagedTransaction, video_id: str, topic: str):
        query = (
            "MATCH (v:Video {videoId: $video_id}) "
            "MATCH (t:Topic {name: $topic}) "
            "MERGE (v)-[:BELONGS_TO]->(t)"
        )
        tx.run(query, video_id=video_id, topic=topic)

    def connect_video_tag(self, video_id: str, tag: str): 
        with self.driver.session() as session:
            session.execute_write(self._connect_video_tag_tx, video_id, tag)

    @staticmethod
    def _connect_video_tag_tx(tx: ManagedTransaction, video_id: str, tag: str):
        query = (
            "MATCH (v:Video {videoId: $video_id}) "
            "MATCH (t:Tag {name: $tag}) "
            "MERGE (v)-[:HAS_TAG]->(t)"
        )
        tx.run(query, video_id=video_id, tag=tag)

    def connect_related(self, video_id: str, related_id: str): 
        with self.driver.session() as session:
            session.execute_write(self._connect_related_tx, video_id, related_id)

    @staticmethod
    def _connect_related_tx(tx: ManagedTransaction, video_id: str, related_id: str):
        query = (
            "MATCH (v1:Video {videoId: $video_id}) "
            "MATCH (v2:Video {videoId: $related_id}) "
            "MERGE (v1)-[:RELATED_TO]->(v2)"
        )
        tx.run(query, video_id=video_id, related_id=related_id)
    def create_user(self, user_id: str):
        with self.driver.session() as session:
            session.execute_write(self._create_user_tx, user_id)

    @staticmethod
    def _create_user_tx(tx: ManagedTransaction, user_id: str):
        query = "MERGE (u:User {userId: $user_id})"
        tx.run(query, user_id=user_id)
    def connect_user_video(self, user_id: str, video_id: str):
        with self.driver.session() as session:
            session.execute_write(self._connect_user_video_tx, user_id, video_id)

    @staticmethod
    def _connect_user_video_tx(tx: ManagedTransaction, user_id: str, video_id: str):
        query = (
            "MATCH (u:User {userId: $user_id}) "
            "MATCH (v:Video {videoId: $video_id}) "
            "MERGE (u)-[:WATCHED]->(v)"
        )
        tx.run(query, user_id=user_id, video_id=video_id)
