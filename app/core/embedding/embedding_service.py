import numpy as np
import requests
def embedding_service(prompt):
    url = "http://localhost:11434/api/embed"
    if isinstance(prompt,str):
        prompt=[prompt]
    payload = {
        "model": "mxbai-embed-large",
        "input": prompt
    }
    response=requests.post(url,json=payload)
    if response.status_code == 200:
        json_data = response.json()
        embeddings = json_data.get("embeddings", [])

        if embeddings:
            vectors = [[float(val) for val in vector] for vector in embeddings]
            return vectors
        else:
            print("❌ 向量为空", prompt)
            return None
    else:
        #print(f"❌ 请求失败: {response.status_code}, {response.text}")
        return None

