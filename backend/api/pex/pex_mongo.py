from typing import List, Optional
from utils.mongo import mongo_manager

class PexMongo:
    def __init__(self):
        self.mongo_manager = mongo_manager
        self.collection_name = "peers"

    async def add_peer(self, node_info: dict) -> bool:
        """
        Add a new peer to the database.
        """
        existing_peer = await self.mongo_manager.find_documents(
            self.collection_name, {"node_info": node_info}
        )
        if existing_peer:
            return False
        await self.mongo_manager.insert_document(
            self.collection_name, {"node_info": node_info}
        )
        return True

    async def get_all_peers(self) -> List[dict]:
        """
        Retrieve all peers from the database.
        """
        peers = await self.mongo_manager.find_documents(self.collection_name, {})
        return [peer["node_info"] for peer in peers]

    async def remove_peer(self, node_info: dict) -> bool:
        """
        Remove a peer from the database.
        """
        return await self.mongo_manager.delete_document(
            self.collection_name, {"node_info": node_info}
        )

    async def update_peer(
        self, old_node_info: dict, new_node_info: dict
    ) -> Optional[dict]:
        """
        Update a peer's node_info.
        """
        result = await self.mongo_manager.update_document(
            self.collection_name,
            {"node_info": old_node_info},
            {"node_info": new_node_info},
        )
        return new_node_info if result else None
