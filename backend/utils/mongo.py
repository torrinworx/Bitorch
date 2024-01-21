import os
from typing import List, Dict

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()


class MongoDBManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
            db_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
            random_db_name = os.getenv("DB_NAME", "bitorch")  # TODO: make unique name for docker compose dev environment so each peer has it's own db without effecting others.
            try:
                cls._instance.client = AsyncIOMotorClient(db_url)
                cls._instance.db = cls._instance.client[random_db_name]
                print("INFO: Connected to MongoDB successfully.")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                cls._instance.client = None
                cls._instance.db = None
        return cls._instance

    async def close_connection(self):
        if self.client:
            self.client.close()
            self.client = None

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


async def test_mongo_operations():
    mongo_manager = MongoDBManager()

    try:
        # Create a test collection
        test_collection = "test"
        await mongo_manager.drop_collection(test_collection)

        if not await mongo_manager.create_collection(test_collection):
            return False

        # Insert a document
        test_document = {"name": "John Doe", "age": 30}
        if not await mongo_manager.insert_document(test_collection, test_document):
            return False

        # Find documents
        query = {"name": "John Doe"}
        found_documents = await mongo_manager.find_documents(test_collection, query)
        if not found_documents:
            return False

        # Update a document
        update_query = {"name": "John Doe"}
        update_data = {"$set": {"age": 31}}
        if not await mongo_manager.update_document(
            test_collection, update_query, update_data
        ):
            return False

        # Find documents again to verify update
        updated_documents = await mongo_manager.find_documents(test_collection, query)
        if not updated_documents or updated_documents[0]["age"] != 31:
            return False

        # Delete a document
        delete_query = {"name": "John Doe"}
        if not await mongo_manager.delete_document(test_collection, delete_query):
            return False

        # Find documents to verify deletion
        post_delete_documents = await mongo_manager.find_documents(
            test_collection, query
        )
        if post_delete_documents:
            return False

        # Test completed successfully
        return True

    except Exception as e:
        print(f"An error occurred during the test: {e}")
        return False

mongo_manager = MongoDBManager()
