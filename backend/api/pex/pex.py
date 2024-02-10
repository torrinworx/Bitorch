import os
import traceback
from typing import List, Tuple

import httpx

from utils.utils import Utils, Peer
from .pex_mongo import PexMongo
from utils.scheduler import scheduler

class PexTasks:
    @staticmethod
    async def startup():
        """
        Initialize startup tasks for the peer-to-peer network.

        This function is responsible for establishing initial peer connections.
        It checks if the current peer list is empty and, if so, searches for
        additional peers to connect to for starting network activities.
        """
        await PexTasks.join_network()

        # Add self to peer list:
        my_peer = await Utils.get_my_peer()
        await PexMongo.add_peer(peer=my_peer)

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
            return  # No registration needed because we are the source peer

        peers = Utils.get_source_peers()
        await PexEndpoints.register_peers(peers=peers)

    @scheduler.schedule_task(
        trigger="interval", seconds=10, id="peer_list_monitor"
    )
    @staticmethod
    async def peer_list_monitor():
        """
        Monitors and maintains the active peers in peer list and the last_seen time.

        my_peer_list = get_peer_list_from_mongo

        for peer in peer_list:
            keep track of and detect the last time a peer in the peer_list has been requested
            update_peer_list from. through lastSeen

            last_seen = peer.last_seen

            if 5 minutes < last_seen < 10 minutes, send an update_peer_list() request.
                response = await PexEndpoints.update_peer_list(peers)

                response_peer_list = response.peer_list

                response_peer_list = filter and remove duplicate or black-listed/blocked peers

                PexEndpoints.register_peers(response_peer_list)

            if greater than 10 minutes sends a health_check() request.
                if health_check fails, remove from peer_list and mark as "dead".

        lastSeen for each peer in peer_list should be updated whenever
        contacted or successful request returned by a peer in all endpoints.

        TODO: Create universal utils.update_last_seen(peer) function that
        updates the last time a peer was seen in the network.
        """
        from datetime import datetime, timedelta
        my_peer_list = await PexMongo.get_all_peers()
        current_time = datetime.now()
        five_minutes_ago = current_time - timedelta(seconds=1)
        ten_minutes_ago = current_time - timedelta(seconds=2)
        for peer in my_peer_list:
            peer_last_seen = datetime.fromisoformat(peer.last_seen)
            if ten_minutes_ago > peer_last_seen:
                # Health check
                alive = await PexEndpoints.health_check(peer)
                if not alive:
                    # TODO: handle marking the peer as dead in the database, shouldn't delete it, but just mark it dead and filter it out.
                    pass 

            elif five_minutes_ago < peer_last_seen < ten_minutes_ago:
                await PexEndpoints.register_peers([peer])

class PexEndpoints:
    @staticmethod
    async def register_peers(peers: List[Peer.Internal]):
        """
        Request registration from a list of peers in the network. Adds current peer to their
        peer_list and receives a truncated peer_list from them.

        This method attempts to register the current peer with each peer in the `peers` list
        by sending a POST request.

        Parameters:
        - peers (List[Peer.Internal]): A list of Peer.Internal instances representing the peers.

        Returns:
        - None
        """
        # Retrieve the current recursion depth and the limit flag
        depth, limit_reached = await PexUtils.get_depth()

        if limit_reached:
            print(f"Recursion depth limit reached, currently at depth {depth}. Stopping further registrations.")
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
                    filtered_new_peers = await PexUtils.filter_peers_registered(new_peer_list)

                    # Add peers to db
                    await PexMongo.add_peers(filtered_new_peers)

                    # Make a recursive call to continue the registration process
                    if not limit_reached:
                        await PexEndpoints.register_peers(filtered_new_peers)

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
    @staticmethod
    async def filter_peers_registered(peer_list: List[Peer.Internal]) -> List[Peer.Internal]:
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

        TODO:
        - Implement filtering based on a blacklist of peers.
        - Integrate with rate limiter and blacklist systems in Utils.Peer/PexMongo.

        Note:
        - This function assumes that each peer has a unique IP address for identification purposes.
        - The implementation of blacklist filtering is pending. The current version does not filter
        out blacklisted peers.
        """
        my_peer_list = await PexMongo.get_all_peers()

        # Create a set of IPs from my_peer_list for quick lookup
        known_ips = {peer.ip for peer in my_peer_list}

        # Filter out any peers that are already in my_peer_list
        return [peer for peer in peer_list if peer.ip not in known_ips]

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
