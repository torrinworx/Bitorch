import os
import traceback
from typing import List, Dict

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

# TODO: implement race conditions
# TODO: Investigate and take advantage of connection pooling in motor.


class MongoDBManager:
    def __init__(self):
        try:
            mongo_url = os.getenv("MONGO_URL", "mongodb://mongodb:27017/")
            db_name = os.getenv("DB_NAME")
            mongo_url = "mongodb://mongodb:27017/"
            # mongo_url = "mongodb://localhost:27017"
            print(mongo_url)
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[db_name]

            print("INFO: Connected to MongoDB.")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None
            self.db = None

    def __del__(self):
        if self.client:
            self.client.close()
            print("INFO: MongoDB connection closed.")

    async def create_collection(self, collection_name: str) -> bool:
        if collection_name in await self.db.list_collection_names():
            return False
        await self.db.create_collection(collection_name)
        return True

    async def insert_document(self, collection_name: str, document: Dict) -> bool:
        collection = self.db[collection_name]
        await collection.insert_one(document)
        return True

    async def find_documents(self, collection_name: str, query: Dict) -> List[Dict]:
        collection = self.db[collection_name]
        cursor = collection.find(query)
        documents = [doc async for doc in cursor]
        return documents

    async def update_document(
        self, collection_name: str, query: Dict, update: Dict
    ) -> bool:
        collection = self.db[collection_name]
        # Check if the update dict contains any key that starts with '$'
        if not any(key.startswith("$") for key in update):
            update = {"$set": update}  # Use '$set' as default if no $ operator is found
        result = await collection.update_one(query, update)
        return result.modified_count > 0

    async def delete_document(self, collection_name: str, query: Dict) -> bool:
        collection = self.db[collection_name]
        result = await collection.delete_one(query)
        return result.deleted_count > 0

    async def drop_collection(self, collection_name: str) -> bool:
        if collection_name in await self.db.list_collection_names():
            await self.db.drop_collection(collection_name)
            return True
        return False

    async def test(self):
        try:
            # Create a test collection
            test_collection = "test"
            # await self.drop_collection(collection_name=test_collection)

            if not await self.create_collection(test_collection):
                return False

            # Insert a document
            test_document = {"name": "John Doe", "age": 30}
            if not await self.insert_document(
                collection_name=test_collection, document=test_document
            ):
                return False

            # Find documents
            query = {"name": "John Doe"}
            found_documents = await self.find_documents(
                collection_name=test_collection, query=query
            )
            if not found_documents:
                return False

            # Update a document
            update_query = {"name": "John Doe"}
            update_data = {"$set": {"age": 31}}
            if not await self.update_document(
                collection_name=test_collection, query=update_query, update=update_data
            ):
                return False

            # Find documents again to verify update
            updated_documents = await self.find_documents(test_collection, query)
            if not updated_documents or updated_documents[0]["age"] != 31:
                return False

            # Delete a document
            delete_query = {"name": "John Doe"}
            if not await self.delete_document(test_collection, delete_query):
                return False

            # Find documents to verify deletion
            post_delete_documents = await self.find_documents(test_collection, query)
            if post_delete_documents:
                return False

            # Test completed successfully
            return True

        except Exception as e:
            print(f"An error occurred during the test: {e}")
            print(traceback.format_exc())
            return False
