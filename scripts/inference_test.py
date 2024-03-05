import os
from dotenv import load_dotenv
import requests
import gradio as gr
from typing import Optional, List, Dict

# Load environment variables from .env file
load_dotenv()

# Get backend URL from environment variable or provide a default
default_backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
# Define a textbox for server URL input


def process_streamed_response(response):
    """
    Processes a streaming response from the server and yields each line with HTML line breaks.
    """
    try:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                decoded_line_with_breaks = decoded_line.replace("\\n", "<br>")
                yield decoded_line_with_breaks  # Yield each line with HTML line breaks
    except Exception as e:
        # Log the exception and rethrow or handle accordingly
        print(f"Error while streaming response: {e}")
        raise e


def request_inference(
    messages: Optional[List[Dict[str, str]]],
):
    # Perform the request to the endpoint with stream=True if streaming is needed
    response = requests.post(
        f"http://localhost:8000/inference-request",
        json={
            "prompt": None,
            "messages": messages,
            "stream": True,
        },
        stream=True,
    )

    return process_streamed_response(response)


# Function to generate model predictions.
def predict(message, history):
    # Convert history from Gradio format to `request_inference` function expected format
    messages = []
    system_statement = {
        "role": "system",
        "content": "You are an AI assistant that follows instruction extremely well. Help as much as you can.",
    }
    messages.append(system_statement)

    # Add user and assistant messages to the chat_session
    for dialog in history:
        user_message, assistant_message = dialog

        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": assistant_message})

    # Add the latest message from the user to the chat_session
    messages.append({"role": "user", "content": message})

    # Call request_inference which should return a generator if stream=True
    inference_generator = request_inference(messages=messages)

    # Yield from the generator to pass streamed content to Gradio interface
    partial_message = ""
    for new_token in inference_generator:
        partial_message += new_token
        yield partial_message


# Setting up the Gradio chat interface.
interface = gr.ChatInterface(
    fn=predict,
    title="Bitorch Chat",
    description="Ask a model anything",
    examples=["How to cook a fish?", "Who is the president of US now?"],
)
interface.queue()  # Enable the queue for the interface using the .queue() method.
interface.launch()  # Launching the web interface.
