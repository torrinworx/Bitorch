import json
import traceback
from typing import List

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

        await PexEndpoints.register_peers(peers=Utils.get_source_peers())

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
        five_minutes_ago = current_time - timedelta(minutes=5)
        ten_minutes_ago = current_time - timedelta(minutes=10)
        for peer in my_peer_list:
            peer_last_seen = datetime.fromisoformat(peer.last_seen)
            if ten_minutes_ago > peer_last_seen:
                # Health check
                alive = await PexEndpoints.health_check(peer)
                if not alive:
                    # Mark the peer as dead in the database
                    # ... Update code to handle marking the peer as dead
                    pass 

            elif five_minutes_ago < peer_last_seen < ten_minutes_ago:
                # # Update peer list
                # response = await PexEndpoints.update_peer_list(my_peer_list)
                # response_peer_list = response.peer_list
                # # Filter out duplicates and blacklisted peers
                # filtered_peer_list = PexUtils.filter_peers(response_peer_list)
                # await PexEndpoints.register_peers(filtered_peer_list)
                pass

            # TODO: Implement the utils.update_last_seen(peer) function

class PexEndpoints:
    @staticmethod
    async def register_peers(peers: list):
        """
        Request registration from a list of peers in the network. Adds current peer to their
        peer_list and receives peer_list truncated from them.

        This method corresponds to the /backend/api/pex/register.py endpoint.
        It attempts to register the current peer with each source peer in the `peers` list
        by sending a POST request to each.

        TODO: Design this as a simple two birds with one stone endpoint;
        register with a peer, peer returns random selection of peer_list capped at some value.

        Parameters:
        peers (list): A list of dicitonaries, each containing information about a peer.
        """
        try:
            async with httpx.AsyncClient() as client:
                for peer in peers:
                    peer_url = f"http://{peer['ip']}:{peer['port']}/register"
                    my_peer = await Utils.get_my_peer()

                    print(f"Attempting to register with {peer_url}")
                    response = await client.post(
                        url=peer_url,
                        json=my_peer.dict(),
                    )

                    # Convert bytes to string and then to a dictionary
                    response_data = json.loads(response.content.decode("utf-8"))
                    print(response_data)

                    # TODO: Maybe run some kind of loop to register peers before
                    # adding them to the database? Infinite loop might happen here
                    # without some kind of hard limit if the network becomes huge.
                    # TODO: Run filter on received peer list before adding to peer list

                    # Convert each dict in response_peer_list to an instance of Utils.Peer
                    response_peer_list = [
                        Peer.Internal(**peer)
                        for peer in response_data["content"]["peer_list"]
                    ]

                    # Filter Peers
                    response_peer_list = PexUtils.filter_peers(
                        peer_list=response_peer_list
                    )

                    # Add Peers to network
                    await PexMongo.add_peers(peer_list=response_peer_list)

                    if response.status_code == 200:
                        print(f"Registered with {peer} successfully.\n")
                    else:
                        print(f"Failed to register with {peer}: {response.text}\n")

        except Exception as e:
            print(traceback.format_exc())
            print(f"Error in registration process: {e}\n")

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
    # TODO:
    @staticmethod
    def filter_peers(peer_list: List[Peer.Internal]):
        """
        takes in a list of peers, removes duplicated peers already found in the peer_list.

        removes peers found in the black_list.

        hinges on building out the rate_limitor and the blacklist system in Utils.Peer/PexMongo stuff.
        """
        return peer_list
