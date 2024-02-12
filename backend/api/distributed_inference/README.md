# Distributed Inference research
This section primarily contains information and research, mostly links, about distributed inference, specifically how to segment models using the transformer architecture to run on either multiple gpus, or multiple nodes in parallel with a single input/output stream.

## Resources:
- [Distributed Inference with 🤗 Accelerate](https://huggingface.co/docs/accelerate/en/usage_guides/distributed_inference)
- [DistributedLLM](https://github.com/X-rayLaser/DistributedLLM)
- [DeepSpeed: Accelerating large-scale model inference and training via system optimizations and compression](https://www.microsoft.com/en-us/research/blog/deepspeed-accelerating-large-scale-model-inference-and-training-via-system-optimizations-and-compression/)
- [petals model configuration/blocking/partitoning](https://github.com/bigscience-workshop/petals/tree/mixtral/src/petals/models)
- [Handling big models for inference](https://huggingface.co/docs/accelerate/usage_guides/big_modeling)


Generally there are two approaches:
1. Load the model onto each gpu, which has the caviat of being memory intensive for peers with less memory and larger models.
2. Split the model and send the blocks/layers/chunks to the peers and have them run those layers in a method called Scheduled Pipeline Parallelism

Ideally we would use the "Model Parallelism" method as it allows for more flexibility in terms of the hardware each peer on the network can contribute, allowing smaller peers running smaller chunks of the model. However the way to do this with transformers isn't clear.

Something like this https://pytorch.org/tutorials/intermediate/model_parallel_tutorial.html, found here: https://discuss.huggingface.co/t/how-to-load-large-model-with-multiple-gpu-cards/18522/3

Ideally we would find a method that will allow us to chunk and distribute all transformer models so that this approach is model agnostic so that we can incompass all types of models from text to speech, speech to text, depth estimation, text to image, llms, etc.
