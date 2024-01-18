from bson import ObjectId
from typing import List, Optional
from utils.mongo import mongo_manager

from utils.utils import Utils

peer_class = Utils.Peer  # Use in new methods

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
    async def add_peers(peer_list: List[Utils.Peer]) -> bool:
        """
        Serialize MongoDB data by converting ObjectId to string.
        """
        success = True
        for peer_model in peer_list:
            peer_dict = peer_model.dict()
            peer_exists = await mongo_manager.find_documents(collection_name, peer_dict)
            if not peer_exists:
                await mongo_manager.insert_document(collection_name, peer_dict)
            else:
                success = False
        return success

    @staticmethod
    async def add_peer(peer: Utils.Peer) -> str:
        """
        Add a new peer to the database or update it if it already exists.
        Check if a peer with the same IP address exists, and update its details if other fields have changed.
        """
        peer_dict = peer.dict()
        existing_peer = await mongo_manager.find_documents(
            collection_name, {"ip": peer_dict["ip"]}
        )
        if existing_peer:
            await mongo_manager.update_document(
                collection_name, {"ip": peer_dict["ip"]}, peer_dict
            )
            return "Peer updated"
        else:
            await mongo_manager.insert_document(collection_name, peer_dict)
            return "New peer added"

    @staticmethod
    async def get_all_peers() -> List[Utils.Peer]:
        """
        Retrieve all peers from the database and remove the '_id' field.
        """
        peers = await mongo_manager.find_documents(collection_name, {})
        result = []
        for peer_dict in peers:
            peer_dict.pop("_id", None)
            result.append(Utils.Peer(**peer_dict))
        return result

    @staticmethod
    async def remove_peer(peer_model: Utils.Peer) -> bool:
        """
        Remove a peer from the database.
        """
        peer_dict = peer_model.dict()
        return await mongo_manager.delete_document(collection_name, peer_dict)

    @staticmethod
    async def update_peer(
        old_peer_model: Utils.Peer, new_peer_model: Utils.Peer
    ) -> Optional[Utils.Peer]:
        """
        Update a peer's info.
        """
        result = await mongo_manager.update_document(
            collection_name=collection_name,
            query=old_peer_model.dict(),
            update=new_peer_model.dict()
        )
        return new_peer_model if result else None
