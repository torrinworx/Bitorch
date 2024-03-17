<div align="center">

# **Bitorch**

Open-Source distributed inference network

<img src="/docs/images/bitorch_flame.png" alt="Bitorch_flame" style="width: 30%; height: auto;">

<h3>

[Documentation]() | [Discord]()

</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/torrinworx/Bitorch)](https://github.com/torrinworx/Bitorch)

</div>

> [!CAUTION]
> This project is still in the early development stages. Some features mentioned are not yet implemented. Bitorch is not recommended for production use at this time.

---

## Description
A simple way to host and use open source AI models for public or private tasks across all modalities. Contribute to the public Bitorch network according to your ability, utilize it according to your needs. Help dismantle our reliance on monopolies that hold hostage computational power built on our data.

**What is Bitorch?**
With Bitorch you can run parts of, or the entirety of AI models on devices like your desktop, laptop, server, or Raspberry Pi collectively. Models that can generate text, images, audio, video, and more, all can be run from one platform. Bitorch makes it easy to manage these models while allowing you to contribute to the Bitorch network. You can choose to run your server privately, for your use only, or publicly, to help the network and enjoy faster compute times for your operations.

**How can a real user use this?**
In time, Bitorch will serve not just as a backend server, but also as a frontend client. With this client, you'll be able to use the Bitorch network much like LibreChat, GPT4All, Gemini, Copilot, and ChatGPT. You'll be able to manage your contribution to the network and your usage of the network all in a single desktop app or docker container.

**What makes Bitorch decentralized?**
Bitorch decentralizes AI model hosting and inference with a peer exchange (PEX) system, similar to BitTorrent and Bitcoin's decentralized networks. This structure allows the platform to scale naturally as more participants join, share AI models, and process inference requests, leading to better response times. It promotes diversity in model availability, ensuring access to effective community-vetted models. With this, Bitorch democratizes access to cutting-edge AI technologies, sidestepping the pitfalls of innovation hoarding by centralized monopolistic corporations.

Moreover, this collaboration enables the running of sophisticated and demanding AI models that would be challenging or impossible to operate on a single device.

**What about dependency hell?**
Bitorch will solve the problem of model dependency hell by abstracting away the setup of new models and modalities into a **plugin system** which will provide a clear and concise standard for anyone to add models to the network regardless of architecture. The philosophy of the project is "a single inference request", meaning that all inference requests, regardless of modality, are run using a single inference request endpoint with three simple parts:

`Input Data + Model Parameters --> Model + Dependencies -->  Output Data`

This approach will simplify the setup needed acrosss modalitities and architectures and provide a clear standard models can adopt and conform to for broader usage on consumer hardware.

**What do I need to know about Bitorch?**
Bitorch has four important main components:
1. **Peer Exchange** network allowing peers on the network to communicate with each other in a decentralized manner.
2. **Distributed Inference** allows individual or groups of peers to run AI models collectively through data or model parallelism.
3. **Model Distribution** allows for new peers to join the network and easily pull chunks or entier models to host and run without the need for external model hosting services.
4. **Compensation Mechanism** ensentivises peers to join the public network to host and run models and be fairly compensated for their contribution to the network.

These four components 
> They say, "Jump" And ya say, "How high?"

*-- Rage Against the Machine*

---

# Roadmap
Bitorch is in a proof of concept phase. We are trying to build out the core codebase and feature set, as such not all of our ambitious features are currently operational. This roadmap outlines some of the major features we wish to implement in the future:

- [ ] **Model agnostic inference** - Host and inference multiple modalities on multiple machines.
- [ ] **Model chunking and inference** - Run larger models on multiple machines.
- [ ] **Model agnostic plugin system** - allowing anyone to build and share plugins to load models and model chunking systems.
- [ ] **Model management system** - allows users to manage which models and model chunks they want to host and inference.
- [ ] **Distributed trasaction ledger** - a secure, private, and practical management system of funds and rewards, emphasizing real utility with a practical blockchain usage approach, efficiency through sustainable consensus mechanisms like PoS or DPoS, while avoiding speculative crypto trends, aiming to serve the project's needs for efficient, fair, and purpose-driven transactions among users and hardware-contributing peers.
- [ ] **Multi-factor consensus mechanism** - a custom consensus mechanism focused on rewarding meaningful participation and maintaining network trust, integrating multiple factors like seeding AI models, security compliance, network support, execution success, and hosting demand, while ensuring fairness, decentralization, and efficiency.
- [ ] **All inclusive server and GUI**, a server and GUI designed for simplicity and inclusivity, easy setup and participation for users regardless of technical expertise, featuring user-friendly installation, token-based usage, scalability, cross-platform support, and strong security measures.
- [ ] **Output verification and peer integrity system** - Authenticating the accuracy of AI model outputs to prevent malicious activities, involving model output validation, anomaly detection, peer integrity checks with activity monitoring, and behavior analysis, alongside incentivizing accurate contributions through rewards and penalizing dishonesty, while considering data privacy and secure verification protocols.
- [ ] **Distributed model training** - TBD

# Challenges
The biggest challenge with Bitorch at the moment is model parallelism and model chunking. Each ai model architecture is unique and requeires special consideration when implementing a decentralized inference mechanism. This is a sevier limitation to Bitorch's capabilities, as right now the only feasable way to implement a distributed inference network is with data parallelism (loading the entire model on a single peer). This limits the potential of the network by the size of the models an individual peer can load onto it's hardware. See the document in [/backend/api/distributed_inference/README.md](/backend/api/distributed_inference/README.md) for a summary of information, resources and solutions to the problem.

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
TODO
- Docker 25.0.3 or greater (if simulating network) https://docs.docker.com/get-docker/
- Docker Compose v2.24.6 or greater (if simulating network) (installs with docker)
