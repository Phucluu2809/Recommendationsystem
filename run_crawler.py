from config.config import Config
from crawler.video_crawler import VideoCrawler


def main(): 

    crawler = VideoCrawler(
        topics=Config.TOPICS,
        target_size=Config.TARGET_SIZE
    )

    crawler.run() 


if __name__ == "__main__":
    main()
