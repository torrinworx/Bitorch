from bson import ObjectId
from typing import List, Optional
from utils.mongo import mongo_manager

collection_name = "peers"


class PexMongo:
    @staticmethod
    def serialize(data):
        """
        Serialize MongoDB data by converting ObjectId to string.
        """
        if isinstance(data, list):
            return [PexMongo.serialize(item) for item in data]
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, ObjectId):
                    data[key] = str(value)
        return data

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
    async def add_peer(peer: dict) -> bool:
        """
        Add a new peer to the database.
        """
        existing_peer = await mongo_manager.find_documents(collection_name, peer)
        if existing_peer:
            return False
        await mongo_manager.insert_document(collection_name, peer)
        return True

    @staticmethod
    async def get_all_peers() -> List[dict]:
        """
        Retrieve all peers from the database.
        """
        peers = await mongo_manager.find_documents(collection_name, {})
        return PexMongo.serialize(peers)

    @staticmethod
    async def remove_peer(peer_info: dict) -> bool:
        """
        Remove a peer from the database.
        """
        return await mongo_manager.delete_document(collection_name, peer_info)

    @staticmethod
    async def update_peer(old_peer_info: dict, new_peer_info: dict) -> Optional[dict]:
        """
        Update a peer's peer_info.
        """
        result = await mongo_manager.update_document(
            collection_name, old_peer_info, new_peer_info
        )
        return PexMongo.serialize(new_peer_info) if result else None
