from typing import List, Optional
from utils.mongo import mongo_manager

mongo_manager = mongo_manager
collection_name = "peers"


class PexMongo:
    @staticmethod
    async def add_peers(peer_list: List[dict]) -> bool:
        """
        Add list of peers to the database.
        """
        success = True
        for peer in peer_list:
            peer_exists = await mongo_manager.find_documents(collection_name, peer)
            if not peer_exists:
                await mongo_manager.insert_document(collection_name, peer)
            else:
                success = False
        return success

    @staticmethod
    async def add_peer(peer_info: dict) -> bool:
        """
        Add a new peer to the database.
        """
        existing_peer = await mongo_manager.find_documents(collection_name, peer_info)
        if existing_peer:
            return False
        await mongo_manager.insert_document(collection_name, peer_info)
        return True

    @staticmethod
    async def get_all_peers() -> List[dict]:
        """
        Retrieve all peers from the database.
        """
        return await mongo_manager.find_documents(collection_name, {})

    @staticmethod
    async def remove_peer(peer_info: dict) -> bool:
        """
        Remove a peer from the database.
        """
        return await mongo_manager.delete_document(collection_name, peer_info)

    @staticmethod
    async def update_peer(
        self, old_peer_info: dict, new_peer_info: dict
    ) -> Optional[dict]:
        """
        Update a peer's peer_info.
        """
        result = await mongo_manager.update_document(
            collection_name, old_peer_info, new_peer_info
        )
        return new_peer_info if result else None
