from platform import machine

from pymilvus import CollectionSchema, FieldSchema, DataType, connections,Collection,utility
def  init_resume_collection():
    connections.connect("default",host="localhost",port="19530")
    fields=[
        #主键
        FieldSchema(name="resumeId",dtype=DataType.VARCHAR,is_primary=True),
        #基础信息用于精确匹配
        FieldSchema(name="name",dtype=DataType.VARCHAR,max_length=100),
        FieldSchema(name="city",dtype=DataType.VARCHAR,max_length=75),
        #用列表存储技能栈
        FieldSchema(name="skills",dtype=DataType.ARRAY,max_length=100,max_capacity=10),
        FieldSchema(name="education",dtype=DataType.JSON),
        FieldSchema(name="projects",dtype=DataType.FLOAT_VECTOR,dim=384),
        FieldSchema(name="awards",dtype=DataType.VARCHAR,max_length=300),
        FieldSchema(name="overallSummary",dtype=DataType.FLOAT_VECTOR,dim=384),
        FieldSchema(name="workExperience",dtype=DataType.FLOAT_VECTOR,dim=384)
    ]
    schema=CollectionSchema(fields,description="Resume Collection")
    collection_name="ai_interviewer_resumes"
    if not utility.has_collection(collection_name):
        collection = Collection(name=collection_name, schema=schema)
    else:
        collection = Collection(name=collection_name)
    index_params = [
        # 为三个向量字段创建 HNSW 索引，使用余弦相似度
        {
            "field_name": "projects",
            "index_type": "HNSW",
            "metric_type": "COSINE",
            "params": {"M": 16, "efConstruction": 200}  # HNSW 核心参数
        },
        {
            "field_name": "overallSummary",
            "index_type": "HNSW",
            "metric_type": "COSINE",
            "params": {"M": 16, "efConstruction": 200}
        },
        {
            "field_name": "workExperience",
            "index_type": "HNSW",
            "metric_type": "COSINE",
            "params": {"M": 16, "efConstruction": 200}
        },
        # 辅助：为常用的城市过滤字段创建倒排索引
        {
            "field_name": "city",
            "index_type": "INVERTED"
        }
    ]
    for param in index_params:
        collection.create_index(field_name=param["field_name"], index_params=param)
    collection.load()
if __name__ == "__main__":
    init_resume_collection()