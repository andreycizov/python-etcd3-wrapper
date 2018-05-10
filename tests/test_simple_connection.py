import os
import unittest
from urllib.parse import urlparse

from etcd3wrapper.helpers import create_channel
from etcd3wrapper.rpc import KV, PutRequest, RangeRequest, DeleteRangeRequest, CompactionRequest, TxnRequest, Compare, \
    RequestOp


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

    def test_delete_key(self):
        ch = from_url(os.environ['TEST_ETCD_URL'])
