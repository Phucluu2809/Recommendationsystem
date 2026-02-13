"""
Neo4j graph database operations for YouTube video graph.
"""
from typing import Dict, Any, List
from neo4j import GraphDatabase, Driver, ManagedTransaction


class GraphNodes:
    """
    A class to interact with a Neo4j graph database.
    """

    def __init__(self, uri: str, user: str, password: str):
        """
        Initializes the GraphNodes.

        Args:
            uri: The URI of the Neo4j instance.
            user: The username for the Neo4j instance.
            password: The password for the Neo4j instance.
        """
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Closes the database connection.
        """
        self.driver.close()

    def create_video(self, video_data: Dict[str, Any]):
        """
        Creates a Video node in the graph.

        Args:
            video_data: A dictionary containing video data.
        """
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
        """
        Creates a Channel node in the graph.

        Args:
            channel_data: A dictionary containing channel data.
        """
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
        """
        Creates a Topic node in the graph.

        Args:
            topic_name: The name of the topic.
        """
        with self.driver.session() as session:
            session.execute_write(self._create_topic_tx, topic_name)

    @staticmethod
    def _create_topic_tx(tx: ManagedTransaction, topic_name: str):
        query = "MERGE (t:Topic {name: $name})"
        tx.run(query, name=topic_name)

    def create_tag(self, tag_name: str):
        """
        Creates a Tag node in the graph.

        Args:
            tag_name: The name of the tag.
        """
        with self.driver.session() as session:
            session.execute_write(self._create_tag_tx, tag_name)

    @staticmethod
    def _create_tag_tx(tx: ManagedTransaction, tag_name: str):
        query = "MERGE (t:Tag {name: $name})"
        tx.run(query, name=tag_name)

    def connect_channel_video(self, channel_id: str, video_id: str):
        """
        Connects a Channel to a Video.

        Args:
            channel_id: The ID of the channel.
            video_id: The ID of the video.
        """
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
        """
        Connects a Video to a Topic.

        Args:
            video_id: The ID of the video.
            topic: The name of the topic.
        """
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
        """
        Connects a Video to a Tag.

        Args:
            video_id: The ID of the video.
            tag: The name of the tag.
        """
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
        """
        Connects two related videos.

        Args:
            video_id: The ID of the source video.
            related_id: The ID of the related video.
        """
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