from bson import ObjectId
from datetime import datetime
from typing import List, Optional


from utils.utils import Utils
from utils.mongo import MongoDBManager

collection_name = "peers"


class PexMongo:
    async def __init__(self):
        # await PexMongo.create_collection(collection_name=collection_name) Check if collection exists and create it if not. 
        pass

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
            peer_exists = await MongoDBManager().find_documents(
                collection_name, peer_dict
            )
            if not peer_exists:
                await MongoDBManager().insert_document(collection_name, peer_dict)
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
        existing_peer = await MongoDBManager().find_documents(
            collection_name, {"ip": peer_dict["ip"]}
        )
        if existing_peer:
            await MongoDBManager().update_document(
                collection_name, {"ip": peer_dict["ip"]}, peer_dict
            )
            return "Peer updated"
        else:
            await MongoDBManager().insert_document(collection_name, peer_dict)
            return "New peer added"

    @staticmethod
    async def get_all_peers() -> List[Utils.Peer]:
        """
        Retrieve all peers from the database and remove the '_id' field.
        """
        peers = await MongoDBManager().find_documents(collection_name, {})
        result = []
        for peer_dict in peers:
            peer_dict.pop("_id", None)
            result.append(Utils.Peer(**peer_dict))
        return result

    @staticmethod
    async def remove_peer(peer: Utils.Peer) -> bool:
        """
        Remove a peer from the database.
        """
        peer_dict = peer.dict()
        return await MongoDBManager().delete_document(collection_name, peer_dict)

    @staticmethod
    async def update_peer(
        old_peer: Utils.Peer, new_peer: Utils.Peer
    ) -> Optional[Utils.Peer]:
        """
        Update a peer's info.
        """
        result = await MongoDBManager().update_document(
            collection_name=collection_name,
            query=old_peer.dict(),
            update=new_peer.dict(),
        )
        return new_peer if result else None

    @staticmethod
    async def get_peer(ip: str) -> Optional[Utils.Peer]:
        """
        Get an individual peer by their IP address.
        """
        peer_dict = await MongoDBManager().find_documents(collection_name, {"ip": ip})
        if peer_dict:
            return Utils.Peer(**peer_dict[0])
        return None

    @staticmethod
    async def update_peer_request_history(
        client_ip: str, request_info: Utils.RequestInfo
    ) -> bool:
        """
        Append a new request record to the peer's request history and update the 'last seen' timestamp.
        If the peer doesn't exist, create a new peer and add the request history.
        """
        current_time = datetime.utcnow().isoformat()
        update_result = False

        peer_dict = {"ip": client_ip}
        peer_exists = await MongoDBManager().find_documents(collection_name, peer_dict)

        if not peer_exists:
            # If the peer doesn't exist, create a new peer and add the request history
            new_peer = Utils.Peer(
                ip=client_ip, request_history=[request_info], _last_seen=current_time
            )
            await MongoDBManager().insert_document(collection_name, new_peer.dict())
            update_result = True
        else:
            # If the peer exists, update the request history and 'last seen' timestamp
            update_result = await MongoDBManager().update_document(
                collection_name,
                {"ip": client_ip},
                {
                    "$push": {"_request_history": request_info.dict()},
                    "$set": {"_last_seen": current_time},
                },
            )

        return bool(update_result)
