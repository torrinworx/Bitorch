# Backend Documentation
---
The `README.md` file serves as the central documentation hub for the Bitorch backend server. Its primary purpose is to provide a comprehensive and newcomer friendlly guide to understanding the structure, components, and operation of the backend system.

Let's build some cool shit.

---
## /run.py
`run.py` serves as the execution script for launching the Bitorch backend application. Its primary role is to manage the server's configuration, environment checks, and the actual start-up process. This file ensures the reliable deployment and operation of the Bitorch backend. This file is placed at the root of the project to make running the backend server a simple `python run.py` command.
Key Functions:
- **Server Configuration**: Determine the server environment, default port, and backend URL.
- **Port Availability**: Find an available port for the server to listen on.
- **Environment Checks**: Conduct checks during development mode to ensure the necessary environment setup.
- **Server Start-up**: Initialize the server using FastAPI and UVicorn, taking into account the specified environment.

---
## /backend/main.py
`main.py` serves as the entry point and central coordinator for Bitorch. Its primary responsibilities include initializing the application, configuring essential components, and managing critical processes. This file ensures the smooth operation and functionality of the entire backend system.

Key Functions:
- **Initialization**: Load environment variables, set up core components, and configure the FastAPI application.
- **Middleware and CORS**: Manage middleware for request handling and set Cross-Origin Resource Sharing (CORS) policies.
- **API Routing**: Define and route HTTP requests to relevant endpoints using the API router.
- **Startup Tasks**: Execute essential tasks during application startup.
- **Scheduler**: Run scheduled tasks and background processes.
- **MongoDB Connection**: Handle the opening and closing of connections to the MongoDB database.
- **Logging**: Configure logging format and level for monitoring and debugging.

---
## /backend/api
The `/backend/api` directory serves as the entry point for all major components of the Bitorch server, each residing in its respective subfolder (e.g., `/backend/api/pex`). This modular approach allows for a clear and organized separation of functionality within the backend system.

### Structure and Purpose

- **Endpoint Handling**: Each subfolder, such as `/backend/api/pex`, contains the necessary files to run a specific section of the application. For instance, in the `/backend/api/pex` example, you'll find files like `peer_list.py`, `register.py`, and more, which collectively define the endpoints required for the Peer Exchange network functionality of a peer.

- **Automatic Endpoint Mounting**: The magic happens in the `/backend/api/__init__.py` file, which automatically mounts these defined endpoints to the FastAPI server. This means that you don't need to manually configure every endpoint; they are seamlessly integrated into the server.

- **Database Operations**: Within these subfolders, you'll also find files like `pex_mongo.py`, which are responsible for handling MongoDB operations specific to the featured functionality. This ensures that database interactions are localized to the relevant component.

- **Task Management**: Some components, like the Peer Exchange network, may have `pex.py`, housing various classes for `PexTasks` that can be executed via the scheduler or during startup. Additionally, `PexEndpoints` may be available to facilitate calls to endpoints on other peers running similar functionality.

- **Utility Functions**: To maintain a clean separation of concerns, the `/backend/api` structure also accommodates feature-specific utility functions in classes like `PexUtils`. Unlike the global `/backend/utils`, these utilities are tailored to the operation of the specific feature.

### Design Principles

The design philosophy underlying this structure is to keep feature-specific code contained within its respective `api` subfolder. This approach promotes organization and maintains a clear separation of concerns among the various features of the Bitorch backend.

As new features are developed, it is recommended to adhere to these design principles, ensuring that each feature's functionality remains neatly encapsulated within its designated `api` folder. This approach enhances maintainability and simplifies the integration of new components into the backend system.

---
## /backend/utils

The `/backend/utils` directory houses a collection of general-purpose utility modules and methods designed to facilitate smooth interaction and standardization among all features within the `/backend/api` directory. These utilities serve as a foundational layer upon which individual features can build and customize as needed. utils ensures that the backend operates efficiently and reliably, with a strong focus on data validation and security when interacting with external peers on the network. This approach promotes consistency, code reusability, and centralized control over critical components like the database and task scheduling. 

### Key Components

1. **Mongo Database Operations**: The `mongo.py` file handles MongoDB operations in a singleton manner, ensuring that all features operate on the same instance of the MongoDB database. This centralized approach enhances data consistency and integrity across the application.

2. **Task Scheduler**: Similar to `mongo.py`, the `scheduler.py` file follows the singleton design pattern to provide a shared scheduler instance. This ensures that all features utilize the same scheduler for managing scheduled tasks and background processes. The scheduler has also been designed as a decorator to simply wrap around functions desired to be scheduled (See example in /backend/utils/scheduler.py).

3. **General Utility Functions and Classes**: The `utils.py` file contains various general-purpose utility functions and classes that can be employed throughout the backend. These utilities simplify common tasks and promote code reusability.

### Notable Features in `utils.py`

Within `utils.py`, several key features stand out:

- `Utils.env`: This simple variable allows you to identify the current environment without the need to repeatedly call `os.getenv(...)`. It streamlines environment detection within the codebase.

- `Peer`: A Pydantic model representing a single peer on the network. This model plays a pivotal role in data validation when receiving input from other peers on the public network. It ensures that data received is safe for storage in the MongoDB database. Additionally, internal fields within the `Peer` model may be used for internal purposes, marked with an underscore (_) to indicate their non-public nature.

- `PublicPeerResponse`: This filter is designed to remove non-public fields from any data type nested within it. While it simplifies data filtering for endpoints returning a `Peer` model class to other network nodes, it may have limitations with more complex data types that require additional consideration.

[For more in-depth documentation of /backend/utils, visit /backend/utils/README.md](/backend/utils/README.md)

---
## /backend/middleware

The `/backend/middleware` directory operates in a manner similar to `/backend/api`, but with a distinct focus on manipulating the behavior of the FastAPI framework as needed. Each file within this directory is automatically mounted to the FastAPI middleware by `/backend/middleware/__init__.py`, allowing for the fine-tuning of FastAPI's functionality.

### Middleware Operations

The operations and code within this directory are designed to influence FastAPI itself, rather than building core features. A notable example is `rate_limit.py`, which interfaces with FastAPI to enforce rate limiting on requests made by peers on the network. This middleware plays a critical role in maintaining network integrity and applies specific rules to peers, including marking them as blacklisted or rate-limited within their `Peer` class if they fail to adhere to network rules.

### Use Cases and Scope

The `/backend/middleware` directory focuses on tasks that require interaction with FastAPI, Pex functionality, and MongoDB functionality simultaneously. It is important to note that these operations are specific to enhancing FastAPI behavior and should not be used to build core features. If an operation exclusively requires Pex and MongoDB functionality, it would be placed outside the middleware folder.
