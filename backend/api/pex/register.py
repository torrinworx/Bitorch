# Accepts peer registration requests

import copy
import traceback
from typing import Dict, Any

from fastapi import HTTPException

from .pex_mongo import PexMongo
from utils.utils import Utils, Peer


router = Utils.router


@router.post(
    "/register",
    tags=["Peer Exchange"],
    summary="Register a new peer",
    description="Accepts peer registration requests and adds them to the peer list.",
)
async def register_peer_endpoint(peer: Peer.Public) -> Dict[str, Any]:
    try:
        # First step in any endpoint, convert public to private peer, might want to convert this into a middleware to automatically do this in the future somehow:
        peer = Peer.to_internal(peer)
        added = await PexMongo.add_peer(peer=copy.deepcopy(peer))
        if not added:
            raise HTTPException(status_code=400, detail="Peer already registered.")

        peer_list = await PexMongo.get_all_peers()
        print("PEER LIST:", peer_list[0].to_public())
        return {
            "content": {
                "peer": Peer.to_public(peer),
                "peer_list": Peer.to_public(peer_list),
            },
            "status_code": 200,
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
