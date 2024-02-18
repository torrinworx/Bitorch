"""
Generally we should only begin doing the work once we have verified that there is an escrow peer holding the blockchain/tokens for us that
will verify the output as valid or something along those lines or some maybe peer ranking system idk. I'm not sure what the best approach is
for this, wheather or not the requesting peer should send the money first, then the result returned and if the inference peer doesn't send back
the result then the network losses a lot of trust in them.

However for the first test we can just simply request inference from a peer running any model on the network right now.

Generally the inference function/endpoint should be just the wrapper for whatever model is being requested, I'm imagining that each type of model,
e.g. the type of data input/output, would have their own pydantic model class that we can define that would be applicable to all types:
- Image model generation, input = text and ...params specific to the model, output = some image file and metadata needed
- LLM, input = text and ...params specific to the model, output = text string and metadata needed
- etc.

basically the pydantic classes defining the type of model should be super general and abstract away the  model specific stuff and just plugin directly
to whatever huggingface transformer pipeline that is needed to run the model.

Something like this:
```
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
import time
import json

app = FastAPI()

def perform_inference(task_id: str):
    # Placeholder for actual inference task,
    # imagine that this function does the real work.
    for progress in range(1, 101):
        time.sleep(0.1)  # Simulate work being done
        yield f"data: {json.dumps({'task_id': task_id, 'status': 'IN_PROGRESS', 'progress': progress})}\n\n"
    # Simulate the final result
    final_result = "Inference Result Here"
    yield f"data: {json.dumps({'task_id': task_id, 'status': 'COMPLETED', 'result': final_result})}\n\n"

@app.get("/inference/{task_id}")
async def inference(task_id: str, background_tasks: BackgroundTasks):
    def event_stream():
        for event in perform_inference(task_id):
            yield event

    background_tasks.add_task(event_stream)
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

Generally I want this endpoint to handle everything. Like status reporting back to the client/requesting peer, returning of results, security of result transmission, etc.
"""

# Return peer_list when requested by other peers
# TODO: Review and delete this? Might not be necissary now that /register sort of acts like an all in one endpoint for pex.

import traceback

from fastapi import APIRouter, HTTPException

# from api.pex import PexMongo
from utils.utils import Peer

router = APIRouter()


@router.get(
    "/inference-request",
    tags=["Distributed Inference"],
    summary="TODO",
    description="TODO",
)
async def inference_request_endpoint(peer: Peer.Public):
    try:
        # TODO: Check if peer is registered, if not, deny request.
        return
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
