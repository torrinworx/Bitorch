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
import queue
import threading
from pydantic import BaseModel
from typing import List, Optional, Dict, Iterator

from gpt4all import GPT4All
from fastapi import APIRouter
from fastapi.responses import StreamingResponse


router = APIRouter()


class InferenceInput(BaseModel):
    messages: Optional[List[Dict[str, str]]]
    stream: bool = False # Weather or not to stream back the request as it's generated

    class Config:
        schema_extra = {
            "examples": [
                {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an AI assistant that follows instruction extremely well. Help as much as you can.",
                        },
                        {
                            "role": "user",
                            "content": "what's up dude?"
                        },
                        {
                            "role": "assistant",
                            "content": "I'm doing great, thank you for asking! How about you?",
                        },
                        {
                            "role": "user",
                            "content": "What is the speed of light?"
                        },
                    ],
                    "stream": False,
                },
            ]
        }


def format_prompt_for_llm(prompt_list):
    """
    Takes a list of conversation entries and formats them as a single string prompt.

    :param prompt_list: A list of dictionaries with 'role' and 'content' keys.
    :return: A formatted string prompt.
    """
    formatted_prompt = ""

    # Mapping from your roles to the required prompt labels
    role_to_label = {
        "system": "### System:",
        "user": "### Human:",
        "assistant": "### Assistant:",
    }

    for entry in prompt_list:
        role_label = role_to_label.get(entry["role"], "")
        if role_label:
            formatted_prompt += f"{role_label}\n{entry['content']}\n\n"

    # We always expect the assistant's reply at the end, hence the final "### Assistant:"
    formatted_prompt += "### Assistant:\n"

    return formatted_prompt


@router.post(
    "/inference-request",
    tags=["Distributed Inference"],
    summary="Generates text based on the input prompt or chat_session.",
    description="This endpoint receives a text input and returns a generated text response.",
)
async def inference_request_endpoint(inference_input: InferenceInput):
    """
    TODO: Docstring
    TODO: Compatibility with openai api
    TODO: All peer to select which models it wants to host and allow endpoint user to select model to run based on hosted models
    TODO: Securly wrap the GPT4ALL.generate and .chat_session variables with thought about what the peer should control vs what the user should control
    TODO: security sanatization of all input data from user of endpoints.
    
    NOTE: Core aspect of this design is that the client, whatever it is, is expected to keep track of the chat_session, not the server. the server will only responde
    with the response of the model, whether that be strings, images, audio, whatever.
    """
    model_path = os.path.join("models")
    os.makedirs(model_path, exist_ok=True)

    # Use the absolute path of the directory where your model should be located
    abs_model_path = os.path.abspath(model_path)

    model = GPT4All(
        model_name="mistral-7b-openorca.gguf2.Q4_0.gguf",  # https://raw.githubusercontent.com/nomic-ai/gpt4all/main/gpt4all-chat/metadata/models2.json
        allow_download=True,
        model_path=abs_model_path,
        verbose=True
    )

    prompt = format_prompt_for_llm(prompt_list=inference_input.messages)
    
    if inference_input.stream:
        # Queue to hold generated tokens
        token_queue = queue.Queue()

        def worker():
            try:
                for token in model.generate(
                    prompt=prompt, max_tokens=1000, streaming=True
                ):
                    # print(token, end='', flush=True)  # Append to the same line and flush the output
                    token_queue.put(token)  # Put the token in the queue
            finally:
                # print()  # Ensure the next console output appears on a new line
                token_queue.put(None)  # Put sentinel value to indicate end

        # Start the worker in a separate thread
        threading.Thread(target=worker, daemon=True).start()

        # Generator function for StreamingResponse
        def token_streamer() -> Iterator[str]:
            # Fetch tokens from the queue
            while True:
                token = (
                    token_queue.get()
                )  # will block until a new item is available
                if token is None:
                    break  # If we get sentinel value, exit
                yield token + "\n"  # Yield token to the client

        # Return the streaming response
        return StreamingResponse(token_streamer(), media_type="text/plain")
    else:
        return model.generate(prompt=prompt, max_tokens=1000, streaming=False)
