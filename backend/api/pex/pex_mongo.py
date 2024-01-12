from typing import List, Optional
from utils.mongo import mongo_manager


class PexMongo:
    def __init__(self):
        self.mongo_manager = mongo_manager
        self.collection_name = "peers"

    async def add_peers(self, peer_list: List[dict]) -> bool:
        """
        Add list of peers to the database.
        """
        success = True
        for peer in peer_list:
            peer_exists = await self.mongo_manager.find_documents(
                self.collection_name, peer
            )
            if not peer_exists:
                await self.mongo_manager.insert_document(self.collection_name, peer)
            else:
                success = False
        return success

    async def add_peer(self, peer_info: dict) -> bool:
        """
        Add a new peer to the database.
        """
        existing_peer = await self.mongo_manager.find_documents(
            self.collection_name, peer_info
        )
        if existing_peer:
            return False
        await self.mongo_manager.insert_document(self.collection_name, peer_info)
        return True

    async def get_all_peers(self) -> List[dict]:
        """
        Retrieve all peers from the database.
        """
        return await self.mongo_manager.find_documents(self.collection_name, {})

    async def remove_peer(self, peer_info: dict) -> bool:
        """
        Remove a peer from the database.
        """
        return await self.mongo_manager.delete_document(self.collection_name, peer_info)

    async def update_peer(
        self, old_peer_info: dict, new_peer_info: dict
    ) -> Optional[dict]:
        """
        Update a peer's peer_info.
        """
        result = await self.mongo_manager.update_document(
            self.collection_name, old_peer_info, new_peer_info
        )
        return new_peer_info if result else None

