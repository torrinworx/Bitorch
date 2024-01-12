import httpx
from utils.utils import Utils


class PexTasks:
    @staticmethod
    async def startup_check():
        # TODO: Peer connection function, check if peers list is empty
        # then search for more peers to connect to to start things off.
        pass

    def get_my_node_info():
        # TODO: Create function to get the current nodes node_info to send to other nodes
        pass

    @staticmethod
    async def request_register():
        source_nodes = Utils.load_config()
        current_node_address = await Utils.get_ip_address()

        print(source_nodes)
        # Print the nodes we're attempting to connect to
        print("Attempting to connect to the following nodes:")
        for node, node_info in source_nodes.items():
            print(f"Node: {node}, Info: {node_info}")

        # Try to register with each source node
        for node, node_info in source_nodes.items():
            # Construct the URL from the node info
            ip = node_info.get("ip")
            port = node_info.get("port")
            url = f"http://{ip}:{port}/register"

            node_info = {
                "ip": current_node_address,
                "port": 8000,
                "name": "yo mama's",
            }

            if current_node_address == "node0":
                print("Yo mama's node.")
                return True  # No registration needed because we are the og source node

            try:
                async with httpx.AsyncClient() as client:
                    print(f"Attempting to register with {url}")
                    response = await client.post(url, json=node_info)

                    if response.status_code == 200:
                        print(f"Registered with {node} successfully.\n")
                        return True
                    else:
                        print(f"Failed to register with {node}: {response.text}\n")
                        return True
            except Exception as e:
                print(f"Error registering with {node}: {e}\n")

        return True

    @staticmethod
    async def update_peer_list():
        # Implement the logic to update the peer list
        pass

    @staticmethod
    async def send_health_checks():
        print("Scheduled health check function ran")
        return False
        # Implement the logic to send health checks
