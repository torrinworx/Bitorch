# # Controls when nodes get rate limited or blacklisted

# # TODO: Finish/work out the full implmentation to track needed metric in the Peer
# # class/mongodb and use here.

# import time

# from fastapi import Request, HTTPException
# from starlette.middleware.base import BaseHTTPMiddleware


# class RateLimiterMiddleware(BaseHTTPMiddleware):
#     def __init__(
#         self, app, max_requests_per_minute=60, blacklist_threshold=5
#     ):  # TODO: Set these as env vars
#         self.app = app
#         self.max_requests_per_minute = max_requests_per_minute
#         self.blacklist_threshold = blacklist_threshold
#         self.peer_last_request = {}  # TODO: get from mongodb
#         self.peer_request_count = {}  # TODO: get from mongodb
#         self.peer_request_list = (
#             {}
#         )  # TODO: create a request_record dict for each Peer and store in mongodb with timestamps

#     async def __call__(self, request: Request):
#         peer_ip = request.client.host

#         # Check if the peer is blacklisted, and if so, reject the request
#         if self.is_blacklisted(peer_ip):
#             raise HTTPException(status_code=403, detail="Peer is blacklisted.")

#         # Check rate limit for the peer
#         if not self.is_rate_limited(peer_ip):
#             # Update request count and last request timestamp
#             self.update_request_info(peer_ip)
#             return await self.app(request)
#         else:
#             raise HTTPException(status_code=429, detail="Rate limit exceeded.")

#     def is_blacklisted(self, peer_ip):
#         # Implement logic to check if the peer is blacklisted
#         # Use MongoDB database to check if the peer is blacklisted
#         # Return True if blacklisted, otherwise False
#         return False

#     def is_rate_limited(self, peer_ip):
#         # Implement rate limiting logic here
#         current_time = time.time()
#         if peer_ip in self.peer_last_request:
#             last_request_time = self.peer_last_request[peer_ip]
#             request_count = self.peer_request_count.get(peer_ip, 0)

#             # If the peer has exceeded the rate limit, return True
#             if request_count >= self.max_requests_per_minute:
#                 return True

#             # If the peer has made too many requests in a short time, blacklist it
#             if (current_time - last_request_time) < 60:
#                 self.update_request_info(peer_ip)
#                 request_count += 1
#                 if request_count >= self.blacklist_threshold:
#                     self.blacklist_peer(peer_ip)
#                 return False

#         # If the peer is not rate limited, return False
#         return False

#     def update_request_info(self, peer_ip):
#         current_time = time.time()
#         self.peer_last_request[peer_ip] = current_time
#         if peer_ip in self.peer_request_count:
#             self.peer_request_count[peer_ip] += 1
#         else:
#             self.peer_request_count[peer_ip] = 1

#     def blacklist_peer(self, peer_ip):
#         # Implement logic to blacklist the peer (TODO: add blacklist tag/bool to MongoDB/Peer class model)
#         pass
