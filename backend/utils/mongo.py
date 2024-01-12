from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from typing import List, Optional
import os
import secrets
from dotenv import load_dotenv

load_dotenv()


class PeerListManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PeerListManager, cls).__new__(cls)
            db_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
            random_db_name = secrets.token_hex(16)
            try:
                cls._instance.client = AsyncIOMotorClient(db_url)
                cls._instance.db = cls._instance.client[random_db_name]
                cls._instance.peers_collection = cls._instance.db["peers"]
                print("INFO: Connected to MongoDB successfully.")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                cls._instance.client = None
                cls._instance.db = None
                cls._instance.peers_collection = None
        return cls._instance

    async def close_mongo_connection(self):
        if self.client:
            self.client.close()
            self.client = None

    async def add_peer(self, node_info: dict) -> bool:
        """
        Add a new peer to the database.
        """
        if await self.peers_collection.find_one({"node_info": node_info}):
            return False
        await self.peers_collection.insert_one({"node_info": node_info})
        return True

    async def get_all_peers(self) -> List[dict]:
        """
        Retrieve all peers from the database.
        """
        peers_cursor = self.peers_collection.find({}, {"_id": 0})
        peers = [peer["node_info"] async for peer in peers_cursor]
        return peers

    async def remove_peer(self, node_info: dict) -> bool:
        """
        Remove a peer from the database.
        """
        result = await self.peers_collection.delete_one({"node_info": node_info})
        return result.deleted_count > 0

    async def update_peer(
        self, old_node_info: dict, new_node_info: dict
    ) -> Optional[dict]:
        """
        Update a peer's node_info.
        """
        result = await self.peers_collection.find_one_and_update(
            {"node_info": old_node_info},
            {"$set": {"node_info": new_node_info}},
            return_document=ReturnDocument.AFTER,
        )
        return result["node_info"] if result else None


peer_list_manager = PeerListManager()
