# Accepts peer registration requests

import copy
import traceback
from typing import Dict, Any

from fastapi import HTTPException

from api.pex import PexMongo
from utils.utils import Utils, Peer


router = Utils.router


@router.post(
    "/register",
    tags=["Peer Exchange"],
    summary="Register a new peer",
    description="Accepts peer registration requests and adds them to the peer list.",
)
async def register_endpoint(peer: Peer.Public) -> Dict[str, Any]:
    """
    Registers a new peer within the peer-to-peer network.

    Endpoint that handles the registration process for new peers trying to join the network.
    It receives a peer's public information, converts it to the internal data format, and
    then attempts to add the new peer to the database. It will return a truncated peer list to
    the newly registered peer for further network discovery if successful.

    Upon registration, peers in the network may synchronize and update their local peer lists,
    ensuring the network's integrity and topology are maintained.

    Args:
        peer (Peer.Public): A Peer.Public instance containing the required data for registration.

    Returns:
        Dict[str, Any]: A dictionary containing the registration status and, on a successful
                        registration, the peer's own public information and the peer list.

    Raises:
        HTTPException: If the peer is already registered or if any exception occurs during the
                       process, an HTTPException with appropriate status code and error details
                       is raised.

    Example response:
        {
            "content": {
                "peer": {
                    "name": "peer1",
                    "ip": "192.168.1.2",
                    "port": "8080"
                },
                "peer_list": [
                    {"name": "peer2", "ip": "192.168.1.3", "port": "8081"},
                    {"name": "peer3", "ip": "192.168.1.4", "port": "8082"}
                ]
            },
            "status_code": 200
        }
    """
    # TODO: Need to implement a check that the ip address the peer is providing is the same one it's requesting from, peers should always provide the valid ip address they are requesting from. if not then the request should be rejected.
    try:
        # First step in any endpoint, convert public to private peer, might want to convert this into a middleware to automatically do this in the future somehow:
        peer_int = Peer.to_internal(peer)
        added = await PexMongo.add_peer(
            peer=copy.deepcopy(peer_int)
        )  # Need to deep copy here because mongo throws a fit, could be a better fix for this in pex.PexMongo
        if not added:
            raise HTTPException(status_code=400, detail="Peer already registered.")

        peer_list = await PexMongo.get_random_peers()
        return {
            "content": {
                "peer": peer,
                "peer_list": Peer.to_public(peer_list),
            },
            "status_code": 200,
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
