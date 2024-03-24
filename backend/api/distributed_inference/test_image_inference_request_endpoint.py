# import os
# import io
# from pydantic import BaseModel

# import torch
# from fastapi import APIRouter, HTTPException
# from fastapi.responses import StreamingResponse
# from diffusers import AutoPipelineForText2Image

# router = APIRouter()

# # TODO: Handle logic and user specifications about which models are loaded and hosted in memory vs booted per request.
# model_path = os.path.join("models")


# class InferenceInput(BaseModel):
#     prompt: str

# pipe = AutoPipelineForText2Image.from_pretrained(
#     pretrained_model_or_path=os.path.join(model_path, "sdxl-turbo"),
#     torch_dtype=torch.float16,
#     variant="fp16",
# )
# pipe.to("cuda")

# @router.post(
#     "/image-inference-request",
#     tags=["Distributed Inference"],
#     summary="Generate an image based on the provided input.",
#     description="This endpoint takes in a textual description (prompt) and returns a generated image that corresponds to that description.",
#     response_class=StreamingResponse,  # Specify that the endpoint will return a streaming response
# )
# async def image_inference_request_endpoint(inference_input: InferenceInput):
#     """
#     Receive a prompt and return an AI-generated image based on the input.
#     """

#     try:

#         image = pipe(
#             inference_input.prompt,
#             num_inference_steps=2,
#             guidance_scale=0.0,
#         ).images[0]

#         # Convert PIL Image to bytes
#         img_byte_arr = io.BytesIO()
#         image.save(img_byte_arr, format="JPEG")  # Change 'JPEG' to your desired format
#         img_byte_arr.seek(0)

#         return StreamingResponse(img_byte_arr, media_type="image/jpeg")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
