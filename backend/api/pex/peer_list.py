# Return peer_list when requested by other peers

import traceback
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from .pex_mongo import PexMongo
from utils.utils import Utils

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
            "content": {
                "peer_list": Utils.PublicPeerResponse.to_public(peer_list)
            },
            "status_code": 200,
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
