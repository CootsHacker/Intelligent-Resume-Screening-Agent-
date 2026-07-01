from pymilvus import  AsyncMilvusClient

database_client = AsyncMilvusClient(
    uri="http://localhost:19530"
)
def get_milvus_client():
    return database_client