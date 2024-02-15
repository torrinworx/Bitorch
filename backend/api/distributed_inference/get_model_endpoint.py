"""
Called when a peer on the network wants to request a model from the peer, requesting peer sends what chunk, or model id, or metadata they want to download from and the model is initiated
Critical to note here that there should be a limit calculated based on the hardware capabilities and the network bandwidth on how many downloads to facilitate, but we can worry about that
when we build out the bittorrent protocal for model distribution.

- Checksums: Provide checksums with downloadable files to enable verification of file integrity after download.
- Secure Connections: Use HTTPS to ensure the security of transfers and prevent man-in-the-middle attacks somehow.
"""
