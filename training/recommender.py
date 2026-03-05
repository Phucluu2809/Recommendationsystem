import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = os.path.join("data", "raw", "crawled_data.json")

def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def recommend(input_video_id, top_k=5):
    videos = load_data()

    titles = [v.get("title", "") for v in videos]
    ids = [v.get("video_id") for v in videos]

    if input_video_id not in ids:
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(titles)

    index = ids.index(input_video_id)

    cosine_sim = cosine_similarity(
        tfidf_matrix[index],
        tfidf_matrix
    ).flatten()

    similar_indices = cosine_sim.argsort()[::-1]

    results = []
    for idx in similar_indices:
        if ids[idx] == input_video_id:
            continue

        results.append({
            "id": ids[idx],
            "title": titles[idx]
        })

        if len(results) == top_k:
            break

    return results


if __name__ == "__main__":

    videos = load_data()
     
    test_id = "6tmRFODAm3s"

    print("Input video:", test_id,"  ", )

    recs = recommend(test_id, top_k=5)

    print("\nRecommended:")
    for r in recs:
        print(r["id"], "-", r["title"])