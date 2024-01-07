# Accepts peer registration requests

from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from utils.mongo import PeerListManager

router = APIRouter()
load_dotenv()

class Peer(BaseModel):
    address: str

@router.post(
    "/register",
    tags=["Peer Exchange"],
    summary="Register a new peer",
    description="Accepts peer registration requests and adds them to the peer list."
)
async def register_peer_endpoint(peer: Peer) -> JSONResponse:
    try:
        added = await PeerListManager.add_peer(peer.address)
        if not added:
            raise HTTPException(status_code=400, detail="Peer already registered.")
        
        return JSONResponse(
            content={"message": "You have been registered!", "peer_address": peer.address},
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
