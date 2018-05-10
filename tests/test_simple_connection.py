import os
import unittest
from urllib.parse import urlparse

from etcd3wrapper.helpers import create_channel
from etcd3wrapper.kv import Event
from etcd3wrapper.rpc import KV, PutRequest, RangeRequest, DeleteRangeRequest, CompactionRequest, TxnRequest, Compare, \
    RequestOp, Watch, WatchRequest, WatchCreateRequest


def from_url(url):
    x = urlparse(url)
    return create_channel(x.hostname, x.port)


class TestSimpleConnection(unittest.TestCase):
    def test_create_key(self):
        ch = from_url(os.environ['TEST_ETCD_URL'])

        service = KV(ch)

        KEY = b'123'
        VAL = b'321'
        VAL2 = b'3210'

        x = service.Put(PutRequest(KEY, value=VAL))

        self.assertEqual(x.prev_kv.version, 0)

        resp = service.Range(RangeRequest(key=KEY, range_end=KEY + b'\x00'))
        self.assertEqual(resp.count, 1)

        kv = resp.kvs[0]

        self.assertEqual(kv.value, VAL)
        self.assertEqual(kv.key, KEY)
        self.assertEqual(kv.version, 1)

        resp = service.DeleteRange(DeleteRangeRequest(key=KEY, range_end=KEY + b'\x00'))
        self.assertEqual(resp.deleted, 1)

        resp = service.Compact(CompactionRequest(0))

        resp = service.Txn(TxnRequest(
            compare=[
                Compare(key=KEY, result=Compare.CompareResult.EQUAL, target=Compare.CompareTarget.VERSION, version=0)
            ],
            success=[
                RequestOp(request_put=PutRequest(KEY, value=VAL2)),
            ]
        )
        )

        self.assertEqual(resp.succeeded, True)

    def test_watch_key(self):
        ch = from_url(os.environ['TEST_ETCD_URL'])
        ch2 = from_url(os.environ['TEST_ETCD_URL'])

        watch = Watch(ch)
        kv = KV(ch2)

        PRE = b'123'
        N = 16
        VAL_FN = lambda x: str(x).encode()

        wr = WatchCreateRequest(key=PRE, range_end=PRE[:-1] + bytes([PRE[-1] + 1]))

        responses = watch.Watch(iter([WatchRequest(
            create_request=wr
        )]))

        for i in range(N):
            kv.Put(PutRequest(PRE + VAL_FN(i), value=VAL_FN(i)))

        events_parsed = {}

        stop = False

        for response in responses:
            for ev in response.events:
                self.assertEqual(ev.type, Event.EventType.PUT)
                key = ev.kv.key

                expected_val = int(key[len(PRE):].decode())

                self.assertEqual(ev.kv.value, VAL_FN(expected_val))

                events_parsed[key] = True

                if len(events_parsed) == N:
                    stop = True
                    break
            if stop:
                break
