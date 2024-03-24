import os
import random
import traceback
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Set

import httpx

from ...utils import Utils, Peer
from ...utils.scheduler import scheduler
from ...utils.mongo import MongoDBManager


COLLECTION = "peers"


# TODO: Add better error handling
class PexTasks:
    @staticmethod
    async def startup():
        """
        Initialize startup tasks for the peer-to-peer network.

        This function is responsible for establishing initial peer connections.
        It checks if the current peer list is empty and, if so, searches for
        additional peers to connect to for starting network activities.
        """
        # Add self to peer list:
        my_peer = await Utils.get_my_peer()
        await PexMongo.add_peer(peer=my_peer)

        await PexTasks.join_network()

    @staticmethod
    async def join_network():
        """
        Join the peer-to-peer network.

        This function attempts to join the network by connecting to source peers
        specified in the .config.json file. It's primarily used during the initial
        deployment of a peer. If all source peers are unresponsive, it indicates
        either a lack of internet connectivity or that all source peers are down.

        In development mode, if the current peer is 'peer0', no registration is
        required as it acts as an original source peer.
        """
        my_peer = await Utils.get_my_peer()
        if Utils.env == "development" and my_peer.name == "peer0":
            return  # No registration needed because we are a source peer

        peers = Utils.get_source_peers()
        await PexMethods.register(peers=peers)

    # @scheduler.schedule_task(trigger="interval", seconds=10, id="peer_list_monitor")
    @staticmethod
    async def peer_list_monitor():
        """
        Periodically monitors and updates the status of peers in the P2P network.

        This periodically scheduled task runs every 10 seconds to review the list
        of all known peers and their last activity timestamps. It performs checks to
        determine if a peer has been inactive and follows these rules:

        - If a peer has not been seen for over 10 minutes, a health check is
        initiated to ascertain if the peer is still alive.
        - If the health check fails, the peer's status is updated to indicate
        it is no longer active. The peer is not deleted from the database but
        rather marked as inactive.
        - For peers that have been inactive for between 5 to 10 minutes, an attempt to
        re-register them is made to re-establish active status.

        This function ensures that the network maintains an up-to-date view of peer
        availability and helps to maintain a robust, connected P2P network topology.

        TODO: Change the timing of the task and the period for health checks to be a
        .env var instead of hard coded.

        TODO: Ensure that this thing runs every 10 seconds/## interval whenever this
        function actually finished so that peers don't double check eachother in a short
        time period.
        
        TODO: Introduce some data clean up to keep mongodb size small, remove request body
        and other large chunks of data from the request history if the request is older 
        than a certain time. but keep the bare bones logs so that we still have a record.
        This will preserve space in the db, might not be necissary if the size is minimal,
        but it might add up with multiple peers and lots of requests coming in so idk.
        """
        my_peer_list = await PexMongo.get_all_peers()
        current_time = datetime.now()
        five_minutes_ago = current_time - timedelta(minutes=5)
        ten_minutes_ago = current_time - timedelta(minutes=10)
        for peer in my_peer_list:
            peer_last_seen = datetime.fromisoformat(peer.last_seen)
            if ten_minutes_ago > peer_last_seen:
                # # Perform health check
                # alive = await PexMethods.health_check(peer)
                # if not alive:
                #     # Handle marking the peer as inactive in the database
                pass

            elif five_minutes_ago < peer_last_seen < ten_minutes_ago:
                # Attempt to re-register peer to verify if it is still active
                await PexMethods.register([peer])


class PexMethods:
    """
    The PexMethods class contains a collection of static methods that correspond to
    the public API endpoints defined in the backend/api/pex folder, which are exposed
    through a FastAPI application interface. Each method encapsulates functionality
    available to be called upon by other peers, aligning with the RESTful design of
    peer-to-peer network interactions.

    These methods facilitate critical network operations such as peer registration,
    peer list synchronization, health checks, and various other coordination tasks
    required to ensure the integrity and functionality of the peer-to-peer network.
    """

    @staticmethod
    async def register(peers: List[Peer.Internal]):
        """
        Request registration from a list of peers within the network.

        This asynchronous method initiates the registration process by introducing the current peer
        to the peers specified in the 'peers' parameter. The goal is to mutually exchange information
        and update the peer list. Upon successful registration, the peer's internal network information
        is shared, and a truncated peer list from the contacted peer is received and processed.

        Parameters:
        - peers (List[Peer.Internal]): A list of Peer.Internal instances representing the target peers
          for registration.

        Returns:
        - None: Registration does not return a value but instead updates internal state.

        This method also has a built-in mechanism to avoid excessive recursion through peer networks by
        monitoring the depth of registration calls and limiting them based on a predefined threshold.
        """
        # Retrieve the current recursion depth and the limit flag
        depth, limit_reached = await PexUtils.get_depth()

        if limit_reached:
            # TODO: proper logging/console info, fastapi logging style maybe?
            print(
                f"Recursion depth limit reached, currently at depth {depth}. Stopping further registrations."
            )
            return

        async with httpx.AsyncClient() as client:
            for peer in peers:
                try:
                    peer_url = f"http://{peer.ip}:{peer.port}/register"
                    my_peer = await Utils.get_my_peer()

                    print(f"Attempting to register with peer at {peer_url}")
                    response = await client.post(peer_url, json=my_peer.dict())
                    response.raise_for_status()  # Raises an exception for HTTP error responses

                    response_data = response.json()
                    print(f"Registered with {peer.ip} successfully.")

                    # Obtain the peer list provided by the peer we've just registered with
                    new_peer_list = [
                        Peer.Internal(**p_data)
                        for p_data in response_data["content"].get("peer_list", [])
                    ]

                    # Filter to exclude peers that are already known or not compliant
                    filtered_new_peers = await PexUtils.filter_peers_registered(
                        new_peer_list
                    )

                    # Add peers to db
                    await PexMongo.add_peers(filtered_new_peers)

                    # Make a recursive call to continue the registration process
                    if not limit_reached:
                        await PexMethods.register(filtered_new_peers)

                except Exception as e:
                    print(f"Failed to register with {peer.ip}: {str(e)}")
                    traceback.print_exc()

    # TODO:
    @staticmethod
    async def update_peer_list():
        """
        Request an updated peer list from a list of peers.

        Run periodically for given peers in the peer_list who this peer
        hasn't requested an update from in a while.

        Measures should be put in place to prevent spam and block peers
        that spam this endpoint.
        """
        pass

    # TODO:
    @staticmethod
    async def health_check():
        """
        Sends health checks to a list of peers in the network.

        This function is scheduled to run periodically. It sends health check
        messages to other peers to ensure network integrity and the availability
        of peers.

        TODO: Implement an algorithm to checkup on peers in the peer_list that haven't
        been communicated with in a while to check if they are alive. Remove if no
        response.
        """
        pass


class PexUtils:
    """
    PexUtils is a utility class that provides miscellaneous static methods which
    support the functionality of the peer-to-peer networking layer. These methods
    are designed to assist with tasks that are ancillary to the core P2P operations,
    such as filtering known peers, handling recursion depths, and possibly in future,
    integrating with rate-limiting or blacklisting mechanisms.

    The methods in this class play a supportive role throughout various areas of the
    P2P network implementation, offering reusable logic to ensure that higher-level
    functionalities such as peer registration and network maintenance can operate.
    """

    @staticmethod
    async def filter_peers_registered(
        peer_list: List[Peer.Internal],
    ) -> List[Peer.Internal]:
        """
        Filters a given list of Peer.Internal instances, removing peers that are already registered.

        This function is designed to prevent duplicate registrations by checking the input list of peers
        against the current list of registered peers obtained from the database. It ensures that only
        peers not currently registered are retained. Additionally, this function is designed to remove
        peers that are blacklisted, although this functionality is pending future implementation.

        Peers are uniquely identified by their IP addresses, and the filtering is done on this basis.

        Parameters:
        - peer_list (List[Peer.Internal]): A list of Peer.Internal instances to be filtered.

        Returns:
        - List[Peer.Internal]: A list of Peer.Internal instances that are not already registered.

        NOTE:
        - This function assumes that each peer has a unique IP address for identification purposes.
        """
        my_peer_list = await PexMongo.get_all_peers()

        # Create a set of IPs from my_peer_list for quick lookup
        known_ips = {peer.ip for peer in my_peer_list}

        # Filter out any peers that are already in my_peer_list
        return [peer for peer in peer_list if peer.ip not in known_ips]

    @staticmethod
    async def filter_bad_peers(
        peer_list: List[Peer.Internal],
    ) -> List[Peer.Internal]:
        """
        This function should filter out blacklisted and poor quality or not trusted peers to help provide good quality peers for connection for new users.

        The implementation of blacklist and ratelimiting is pending and this function will be implemented when that system is built.
        """
        return peer_list

    @staticmethod
    async def get_depth() -> Tuple[int, bool]:
        """
        Calculates the recursion depth for peer registration based on the number of peers
        in the peer list. If the number of peers is greater than or equal to the value
        specified in the 'MAX_DEPTH' environment variable, that value is used as the depth.
        Otherwise, the depth is set to the length of the peer list.

        Returns:
        - Tuple[int, bool]: A tuple containing the calculated recursion depth and a boolean
                            indicating whether the recursion limit has been reached.
        """

        # Assign a default max_depth if the environment variable is not set or not an integer
        default_max_depth = 100  # A sensible default value
        try:
            max_depth = int(os.getenv("MAX_DEPTH", default_max_depth))
        except ValueError:
            max_depth = default_max_depth  # Fallback to default if conversion fails

        # Get the current list of peers from the database
        peer_list = await PexMongo.get_all_peers()

        # Calculate the current depth based on the size of the peer list
        current_depth = len(peer_list)

        # Determine if the recursion depth limit has been reached
        limit_reached = current_depth >= max_depth

        # If the limit has been reached, use the max_depth as the depth
        depth = max_depth if limit_reached else current_depth

        return depth, limit_reached


class PexMongo:
    """
    PexMongo is a utility class that serves as an interface to the MongoDB database
    for operations related to managing peer information within the peer-to-peer network.
    It encapsulates the interaction with the 'peers' collection, providing methods
    for CRUD operations on peer data.

    The methods within the class rely on the custom MongoDBManager to handle database
    queries and ensure the application's data persistence layer remains decoupled from
    the core networking logic. This approach facilitates ease of maintenance, scalability,
    and potential integration with other database management systems.

    Functions provided by this class include adding new peers or updating existing ones,
    removing peers, retrieving the list of all peers, and updating peers' 'last seen'
    timestamps and request history. Serialization of MongoDB's ObjectId to strings is
    also handled to ensure data compatibility and ease of JSON serialization for network
    communication.
    """

    @staticmethod
    def serialize(data):
        """
        Serialize MongoDB data by converting ObjectId to string.
        """
        if isinstance(data, list):
            return [PexMongo.serialize(item) for item in data]
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, ObjectId):
                    data[key] = str(value)
        return data

    @staticmethod
    async def add_peers(peer_list: List[Peer.Internal]) -> bool:
        """
        Serialize MongoDB data by converting ObjectId to string.
        """
        success = True
        for peer_model in peer_list:
            peer_dict = peer_model.dict()
            peer_exists = await MongoDBManager().find_documents(
                COLLECTION, peer_dict
            )
            if not peer_exists:
                await MongoDBManager().insert_document(COLLECTION, peer_dict)
            else:
                success = False
        return success

    @staticmethod
    async def add_peer(peer: Peer.Internal) -> str:
        """
        Add a new peer to the database or update it if it already exists.
        Check if a peer with the same IP address exists, and update its details if other fields have changed.
        """
        peer_dict = peer.dict()
        existing_peer = await MongoDBManager().find_documents(
            COLLECTION, {"ip": peer_dict["ip"]}
        )
        if existing_peer:
            await MongoDBManager().update_document(
                COLLECTION, {"ip": peer_dict["ip"]}, peer_dict
            )
            return "Peer updated"
        else:
            await MongoDBManager().insert_document(COLLECTION, peer_dict)
            return "New peer added"

    @staticmethod
    async def get_all_peers() -> List[Peer.Internal]:
        """
        Retrieve all peers from the database and remove the '_id' field. Results are unfiltered and contain blacklisted peers.
        """
        peers = await MongoDBManager().find_documents(COLLECTION, {})
        result = []
        for peer_dict in peers:
            peer_dict.pop("_id", None)
            result.append(Peer.Internal(**peer_dict))
        return result

    @staticmethod
    async def get_random_peers(
        exclude_peers: Set[Peer.Internal] = None, filter_bad_peers: bool = True
    ) -> List[Peer.Internal]:
        """
        Retrieve a configurable random sample of peers from the database,
        excluding those in the exclude_peers set.

        Args:
            exclude_peers (Set[Peer.Internal]): A set of Peer.Internal objects to exclude from the results.
            filter_bad_peers (bool): Flag to filter out bad peers or not.

        Returns:
            List[Peer.Internal]: A list containing the requested number of peers.
        """
        all_peers = await PexMongo.get_all_peers()
        # Assuming PexUtils.filter_bad_peers is a method that filters out peers based on certain criteria.
        all_peers = (
            await PexUtils.filter_bad_peers(all_peers)
            if filter_bad_peers
            else all_peers
        )

        # Create a set of IP addresses for the peers to be excluded.
        exclude_ips = {peer.ip for peer in exclude_peers} if exclude_peers else set()

        # Filter out the excluded peers based on their IP addresses.
        filtered_peers = [peer for peer in all_peers if peer.ip not in exclude_ips]

        raw_share_peers = os.getenv("SHARE_PEERS", "50")  # Default set to 50.

        match raw_share_peers:
            case "0":
                return []
            case "-1":
                return filtered_peers
            case _:
                try:
                    share_count = int(raw_share_peers)
                except ValueError:
                    raise ValueError(
                        "Environment variable 'SHARE_PEERS' must be an integer"
                    )
                if share_count < 0:
                    raise ValueError(
                        "'SHARE_PEERS' must be a non-negative integer or -1"
                    )

                available_peer_count = min(share_count, len(filtered_peers))
                return (
                    random.sample(filtered_peers, available_peer_count)
                    if available_peer_count > 0
                    else []
                )

    @staticmethod
    async def remove_peer(peer: Peer.Internal) -> bool:
        """
        Remove a peer from the database.
        """
        peer_dict = peer.dict()
        return await MongoDBManager().delete_document(COLLECTION, peer_dict)

    @staticmethod
    async def update_peer(
        old_peer: Peer.Internal, new_peer: Peer.Internal
    ) -> Optional[Peer.Internal]:
        """
        Update a peer's info.
        """
        result = await MongoDBManager().update_document(
            collection_name=COLLECTION,
            query=old_peer.dict(),
            update=new_peer.dict(),
        )
        return new_peer if result else None

    @staticmethod
    async def get_peer(ip: str) -> Optional[Peer.Internal]:
        """
        Get an individual peer by their IP address.
        """
        peer_dict = await MongoDBManager().find_documents(COLLECTION, {"ip": ip})
        if peer_dict:
            return Peer.Internal(**peer_dict[0])
        return None

    @staticmethod
    async def update_peer_request_history(
        client_ip: str, request_info: Peer.RequestInfo
    ) -> bool:
        """
        Append a new request record to the peer's request history and update the 'last seen' timestamp.
        If the peer doesn't exist, create a new peer and add the request history.
        """
        current_time = datetime.utcnow().isoformat()
        update_result = False

        peer_dict = {"ip": client_ip}
        peer_exists = await MongoDBManager().find_documents(COLLECTION, peer_dict)

        if not peer_exists:
            # If the peer doesn't exist, create a new peer and add the request history
            new_peer = Peer.Internal(
                ip=client_ip, request_history=[request_info], last_seen=current_time
            )
            await MongoDBManager().insert_document(COLLECTION, new_peer.dict())
            update_result = True
        else:
            # If the peer exists, update the request history and 'last seen' timestamp
            update_result = await MongoDBManager().update_document(
                COLLECTION,
                {"ip": client_ip},
                {
                    "$push": {"request_history": request_info.dict()},
                    "$set": {"last_seen": current_time},
                },
            )

        return bool(update_result)
