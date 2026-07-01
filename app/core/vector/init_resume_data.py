from platform import machine
from fastapi import Depends

from pymilvus import CollectionSchema, FieldSchema, DataType, connections,Collection,utility
from pyxnat.core.schema import datatypes
from sympy.codegen.cxxnodes import using

from app.core.vector.base import get_milvus_client


async def init_resume_collection(client,collection_name):
    if not await client.has_collection(collection_name):
        schema = client.create_schema(auto_id=False)
        schema.add_field(field_name="id", datatype=DataType.VARCHAR, max_length=64, is_primary=True)
        schema.add_field(field_name="resumeId", datatype=DataType.VARCHAR, max_length=64)
        schema.add_field(field_name="content",datatype=DataType.VARCHAR,max_length=3000)
        schema.add_field(field_name="vector",datatype=DataType.FLOAT_VECTOR,dim=1024)
        index_params = client.prepare_index_params()
        index_params.add_index(
            field_name="vector",
            index_type="HNSW",
            metric_type="COSINE",
            params={"M": 16, "efConstruction": 200}
        )
        await client.create_collection(
            collection_name=collection_name,
            schema=schema,
            index_params=index_params
        )
    await client.load_collection(collection_name)
if __name__ == "__main__":
    init_resume_collection()