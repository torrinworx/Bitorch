from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from typing import List, Optional
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

class PeerListManager:
    def __init__(self):
        db_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        # NOTE: this is temporary until we get a proper self naming system in place to self name the nodes.
        random_db_name = secrets.token_hex(16)  # Generate a random 32-character hex string
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[random_db_name]  # Use the random hash as the database name
        self.peers_collection = self.db["peers"]

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

    async def update_peer(self, old_node_info: dict, new_node_info: dict) -> Optional[dict]:
        """
        Update a peer's node_info.
        """
        result = await self.peers_collection.find_one_and_update(
            {"node_info": old_node_info},
            {"$set": {"node_info": new_node_info}},
            return_document=ReturnDocument.AFTER
        )
        return result["node_info"] if result else None
    