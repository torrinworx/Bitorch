from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ...utils import Utils, Peer


router = APIRouter()


@router.get(
    "/health_check",
    tags=["Peer Exchange"],
    summary="Health check",
    description="Simple endpoint to check if node is still alive.",
)
async def health_check_endpoint() -> JSONResponse:
    """
    A simple health check endpoint to verify if the node is operational.

    This endpoint performs a simple operational check (e.g., database connectivity check could be included)
    to ensure the node is up and running. It returns a message indicating the status of the node.

    Returns:
        JSONResponse: A JSON response indicating the status of the node. It returns a status code of 200
                      along with {"status": "OK"} if everything is operational, or a status code of 500
                      along with {"detail": "Node is not healthy"} if an exception is caught indicating the node might be experiencing issues.
    """
    try:
        my_peer = await Utils.get_my_peer()
        return JSONResponse(
            content={"status": "OK", "peer": Peer.to_public(my_peer)}, status_code=200
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return JSONResponse(content={"detail": "Node is not healthy"}, status_code=500)
