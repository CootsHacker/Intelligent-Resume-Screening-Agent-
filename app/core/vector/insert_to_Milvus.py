import asyncio
from sys import maxsize
from typing import List, Any, Callable

from pymilvus import Collection, connections

from app.Exception.Eception import InsertException


import asyncio
from typing import Any, Callable


class QueueBatchWriter:
    def __init__(
        self,
        max_size: int = 10,
        timeout: float = 3.0,
        write_func: Callable = None,
        client=None
    ):
        self.max_size = max_size
        self.timeout = timeout
        self.write_func = write_func
        self.queue = asyncio.Queue()
        self._running = False
        self.client = client

    async def start(self):
        self._running = True
        asyncio.create_task(self._consume_loop())

    async def add(self, item: Any, collection_name: str):
        payload = {
            "collection_name": collection_name,
            "data": item
        }
        await self.queue.put(payload)

    async def _consume_loop(self):
        while self._running:
            batch = []

            try:
                first_item = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=self.timeout
                )

                batch.append(first_item)

                while len(batch) < self.max_size and not self.queue.empty():
                    try:
                        batch.append(self.queue.get_nowait())
                    except asyncio.QueueEmpty:
                        break

            except asyncio.TimeoutError:
                if not batch:
                    continue

            if not batch or self.write_func is None:
                continue

            grouped_batches = {}

            for item in batch:
                col_name = item["collection_name"]

                if col_name not in grouped_batches:
                    grouped_batches[col_name] = []

                grouped_batches[col_name].extend(item["data"])

            for col_name, data_list in grouped_batches.items():
                try:
                    await self.write_func(
                        data_list,
                        self.client,
                        collection_name=col_name
                    )
                except Exception as e:
                    print(f"❌ 写入集合 {col_name} 失败: {e}")

    async def shutdown(self):
        self._running = False

        batch = []

        while not self.queue.empty():
            try:
                batch.append(self.queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        if not batch or self.write_func is None:
            return

        grouped_batches = {}

        for item in batch:
            col_name = item["collection_name"]

            if col_name not in grouped_batches:
                grouped_batches[col_name] = []

            grouped_batches[col_name].extend(item["data"])

        for col_name, data_list in grouped_batches.items():
            try:
                await self.write_func(
                    data_list,
                    self.client,
                    collection_name=col_name
                )
            except Exception as e:
                print(f"❌ shutdown 写入 {col_name} 失败: {e}")

async def insert_to_Milvus(data_list:list,client,collection_name):
    if not data_list:
        return
    try:
        #print(data_list[0])
        await client.insert(collection_name=collection_name, data=data_list)
    except Exception as e:
        raise InsertException(f"写入数据到 Milvus 失败: {e}")



