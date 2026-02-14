import torch
from database.neo4j_service import Neo4jGraphService
from database.user_service import UserService
from services.recommendation_service import RecommendationService

 
URI = "bolt://localhost:7687"    
USER = "neo4j"
PASSWORD = "12345678"


def main():

    db = Neo4jGraphService(URI, USER, PASSWORD)
    user_service = UserService(db)
    rcm_service = RecommendationService(db)

    while True:

        print("\n===== VIDEO APP =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose: ")

        if choice == "1":
            username = input("Username: ")
            password = input("Password: ")
            user_service.register(username, password)

        elif choice == "2":
            username = input("Username: ")
            password = input("Password: ")

            if user_service.login(username, password):
                print("Login success!")

                while True:
                    print("\n1. Watch video")
                    print("2. Recommend")
                    print("3. Logout")

                    sub = input("Choose: ")

                    if sub == "1":
                        vid = input("Video id (0-1005): ")
                        user_service.add_watch(username, vid)

                    elif sub == "2":
                        recs = rcm_service.recommend_for_user(username)
                        print("\nRecommended videos:")
                        for r in recs:
                            print("Video:", r[0], "Score:", r[1])

                    elif sub == "3":
                        break

            else:
                print("Login failed!")

        elif choice == "3":
            break

    db.close()


if __name__ == "__main__":
    main()
