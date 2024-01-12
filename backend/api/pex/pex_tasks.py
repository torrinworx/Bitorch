import httpx
from utils.utils import Utils


class PexTasks:
    @staticmethod
    async def startup_tasks():
        # TODO: Peer connection function, check if peers list is empty
        # then search for more peers to connect to to start things off.
        pass

    @staticmethod
    async def join_network():
        # Joins the network by attempting to join source nodes from .config.json, this function is only needed to be run once for a given node's initial deployment, unless all nodes are unresponsive
        # then either no network connection to the internet, or all source nodes are down.
        source_nodes = (
            Utils.config["development"]
            if Utils.env == "development"
            else Utils.config["production"]
        )

        # Try to register with each source node from .config.json
        for node, node_dict in source_nodes.items():
            url = f"http://{node['ip']}:{node['port']}/register"

            if Utils.env == "development" and Utils.get_my_node()["name"] == "node0":
                """
                Only for development testing:
                Each node, even the source nodes, should act like and be deployed like any node.

                Their behavior is the same. The only difference is that their ip addresses are listed
                in the .config.json file and are from trusted community partners.
                """
                print("Yo mama's node.")
                return  # No registration needed because we are the og source node

            PexEndpoints.register(url=url, node=node_dict)


class PexEndpoints:
    @staticmethod
    async def register(url: str, node: dict):
        """
        Corisponds to the /backend/api/pex/register.py endpoint.
        """
        try:
            async with httpx.AsyncClient() as client:
                print(f"Attempting to register with {url}")
                response = await client.post(url, json=await Utils.get_my_node())

                if response.status_code == 200:
                    print(f"Registered with {node} successfully.\n")
                else:
                    print(f"Failed to register with {node}: {response.text}\n")
        except Exception as e:
            print(f"Error registering with {node}: {e}\n")

    @staticmethod
    async def update_peer_list():
        # Implement the logic to update the peer list
        pass

    @staticmethod
    async def send_health_checks():
        print("Scheduled health check function ran")
        return False
        # Implement the logic to send health checks
