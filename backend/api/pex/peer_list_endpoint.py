# Return peer_list when requested by other peers
# TODO: Review and delete this? Might not be necissary now that /register sort of acts like an all in one endpoint for pex.

import traceback
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from api.pex import PexMongo
from utils.utils import Peer

router = APIRouter()


@router.get(
    "/peer_list",
    tags=["Peer Exchange"],
    summary="Get list of peers",
    description="Returns a list of all registered peers.",
)
async def peer_list_endpoint() -> Dict[str, Any]:
    try:
        peer_list = await PexMongo.get_all_peers()
        return {
            "content": {
                "peer_list": Peer.to_public(peer_list)
            },
            "status_code": 200,
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
