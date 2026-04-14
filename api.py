from fastapi import FastAPI
from pydantic import BaseModel
from services.graph_service import build_graph_file
from services.recommend_service import recommend_videos
import uuid
import os
import uvicorn

app = FastAPI()


class GraphRequest(BaseModel):
    data: dict

# {ytb : video}=> server => graph => tên của m
# {người dùng: lịch sử} => mi -> lịch sử + id của m ->rcm 

@app.post("/build_graph")
def build_graph(req: GraphRequest):

    print("API /build_graph called")

    user_id = str(uuid.uuid4())

    build_graph_file(req.data, user_id)
 
    return {"user_id": user_id}


class RecommendRequest(BaseModel):
    user_id: str
    history: list


@app.post("/recommend")
def recommend(req: RecommendRequest):

    graph_path = f"graph/{req.user_id}.pt"

    if not os.path.exists(graph_path):
        return {"error": "graph not found"}

    results = recommend_videos(graph_path, req.history)

    return {"recommendations": results}

 

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)