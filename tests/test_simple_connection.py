import os
import unittest

from etcd3wrapper.helpers import create_channel
from etcd3wrapper.rpc import KV, PutRequest, RangeRequest


class TestSimpleConnection(unittest.TestCase):
    def test_create_key(self):
        ch = create_channel(os.environ['TEST_ETCD_URL'])

        service = KV(ch)

        KEY = b'123'
        VAL = b'321'

        x = service.Put(PutRequest(KEY, value=VAL))

        self.assertEqual(x.prev_kv.version, 0)

        resp = service.Range(RangeRequest(key=KEY, range_end=KEY + b'\x00'))
        self.assertEqual(resp.count, 1)

        kv = resp.kvs[0]

        self.assertEqual(kv.value, VAL)
        self.assertEqual(kv.key, KEY)
        self.assertEqual(kv.version, 1)
