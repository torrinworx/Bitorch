# Accepts peer registration requests
import copy
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
        peer = peer.dict()
        added = await PexMongo.add_peer(peer=copy.deepcopy(
            peer
        ))
        if not added:
            raise HTTPException(status_code=400, detail="Peer already registered.")

        return JSONResponse(
            content={"peer": peer},
            status_code=200,
        )
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
