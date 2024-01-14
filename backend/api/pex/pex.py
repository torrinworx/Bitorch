import httpx
from utils.utils import Utils
from .pex_mongo import PexMongo


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
        if Utils.env == "development" and my_peer["name"] == "peer0":
            print("Yo mama's peer.")
            return  # No registration needed because we are the og source peer

        source_peers = await Utils.get_source_peers()
        await PexEndpoints.register_peers(peers=source_peers)

    # @scheduler.schedule_task(
    #     trigger="interval", seconds=5, id="peer_list_monitor"
    # )
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
        pass


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
                    print(f"Attempting to register with {peer_url}")
                    response = await client.post(
                        peer_url, json=await Utils.get_my_peer()
                    )

                    response_peer_list = PexUtils.filter_peers(response["peer_list"])

                    PexMongo.add_peers(peer_list=response_peer_list)

                    if response.status_code == 200:
                        print(f"Registered with {peer} successfully.\n")
                    else:
                        print(f"Failed to register with {peer}: {response.text}\n")
        except Exception as e:
            print(f"Error in registration process: {e}\n")

    async def update_peer_list():
        """
        Request an updated peer list from a list of peers.

        Run periodically for given peers in the peer_list who this peer
        hasn't requested an update from in a while.

        Measures should be put in place to prevent spam and block peers
        that spam this endpoint.
        """
        pass

    @staticmethod
    async def health_checks():
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
    def filter_peers():
        """
        takes in a list of peers, removes duplicated peers already found in the peer_list.

        removes peers found in the black_list.
        """
        pass
