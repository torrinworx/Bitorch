# Bitorch

<p align="center">
  <img src="https://github.com/torrinworx/Bitorch/assets/82110564/1e49cbec-44c7-4b61-b186-b5f1715c5283" alt="Bitorch_flame">
</p>

A plan for building a distributed system to run AI models BitTorrent style with a secure compensation mechanism.

**Bitorch** offers a decentralized approach to distributing and running AI models, moving away from reliance on centralized corporations. In an era where the call for open-source and decentralized AI is growing louder, Bitorch steps in to address this need. Utilizing a BitTorrent-like system for model sharing and a blockchain-based mechanism for secure and fair transactions, Bitorch rewards nodes that contribute computational power. Our objective is to make the use and contribution to AI models efficient, transparent, and accessible to all. This project draws inspiration from the [Petals](https://github.com/bigscience-workshop/petals) project by BigScience, building on the idea of collaborative and open AI development.

# Main 
## 1. BitTorrent-like Model Distribution:
- **Function**: This involves distributing AI models across a network of user-contributed computers (seeders and leechers). Seeders provide chunks of the model, and leechers download and subsequently seed these chunks.
- **Incentives**: Incentivizing users to seed models is crucial. One approach is to provide faster access or enhanced services to users who contribute more to the network.
- **Implementation Challenge**: Efficiently splitting and distributing models without loss of functionality or performance, ensuring data integrity and security.

Crucial for distributing models, seeders should be incentives to distribute for free, or near free, it should be very inexpensive to download the model and start seeding.

## 2. Distributed AI Model Execution:
- **Function**: This system allows various AI models, especially those compatible with Hugging Face libraries, to run on distributed nodes.
- **Dynamic Reward System**: Implement a dynamic reward system based on demand. Higher demand for specific models increases the compensation for contributing computing power to that model.
- **Scalability and Efficiency**: Ensuring the system efficiently manages resource allocation based on model demand and network capacity.

Crucial for the actual usage of the network, hardware needs to run the models, and users want the end product of the models, be that strings, audio, video, or images, or any other content.

## 3. Monero-like Blockchain/Distributed Ledger System:
- **Function**: This system is designed to manage and track the distribution of funds and rewards in a manner that is both secure and private. Our focus is on real utility, not hype.
- **Practical Blockchain Use**: Unlike many crypto projects filled with speculative and profit-driven motives, our blockchain implementation is strictly practical. It's all about fair compensation and transparency in transactions, not about creating another speculative asset.
- **Efficiency Over Speculation**: We're choosing a consensus mechanism that is lightweight and efficient. This means moving away from Proof of Work (PoW), which is computationally heavy, towards more sustainable alternatives like Proof of Stake (PoS) or Delegated Proof of Stake (DPoS). These are less resource-intensive and more suited to our goal of maintaining a functional, efficient system.
- **Implementation Challenge**: The challenge lies in adapting or developing a blockchain system that preserves the privacy and security strengths of Monero, while ensuring it doesn’t hinder the computational performance needed for AI model execution. We're committed to making this technology work for the project's goals, not the other way around.
- **Purpose-Driven Design**: It's crucial for us to facilitate a value exchange system that’s devoid of the typical 'crypto craze'. Users and nodes contributing hardware to the network need a reliable way to transact, ensuring fair compensation and verification of model outputs, without falling into the pitfalls of the speculative crypto world.

Our approach is grounded in creating a blockchain system that serves the project’s needs: efficient, fair, and practical. We are committed to steering clear of the profit-seeking and often unsustainable practices seen in much of the cryptocurrency space.

Crucial for users and nodes on the network contributing hardware need to be able to exchange value, users need to pay the nodes that are involved in this system, and a system needs to be in place to veryify that the nodes are producing the output of the models the users pay for.

## 4. Security System:
- **Function**: The security system incorporates dedicated nodes (Security Nodes) tasked with verifying the safety and integrity of models being distributed across the network. These nodes are essential for maintaining the trustworthiness and reliability of the distributed AI models.
- **Model Verification**: Security nodes implement robust verification mechanisms, including antivirus scanners and other security protocols, to scrutinize the models for malicious code. Additionally, they might run models in isolated, controlled environments (sandboxes) to test for any suspicious behavior.
- **Incentives for Security Nodes**: Operators of security nodes are rewarded for their crucial role in safeguarding the network. This incentivization ensures that maintaining high security standards is a priority and attracts participants who are willing to allocate resources to this task.
- **Activation Protocol**: Security nodes are particularly active during the initial phases of model addition, upload, or seeding. They perform thorough checks on new models before these models are cleared for wider distribution. This protocol ensures that only clean, non-malicious models enter the network.
- **Continuous Monitoring and Updates**: To keep up with evolving security threats, the security system will require regular updates to its threat detection capabilities. Continuous monitoring and real-time analysis of models help in quickly identifying and mitigating any emergent risks.
- **Implementation Challenge**: Developing a robust and efficient security system that can handle the complexity and scale of distributed AI models without significantly impacting the network's performance. Balancing security with usability and ensuring that the security measures do not create bottlenecks or false positives is crucial.

Crucial for users to trust nodes and new seeders and modeles.

## 5. A Simple, All-Inclusive Server and GUI:
- **Function**: The focus of this component is to ensure ease of use and accessibility. The system aims to enable any user to set up a node effortlessly, whether they are tech-savvy or not. The goal is to make participation in the network as seamless as possible.
- **Straightforward Setup Process**: Users can download a setup file compatible with a wide range of devices. The installation process will guide them through configuring the type of node they wish to operate, whether it's for seeding, running AI models, transaction processing, or security verification.
- **User-Friendly GUI**: The Graphical User Interface (GUI) will be intuitive and straightforward, catering to users with varying levels of technical expertise. It should provide clear options and guidance on how to participate in the network and use the services.
- **Mandatory Contribution Mechanism**: To foster a community-driven model, users looking to utilize services like ChatGPT will be required to contribute to the network. This can be achieved through various means such as seeding, processing parts of the model, or participating in the blockchain transactions.
- **Token-Based Usage Model**: The access to and usage of AI services will be directly linked to the tokens in a user's wallet. Running out of tokens while using services necessitates further contribution to the network, either through additional seeding, computational contributions, or purchasing tokens/receiving them from other wallets. This creates a sustainable ecosystem where usage and contribution are balanced.
- **Scalability and Cross-Platform Support**: The system should be scalable to handle a large number of users and diverse types of contributions. Cross-platform support ensures wider accessibility, allowing users with different types of devices to participate.
- **Security and Privacy Features**: While focusing on simplicity and usability, the system also needs to incorporate robust security and privacy features to protect user data and transactions.
- **Implementation Challenge**: Developing a system that is both user-friendly and technically robust is challenging. The GUI must be intuitive yet powerful enough to handle diverse functions, and the setup process should be simple enough for non-technical users while offering flexibility and control for more advanced users.

Crucial for adoption of users and contributors to the network.

## 6. Output Verification and Node Integrity System:
- **Objective**: This component is designed to ensure the authenticity and accuracy of the outputs generated by the AI models across the network. It aims to prevent malicious or erroneous behavior by verifying that the nodes are genuinely processing and producing legitimate results.

- **Output Verification Process**:
   - **Model Output Validation**: Implementing mechanisms to validate the outputs of AI models. This could involve cross-referencing results with expected output patterns or using checksums to ensure the integrity of the data returned.
   - **Anomaly Detection**: Systems to detect anomalies or deviations from standard output patterns, which could indicate manipulation or errors in the computation process.

- **Node Integrity Checks**:
   - **Activity Monitoring**: Regular checks to confirm that nodes are actively participating in the network and contributing valid computational work.
   - **Behavior Analysis**: Analyzing the behavior of nodes over time to identify any suspicious or inconsistent activities that might suggest the node is not genuinely processing data.

- **Incentive Alignment for Honest Participation**:
   - **Rewarding Accuracy**: Implementing a reward system that incentivizes nodes to produce accurate and honest results. Nodes that consistently deliver valid outputs receive higher rewards or privileges within the network.
   - **Penalizing Malfeasance**: Establishing penalties for nodes found to be delivering false results or attempting to game the system. This could include temporary or permanent exclusion from the network, loss of accumulated rewards, or other disincentives.

- **Security and Privacy Considerations**:
   - **Data Privacy**: Ensuring that the verification process does not compromise the privacy of the data being processed by the AI models.
   - **Secure Verification Protocols**: Developing secure methods for output verification that cannot be easily manipulated or bypassed by malicious actors.

- **Implementation Challenges**:
   - **Balancing Efficiency and Thoroughness**: Developing a verification system that is thorough enough to ensure integrity without being so resource-intensive that it hampers the overall performance of the network.
   - **Adaptability**: Ensuring the system is adaptable to different types of AI models and can handle the evolution and advancement in AI technologies.

Crucial in maintaining the trustworthiness and reliability of the distributed AI network, ensuring that users can confidently rely on the outputs generated by the system.

## 7. Consensus Mechanism

#### Designing a Multi-Factor Consensus Mechanism

- **Proof of Seeding**: Nodes contributing to the seeding of AI models are rewarded, incentivizing the distribution and availability of models.
- **Proof of Security Compliance**: Nodes passing regular security checks gain higher trust scores, ensuring network integrity and user trust.
- **Proof of Network Support**: Rewards for nodes based on the number of leechers supported, enhancing network robustness.
- **Proof of Execution**: Recognition for nodes that successfully run AI models and provide correct results.
- **Proof of Hosting Demand**: Higher priority or rewards for nodes hosting in-demand models, ensuring adaptation to user needs.

#### Ensuring Fairness and Decentralization

- **Dynamic Trust System**: A system where trust is earned through reliable participation, with a clear path for new nodes to gain trust.
- **Decentralized Governance**: Network participants have a say in governance decisions, preventing power centralization.
- **Regular Reassessment**: Periodic reassessment of consensus factors to maintain relevance and effectiveness.
- **Inclusive Design**: The mechanism does not disproportionately favor certain nodes, allowing equitable participation.

#### Trust and Upward Mobility

- **Transparent Criteria**: Clear communication of the criteria for gaining trust and status within the network.
- **Merit-Based Advancement**: Advancement based on contribution and performance, not pre-existing status.
- **Protection Against Gaming the System**: Safeguards to prevent manipulation of the system for undue advantage.

#### Conclusion

This custom consensus mechanism is tailored to Bitorch's values of fairness, decentralization, and efficiency. By integrating various contribution and performance aspects, it aims to foster a balanced environment that rewards meaningful participation and maintains network trust.


If you are excited about the potential of distributed AI and interested in contributing to the Bitorch project, we would love to hear from you. For collaboration inquiries or to discuss how we can work together to bring this vision to life, please contact Torrin Leonard at [torrinleonard.com/contact](https://www.torrinleonard.com/contact).

Together, we can build a future where advanced AI is accessible, secure, and beneficial for all.


## Moving forward
Build out three systems to demo proof of concepts and to setup a testing environment the point of these projects are sort of first steps and proof of concepts to get down the test deployments and the first initial core components setup, not fully but just the fundamental tech will be there after we build these out.

1. bit torrent python fastapi docker network, automatically deploy 4 docker containers running the fastapi server, 1 seeder, 3 leechers, so that it can run an automatic test proof of concept of a bit torrent distribution seeding + leeching an ai model like llama or something.
2. 