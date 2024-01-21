# Accepts peer registration requests

import copy
import traceback
from typing import Dict, Any

from fastapi import HTTPException

from .pex_mongo import PexMongo
from utils.utils import Utils


router = Utils.router


@router.post(
    "/register",
    tags=["Peer Exchange"],
    summary="Register a new peer",
    description="Accepts peer registration requests and adds them to the peer list.",
)
async def register_peer_endpoint(peer: Utils.Peer) -> Dict[str, Any]:
    try:
        added = await PexMongo.add_peer(peer=copy.deepcopy(peer))
        if not added:
            raise HTTPException(status_code=400, detail="Peer already registered.")

        return {
            "content": {"peer": Utils.PublicPeerResponse.to_public(peer)},
            "status_code": 200,
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
