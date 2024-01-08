# Accepts peer registration requests

from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from utils.mongo import PeerListManager

router = APIRouter()
load_dotenv()

peer_list_manager = PeerListManager()

class NodeInfo(BaseModel):
    ip: str
    port: int
    name: str

class Peer(BaseModel):
    node_info: NodeInfo

@router.post(
    "/register",
    tags=["Peer Exchange"],
    summary="Register a new peer",
    description="Accepts peer registration requests and adds them to the peer list."
)
async def register_peer_endpoint(peer: Peer) -> JSONResponse:
    try:
        node_info = peer.node_info.dict()
        added = await peer_list_manager.add_peer(node_info=node_info)  # Convert to dict
        if not added:
            raise HTTPException(status_code=400, detail="Peer already registered.")
        
        return JSONResponse(
            content={"message": "You have been registered!", "node_info": peer.node_info},
            status_code=200
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
