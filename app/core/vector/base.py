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
    FieldSchema(name="skills",dtype=DataType.ARRAY,max_length=100,max_capacity=10)






]