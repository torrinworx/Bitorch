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
from typing import List, Optional, Dict
from pydantic import BaseModel, root_validator

from gpt4all import GPT4All
from fastapi import APIRouter


router = APIRouter()


class InferenceInput(BaseModel):
    prompt: Optional[str] = None
    chat_session: Optional[List[Dict[str, str]]] = None
    system_template: str = ""
    prompt_template: str = ""

    @root_validator(pre=True)
    def check_prompt_or_chat_session(cls, values):
        prompt, chat_session = values.get("prompt"), values.get("chat_session")
        if (prompt is None and chat_session is None) or (prompt and chat_session):
            raise ValueError(
                "You must provide either a prompt or a chat session, not both."
            )
        return values

    class Config:
        schema_extra = {
            "examples": [
                {
                    # Assuming no chat session is provided if prompt is used
                    "prompt": "What is the capital of France?",
                    # Assuming no prompt is provided if chat_session is used
                    "chat_session": [
                        {
                            "role": "system",
                            "content": "You are an AI assistant that follows instruction extremely well. Help as much as you can.",
                        },
                        {"role": "user", "content": "what's up dude?"},
                        {
                            "role": "assistant",
                            "content": "I'm doing great, thank you for asking! How about you?",
                        },
                        {"role": "user", "content": "What is the speed of light?"},
                    ],
                    "system_template": "You are a knowledgeable assistant.",
                    "prompt_template": "### Human: \n{0}\n\n### Assistant:\n",
                },
            ]
        }


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
    
    """
    model_path = os.path.join("backend", "models")
    os.makedirs(model_path, exist_ok=True)

    # Use the absolute path of the directory where your model should be located
    abs_model_path = os.path.abspath(model_path)

    model = GPT4All(
        model_name="orca-mini-3b-gguf2-q4_0.gguf",  # https://raw.githubusercontent.com/nomic-ai/gpt4all/main/gpt4all-chat/metadata/models2.json
        allow_download=True,
        model_path=abs_model_path,
    )

    prompt = inference_input.prompt if not inference_input.chat_session else inference_input.chat_session[-1]

    with model.chat_session(system_prompt=inference_input.system_template, prompt_template=inference_input.prompt_template):
        model.generate(prompt=prompt, temp=1.7, max_tokens=1000)
        """
        model.generate args we need to expose safely:
        (method) def generate(
            prompt: str,
            max_tokens: int = 200,
            temp: float = 0.7,
            top_k: int = 40,
            top_p: float = 0.4,
            repeat_penalty: float = 1.18,
            repeat_last_n: int = 64,
            n_batch: int = 8,
            n_predict: int | None = None,
            streaming: bool = False,
            callback: ResponseCallbackType = _pyllmodel.empty_response_callback
        ) -> (str | Iterable[str])
        Generate outputs from any GPT4All model.

        Args:
            prompt: The prompt for the model the complete.
            max_tokens: The maximum number of tokens to generate.
            temp: The model temperature. Larger values increase creativity but decrease factuality.
            top_k: Randomly sample from the top_k most likely tokens at each generation step. Set this to 1 for greedy decoding.
            top_p: Randomly sample at each generation step from the top most likely tokens whose probabilities add up to top_p.
            repeat_penalty: Penalize the model for repetition. Higher values result in less repetition.
            repeat_last_n: How far in the models generation history to apply the repeat penalty.
            n_batch: Number of prompt tokens processed in parallel. Larger values decrease latency but increase resource requirements.
            n_predict: Equivalent to max_tokens, exists for backwards compatibility.
            streaming: If True, this method will instead return a generator that yields tokens as the model generates them.
            callback: A function with arguments token_id:int and response:str, which receives the tokens from the model as they are generated and stops the generation by returning False.

        Returns:
            Either the entire completion or a generator that yields the completion token by token.
        """
        return model.current_chat_session
