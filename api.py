from fastapi.responses import FileResponse
from services.graph_service import build_graph_file
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import json
from services.recommend_service import recommend_videos
import os
import uvicorn

app = FastAPI()


class GraphRequest(BaseModel):
    data: dict


@app.post("/build_graph")
def build_graph(req: GraphRequest):

    path = build_graph_file(req.data)

    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename="video_graph.pt"
    )


class HistoryRequest(BaseModel):
    history: list


@app.post("/recommend")
async def recommend(
    graph_file: UploadFile = File(...),
    history: str = File(...)
):

    history_list = json.loads(history)

    graph_bytes = await graph_file.read()

    results = recommend_videos(graph_bytes, history_list)

    return {"recommendations": results}

 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)