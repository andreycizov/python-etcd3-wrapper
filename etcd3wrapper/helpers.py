from urllib.parse import urlparse, ParseResult

import grpc


def create_channel(hostname, port, ca=None, key=None, cert=None):
    r = _create_tcp_channel(hostname, port)

    if ca:
        r = _wrap_tls_channel(r, ca, key, cert)

    return r


def _create_tcp_channel(hostname, port):
    channel = grpc.insecure_channel(f'{hostname}:{port}')
    return channel


def _wrap_tls_channel(chan, ca, key=None, cert=None):
    if isinstance(ca, str):
        with open(ca, 'rb') as f_in:
            ca = f_in.read()

    if key and isinstance(key, str):
        with open(key, 'rb') as f_in:
            key = f_in.read()

    if cert and isinstance(cert, str):
        with open(cert, 'rb') as f_in:
            cert = f_in.read()

    return grpc.secure_channel(
        chan,
        grpc.ssl_channel_credentials(
            ca,
            key,
            cert
        )
    )
