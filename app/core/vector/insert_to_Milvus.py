import asyncio
from sys import maxsize
from typing import List, Any, Callable

from pymilvus import Collection
class InsertException(BaseException):
    """数据写入失败"""
    pass
class QueueBatchWriter:
    def __init__(self, max_size: int = 10, timeout: float = 3.0, write_func: Callable = None):
        self.max_size = max_size
        self.timeout = timeout
        self.write_func = write_func
        self.queue = asyncio.Queue()
        self._running = False
    async def start(self):
        self._running=True
        asyncio.create_task(self._consume_loop())

    async def add(self,item:Any):
        await self.queue.put(item)

    async def _consume_loop(self):
        while self._running:
            batch = []
            try:
                first_item = await asyncio.wait_for(self.queue.get(), timeout=self.timeout)
                batch.append(first_item)
                while len(batch)<self.max_size and not self.queue.empty():
                    try:
                        item = self.queue.get_nowait()
                        batch.append(item)
                    except asyncio.QueueEmpty:
                        break
            except asyncio.TimeoutError:
                if not batch:
                    continue
            if batch and self.write_func:
                try:
                    await self.write_func(batch)
                except InsertException as e:
                    raise InsertException("数据写入失败") from e

    async def shutdown(self):
        self._running = False
        batch = []
        while not self.queue.empty():
            try:
                batch.append(self.queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        if batch and self.write_func:
            await self.write_func(batch)

async def insert_to_Milvus(data_list:list,collection_name="ai_interviewer_resumes"):
    if not data_list:
        return
    collection = Collection(collection_name)
    await asyncio.to_thread(collection.insert, data=data_list)


