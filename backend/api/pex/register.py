# Accepts peer registration requests

import traceback

from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from .pex_mongo import PexMongo


class Peer(BaseModel):
    ip: str
    port: int
    name: str


router = APIRouter()
load_dotenv()


@router.post(
    "/register",
    tags=["Peer Exchange"],
    summary="Register a new peer",
    description="Accepts peer registration requests and adds them to the peer list.",
)
async def register_peer_endpoint(peer: Peer) -> JSONResponse:
    try:
        peer_dict = peer.dict()
        added = await PexMongo.add_peer(node_info=peer_dict)
        if not added:
            raise HTTPException(status_code=400, detail="Peer already registered.")

        return JSONResponse(
            content={"message": "You have been registered!", "node_info": peer_dict},
            status_code=200,
        )
    except Exception:
        print(traceback.format_exc())  # Print the full traceback error
        raise HTTPException(status_code=500, detail="Internal Server Error")
