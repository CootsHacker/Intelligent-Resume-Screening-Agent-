from pymilvus import Collection, connections


def insert_resumes_to_data(original_resumeid:str,chunks:list,vectors:list):
    data=[
        {
        "id": f"{original_resumeid}_chunk_{i}",
        "resumeId": original_resumeid,
        "content": chunk,
        "vector": vector
    }
        for i, (chunk, vector) in enumerate(zip(chunks, vectors))
    ]
    return data