from platform import machine

from pymilvus import CollectionSchema, FieldSchema, DataType, connections,Collection

connections.connect("default",host="localhost",port="19530")
fields=[
    #主键
    FieldSchema(name="resumeId",dtype=DataType.VARCHAR,is_primary=True),
    #基础信息用于精确匹配
    FieldSchema(name="name",dtype=DataType.VARCHAR,max_length=100),
    FieldSchema(name="city",dtype=DataType.VARCHAR,max_length=75),
    #用列表存储技能栈
    FieldSchema(name="skills",dtype=DataType.ARRAY,max_length=100,max_capacity=10),
    FieldSchema(name="education",dtype=DataType.ARRAY,max_length=900,max_capacity=10),
    FieldSchema(name="projects",dtype=DataType.VARCHAR,max_length=1200),
    FieldSchema(name="awards",dtype=DataType.VARCHAR,max_length=300),
    FieldSchema(name="overallSummary",dtype=DataType.FLOAT_VECTOR,max_length=1200),
    FieldSchema(name="workExperience",dtype=DataType.FLOAT_VECTOR,max_length=1200)

]