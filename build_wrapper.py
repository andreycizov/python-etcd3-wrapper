import os
import shutil

from protobuf_gen.patch import ServiceMethodPatch
from protobuf_gen.remap import remap
from protobuf_gen.transpiler import InputModule
from protobuf_gen.wrap import wrap

GIT_REQS = [
    ('etcd/etcd', 'https://github.com/coreos/etcd.git'),
    ('grpc-gateway', 'https://github.com/grpc-ecosystem/grpc-gateway.git'),
    ('protobuf', 'https://github.com/gogo/protobuf.git'),
]


def main(fl=os.path.dirname(__file__)):
    mod = 'etcd3wrapper'

    for fldr, git_req in GIT_REQS:
        fldr_abs = os.path.join(fl, 'pb_includes', fldr)
        if not os.path.exists(fldr_abs):
            try:
                os.subprocess.Popen([
                    'git',
                    'clone',
                    git_req,
                    fldr_abs
                ])
            except:
                shutil.rmtree(fldr_abs)
                raise

    autogen = '_autogen'

    INCLUDES = [
        os.path.join(fl, 'pb_includes/etcd'),
        os.path.join(fl, 'pb_includes/grpc-gateway/third_party/googleapis/'),
        os.path.join(fl, 'pb_includes/protobuf'),
    ]

    rpc_proto = 'etcd/etcdserver/etcdserverpb/rpc.proto'
    kv_proto = 'etcd/mvcc/mvccpb/kv.proto'
    auth_proto = 'etcd/auth/authpb/auth.proto'

    INPUT = [
        rpc_proto,
        kv_proto,
        auth_proto,
        'google/api/annotations.proto',
        'gogoproto/gogo.proto',
        'google/api/http.proto',
    ]

    remap(
        os.path.join(fl, mod, autogen),
        mod + '.' + autogen,
        INCLUDES,
        INPUT
    )

    rpc_patch = [
        ServiceMethodPatch('Watch', 'Watch', True, True),
        ServiceMethodPatch('Lease', 'LeaseKeepAlive', True, True),
        ServiceMethodPatch('Maintenance', 'Snapshot', False, True),
    ]

    wrap(
        output_dir_wrappers=os.path.join(fl, mod),
        root_module=mod,
        root_autogen=mod + '.' + autogen,
        includes=INCLUDES,
        input_proto=INPUT,
        output_files={
            'rpc.py': InputModule('rpc', rpc_proto, rpc_patch),
            'kv.py': InputModule('kv', kv_proto),
            'auth.py': InputModule('auth', auth_proto),
        }
    )


if __name__ == '__main__':
    main()
