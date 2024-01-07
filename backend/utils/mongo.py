from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class PeerListManager:
    def __init__(self, db_name: str):
        db_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self.client = AsyncIOMotorClient(db_url)
        self.db = self.client[db_name]
        self.peers_collection = self.db["peers"]

    async def add_peer(self, peer_address: str) -> bool:
        """
        Add a new peer to the database.
        """
        if await self.peers_collection.find_one({"address": peer_address}):
            return False  # Peer already exists
        await self.peers_collection.insert_one({"address": peer_address})
        return True

    async def get_all_peers(self) -> List[str]:
        """
        Retrieve all peers from the database.
        """
        peers_cursor = self.peers_collection.find({}, {"_id": 0, "address": 1})
        peers = [peer["address"] async for peer in peers_cursor]
        return peers

    async def remove_peer(self, peer_address: str) -> bool:
        """
        Remove a peer from the database.
        """
        result = await self.peers_collection.delete_one({"address": peer_address})
        return result.deleted_count > 0

    async def update_peer(self, old_address: str, new_address: str) -> Optional[str]:
        """
        Update a peer's address.
        """
        result = await self.peers_collection.find_one_and_update(
            {"address": old_address},
            {"$set": {"address": new_address}},
            return_document=ReturnDocument.AFTER
        )
        return result["address"] if result else None

# Example usage
mongo_manager = PeerListManager(db_name="peer_list")
