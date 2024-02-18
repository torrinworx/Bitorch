from pydantic import BaseModel
from typing import Union, Dict, Any


class DisInfUtils:
    """
    General utils for distributred inference.
    """


class Data:
    """
    Class definitions for data types, each type must be interchaingable with input/output for any combinations of data types for ai models.
    """

    class TextData(BaseModel):
        file_types = [
            ".txt"
        ]  # List of file formats accepted by this data type, eg .txt, .json, .png, .jpg, .jpeg, .glb, etc., leave empty if Data type not expected to allow for file inputs.
        content: bytes

        def load_content():
            # Some function to load the data type content from a temp dir or directly from the inference request from fastapi.
            # Loads content into the content: bytes variable.
            pass

        # TODO: Validators:

    class ImageData(BaseModel):
        file_types = [".png", ".jpeg", ".jpg"]
        content: bytes

        def load_content():
            # Some function to load the data type content from a temp dir or directly from the inference request from fastapi.
            # Loads content into the content: bytes variable.
            pass

    class AudioData(BaseModel):
        file_types = [".mp3", ".flac"]
        content: bytes

        def load_content():
            # Some function to load the data type content from a temp dir or directly from the inference request from fastapi.
            # Loads content into the content: bytes variable.
            pass


class ModelDispatcher:
    """
    This class is designed to take in an InferenceRequest, search the available models on the server, review if they are present, then run the model given the input data and returns the output to ther Inference requestor.
    """

    # TODO: Somehow figure out a way to take in the inference request, map it to the model, and map the data sent by the inference-request to the model running in the huggingface library dynamically so that we don't
    # have to manually write code to map the params of the requests to the params of the models in the transformers library pipeline methods for each model. The mapping of params from the InferenceRequest to the
    # transformer model params needs to be agnostic of the params and the model itself. Params should be automatically applied to the model, and running the model, input/output, shouldn't be hard-coded and should
    # be dynamic to whatever the model is that the user of my peer has uploaded if supported by huggingface.transformers.


class InferenceRequest:
    """
    Pydantic model to handle inference requests from peers and validate and sanatize input.
    """

    """
    TODO: Better way to handle this so that we don't have to define a list the more we add to Data? should be a list of these, so if model is stable diffusion, Data.TextData is the only thing to be included in 
    input_data, and Data.ImageData is the only data class used for returning the data to the user because that's what Stable Diffusion takes in.
    
    For another multi modal model like GPT4 Vision, the list of input_data would be Data.TextData and Data.ImageData, output_data would also be Data.TextData and Data.ImageData.
    
    For a model like Whisper, input_data would consist of Data.AudioData, and output_data would be Data.TextData.
    """
    input_data = Union[Data.TextData, Data.ImageData, Data.AudioData]
    model_params = Dict[Any]
    output_data = Union[
        Data.TextData, Data.ImageData, Data.AudioData
    ]  # Optional until the result is processed and returned, otherwise request fails I guess?
