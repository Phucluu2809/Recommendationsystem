import sys
from database.neo4j_service import Neo4jGraphService
from services.user_service import UserService
from services.recommendation_service import RecommendationService
from services.personalized_recommender import PersonalizedRecommender

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"


def main():

    db = Neo4jGraphService(URI, USER, PASSWORD)
    user_service = UserService(db)
    rcm_service = RecommendationService(db)
    personal_rcm = PersonalizedRecommender(user_service)
    
    while True:

        print("\n===== VIDEO APP =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose: ").strip()

        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            user_service.register(username, password)

        elif choice == "2":
            username = input("Username: ").strip()
            password = input("Password: ").strip()

            if user_service.login(username, password):
                print("Login success!")

                while True:
                    print("\n1. Watch video")
                    print("2. Recommend (Graph rule-based)")
                    print("3. Logout")

                    sub = input("Choose: ").strip()

                    # -------------------------
                    # WATCH VIDEO
                    # -------------------------
                    if sub == "1":
                        vid = input("Video id (0-1005): ").strip()

                        # Optional: check video exists
                        if not db.video_exists(vid):
                            print("Video does not exist!")
                            continue

                        user_service.add_watch(username, vid)
                        print("Watch recorded!")

                    # -------------------------
                    # RECOMMEND
                    # -------------------------
                    elif sub == "2":

                        recs = personal_rcm.recommend_for_user(username)

                        if not recs:
                            print("No recommendation found.")
                        else:
                            print("\nRecommended videos (Personalized):")
                            for video_id in recs:
                                print(video_id)

                    elif sub == "3":
                        print("Logged out.")
                        break

                    else:
                        print("Invalid choice.")

            else:
                print("Login failed!")

        elif choice == "3":
            print("Goodbye.")
            break

        else:
            print("Invalid choice.")

    db.close()


if __name__ == "__main__":
    main()
