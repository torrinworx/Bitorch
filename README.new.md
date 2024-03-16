<div align="center">

# **Bitorch**

Open-Source distributed inference

<img src="/docs/images/bitorch_flame.png" alt="Bitorch_flame" style="width: 30%; height: auto;">

<h3>

[Documentation]() | [Discord]()

</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/torrinworx/Bitorch)](https://github.com/torrinworx/Bitorch)

</div>

> [!CAUTION]
> This project is still in very early stages of development, as such some of the features discussed in this readme haven't been created yet. This project is not ready for production use.

## Description
Bitorch allows you to host and run AI models on a distributed, peer-to-peer network. The aim is to make it straightforward for anyone to self-host either portions or entire AI models of any type.

This means you can run parts of, or entire AI models on devices like your desktop, laptop, server, or Raspberry Pi. These models can generate text, images, audio, video, and more, all from one platform. Bitorch makes it easy to manage these models, offering you the opportunity to contribute computational power to the Bitorch network. You can choose to run your server privately, for your use only, or publicly, to help enhance the network and enjoy faster compute times for your operations.

What about user interaction? In time, Bitorch will serve not just as a backend server, but also as a frontend client. This means you could host your own AI-driven applications, like a ChatGPT clone, on your device, using Bitorch as the backend, whether accessing it directly or through the Bitorch network.

Bitorch uses a peer exchange (PEX) system, similar to those of BitTorrent and Bitcoin, ensuring the network is decentralized. This setup means that as more users join the network, share models, and accept public requests, the overall response time improves. It also encourages a rich variety of models on the network, increasing access to the best and community-endorsed models for new users. This democratizes access to cutting-edge AI technologies, sidestepping the pitfalls of innovation hoarding by centralized monopolistic corporations.

Bitorch will have four main components:
1. **Peer Exchange** network allowing peers on the network to communicate with each other in a decentralized manner.
2. **Distributed Inference** allows individual or groups of peers to run AI models collectively through data or model parallelism.
3. **Model Distribution** allows for new peers to join the network and easily pull chunks or entier models to host and run without the need for external model hosting services.
4. **Compensation Mechanism** ensentivises peers to join the public network to host and run models and be fairly compensated for their contribution to the network.

> They say, "Jump" And ya say, "How high?"

*-- Rage Against the Machine*

# Documentation
The Bitorch backend server is written in Python 3.11.0, and uses the FastAPI framework. The design of the server is such that any model can be loaded, and is agnostic to data input, data validation, model loading, model validation, and data output, as each are expected to be unique to each model.

## Setup
### Prerequisites
- Python 3.11.0 or greater https://www.python.org/downloads/

### Steps
1. Install the pipenv package using pip:
    ```bash
    $ pip install pipenv
    ```
2. Install the project environment:
    ```bash
    $ pipenv install
    ```
3. Run the server:
    ```bash
    $ py run.py
    ```

## Development setup
- Docker 25.0.3 or greater (if simulating network) https://docs.docker.com/get-docker/
- Docker Compose v2.24.6 or greater (if simulating network) (installs with docker)
