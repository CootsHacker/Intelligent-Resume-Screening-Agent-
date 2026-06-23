import requests
def embedding_service(prompt):
    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": "all-minilm-l6-v2",
        "prompt": prompt
    }
    response=requests.post(url,json=payload)
    return response.json()["embedding"]
