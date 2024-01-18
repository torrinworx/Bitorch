# Return peer_list when requested by other peers

import traceback
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from .pex_mongo import PexMongo

router = APIRouter()


@router.get(
    "/peer_list",
    tags=["Peer Exchange"],
    summary="Get list of peers",
    description="Returns a list of all registered peers.",
)
async def get_peers_endpoint() -> Dict[str, Any]:
    try:
        peer_list = await PexMongo.get_all_peers()
        return {
            "content": {"peer_list": [peer.dict() for peer in peer_list]},
            "status_code": 200,
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))