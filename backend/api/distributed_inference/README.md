# Distributed Inference research
This section primarily contains information and research, mostly links, about distributed inference, specifically how to segment models using the transformer architecture to run on either multiple gpus, or multiple nodes in parallel with a single input/output stream.

## Resources:
- [Distributed Inference with 🤗 Accelerate](https://huggingface.co/docs/accelerate/en/usage_guides/distributed_inference)
- [DistributedLLM](https://github.com/X-rayLaser/DistributedLLM)
- [DeepSpeed: Accelerating large-scale model inference and training via system optimizations and compression](https://www.microsoft.com/en-us/research/blog/deepspeed-accelerating-large-scale-model-inference-and-training-via-system-optimizations-and-compression/)
- [petals model configuration/blocking/partitoning](https://github.com/bigscience-workshop/petals/tree/mixtral/src/petals/models)
- [Handling big models for inference](https://huggingface.co/docs/accelerate/usage_guides/big_modeling)
- https://github.com/huggingface/blog/blob/main/accelerate-large-models.md
- https://arxiv.org/pdf/2209.01188.pdf
- https://huggingface.co/docs/accelerate/usage_guides/big_modeling


Generally there are two approaches:
1. Load the model onto each gpu, which has the caviat of being memory intensive for peers with less memory and larger models.
2. Split the model and send the blocks/layers/chunks to the peers and have them run those layers in a method called Scheduled Pipeline Parallelism

Ideally we would use the "Model Parallelism" method as it allows for more flexibility in terms of the hardware each peer on the network can contribute, allowing smaller peers running smaller chunks of the model. However the way to do this with transformers isn't clear.

However we might be able to settle for the data parallelism method, or perhaps even both in some kind of dynamic system that selects the best method based on the size of the model, and the size of peer resources.

Something like this https://pytorch.org/tutorials/intermediate/model_parallel_tutorial.html, found here: https://discuss.huggingface.co/t/how-to-load-large-model-with-multiple-gpu-cards/18522/3

Ideally we would find a method that will allow us to chunk and distribute all transformer models so that this approach is model agnostic so that we can incompass all types of models from text to speech, speech to text, depth estimation, text to image, llms, etc.


So here is the plan to simulate a peer uploading a new model to the network:
1. New model is loaded into a directory in full.
2. Model get's split into whatever chunks that it can be using huggingface Accelerate or whatever tools for Transformers.
3. These chunks, and the full model file, are then available to download from the peer hosting it
4. Use some kind of a bittorrent protocal to host, download, and seed the model, and model chunks to other nodes (we can skip this for building out the distributed inference and make this later, right now it can just directly download from the peer uploading the model files.)
5. Each peer that chooses to run the model will download a chunk of it (or for testing it can download the full model.)
6. We simulate a request, sending needed data to all endpoints running the chunks of the model
7. The peers running model chunks process the request, sending data to each other through the selected path chosen by the client peer requesting use of the model.
8. The last peer in the chain sendsd the result back to the client requesting the use of the model.

# First test
For the first test I don't think it is necissary to chunk and run model parallelism. Right now we should just focus on sending the full model, something like mixtral or sd to each peer on the network, then have them be able to be selected and "host" or run the model for users like an api would.
