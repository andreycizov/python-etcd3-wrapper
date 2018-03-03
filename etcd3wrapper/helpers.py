from urllib.parse import urlparse

import grpc


def create_channel(url):
    x = urlparse(url)
    channel = grpc.insecure_channel(f'{x.hostname}:{x.port}')

    return channel