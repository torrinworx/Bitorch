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
            self.client = AsyncIOMotorClient(mongo_url)
            self.db = self.client[db_name]
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            self.client = None
            self.db = None

    def __del__(self):
        if self.client:
            self.client.close()

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

    async def create_collection(self, collection_name: str) -> bool:
        if collection_name in await self.db.list_collection_names():
            return False
        await self.db.create_collection(collection_name)
        return True

    async def drop_collection(self, collection_name: str) -> bool:
        if collection_name in await self.db.list_collection_names():
            await self.db.drop_collection(collection_name)
            return True
        return False

    async def list_collections(self) -> List[str]:
        try:
            collection_names = await self.db.list_collection_names()
            return collection_names
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []

    # TODO: Setup proper unit tests using like pytest or something
    async def test(self):
        test_collection = "test"
        name = "John Doe"

        try:
            # Ensure the test collection is fresh
            if test_collection in await self.list_collections():
                if not await self.drop_collection(test_collection):
                    print("Failed to drop existing test collection.")
                    return False

            if not await self.create_collection(test_collection):
                print("Failed to create test collection.")
                return False
        except Exception as e:
            print(f"Error ensuring fresh test collection: {e}")
            print(traceback.format_exc())
            return False

        try:
            # Insert a document
            test_document = {"name": name, "age": 30}
            if not await self.insert_document(
                collection_name=test_collection, document=test_document
            ):
                print("Failed to insert document.")
                return False
        except Exception as e:
            print(f"Error inserting document: {e}")
            print(traceback.format_exc())
            return False

        try:
            # Find documents
            query = {"name": name}
            found_documents = await self.find_documents(
                collection_name=test_collection, query=query
            )
            if not found_documents:
                print("No documents found.")
                return False
        except Exception as e:
            print(f"Error finding documents: {e}")
            print(traceback.format_exc())
            return False

        try:
            # Update a document
            update_query = {"name": name}
            update_data = {"$set": {"age": 31}}
            if not await self.update_document(
                collection_name=test_collection, query=update_query, update=update_data
            ):
                print("Failed to update document.")
                return False
        except Exception as e:
            print(f"Error updating document: {e}")
            print(traceback.format_exc())
            return False

        try:
            # Find documents again to verify update
            updated_documents = await self.find_documents(test_collection, query)
            if not updated_documents or updated_documents[0]["age"] != 31:
                print("Document update verification failed.")
                return False
        except Exception as e:
            print(f"Error verifying document update: {e}")
            print(traceback.format_exc())
            return False

        try:
            # Delete a document
            delete_query = {"name": name}
            if not await self.delete_document(test_collection, delete_query):
                print("Failed to delete document.")
                return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            print(traceback.format_exc())
            return False

        try:
            # Find documents to verify deletion
            post_delete_documents = await self.find_documents(test_collection, query)
            if post_delete_documents:
                print("Document deletion verification failed.")
                return False
        except Exception as e:
            print(f"Error verifying document deletion: {e}")
            print(traceback.format_exc())
            return False

        # Test completed successfully
        return True
