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

Right now there are two potential packages we can use for the initial test of running the entire model on a single peer since chunking and distributing the model like petals is a bit more complex:
- https://llm.datasette.io/en/stable/python-api.html - pypi llm package
- https://docs.gpt4all.io/gpt4all_python.html - gpt4all python package

llm uses gpt4all under the hood so we should probably just use gpt4all directly so that we don't have to bloat the library. Ideally though, we would at somepoint in the future develop our own
in house alternative of gpt4all package/model running capabilities so that we don't have to get locked in to this library.

I've tried ollama but don't like it because it requires you to deploy a server locally which I don't want in this case because this is supposed to be the server running the llms.

gpt4all seems to be a self contained python library that just runs binaries which should be more python based I guess, also ollama is written in go which is yuck for what I want here.

NOTE: Need to purge all none essential env libraries so that the docker images are lighter.
"""

import os
from pydantic import BaseModel

from gpt4all import GPT4All
from fastapi import APIRouter


router = APIRouter()


class InferenceInput(BaseModel):
    text_input: str


@router.post(
    "/inference-request",
    tags=["Distributed Inference"],
    summary="Generates text based on the input prompt using Mistral model.",
    description="This endpoint receives a text input and returns a generated text response from the Mistral-7B-v0.1 model.",
)
async def inference_request_endpoint(inference_input: InferenceInput):
    model_path = os.path.join("backend", "models")
    os.makedirs(model_path, exist_ok=True)

    # Use the absolute path of the directory where your model should be located
    abs_model_path = os.path.abspath(model_path)

    model = GPT4All(
        model_name="orca-mini-3b-gguf2-q4_0.gguf",  # https://raw.githubusercontent.com/nomic-ai/gpt4all/main/gpt4all-chat/metadata/models2.json
        allow_download=True,
        model_path=abs_model_path,
    )
    response = model.generate(inference_input.text_input, max_tokens=2000)
    return response
