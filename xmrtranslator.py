import grpc
from generated import mining_pb2, mining_pb2_grpc, qrl_pb2, qrl_pb2_grpc
from binascii import hexlify, unhexlify
from flask import Flask
from jsonrpc.backend.flask import api
from grpcHelper import grpc_exception_wrapper
from helpers import State, hexlifystr, build_blockheader_response

channel = grpc.insecure_channel('localhost:50051')
node_public_api = qrl_pb2_grpc.PublicAPIStub(channel)
node_mining_api = mining_pb2_grpc.MiningAPIStub(channel)
mock = True
state = State()

@grpc_exception_wrapper
@api.dispatcher.add_method
def getblocktemplate(wallet_address):
    if not mock:
        # REAL
        node_req = mining_pb2.GetBlockToMineReq(wallet_address=wallet_address.encode())
        node_resp = node_mining_api.GetBlockToMine(node_req)
    else:
        # MOCK
        node_resp = mining_pb2.GetBlockToMineResp(blocktemplate_blob=unhexlify('00000000'), difficulty=unhexlify('a0'))

    pool_response = {
        "blocktemplate_blob": hexlifystr(node_resp.blocktemplate_blob),
        "difficulty": hexlifystr(node_resp.difficulty),
        "status": "OK"
    }
    return pool_response


@grpc_exception_wrapper
@api.dispatcher.add_method
def submitblock(binary_blob):
    if not mock:
        # REAL
        node_req = mining_pb2.SubmitMinedBlockReq(blob=unhexlify(binary_blob))
        node_resp = node_mining_api.SubmitMinedBlock(node_req)
    else:
        # MOCK
        node_resp = mining_pb2.SubmitMinedBlockResp()

    pool_response = {"status": "OK"}  # Let JSON-RPC library handle errors from gRPC
    return pool_response

@grpc_exception_wrapper
@api.dispatcher.add_method
def getlastblockheader():
    if not mock:
        # REAL
        node_info = node_public_api.GetNodeState(qrl_pb2.GetNodeStateReq())
        node_req = mining_pb2.GetBlockMiningCompatibleReq()
        node_resp = node_mining_api.GetBlockMiningCompatible(node_req)
    else:
        # MOCK
        node_info = qrl_pb2.GetNodeStateResp(info=qrl_pb2.NodeInfo(block_height=12))
        header = qrl_pb2.BlockHeader(
            block_number = 10,
            epoch = 1,
            hash_header = unhexlify('10101010'),
            hash_header_prev = unhexlify('09090909'),
            merkle_root = unhexlify('deadbeef'),
            mining_nonce = 539,
            reward_block = 50,
            reward_fee = 1,
            timestamp = qrl_pb2.Timestamp(seconds=1305712800, nanos=100),
            PK = unhexlify('deadbeefdeadbeefdeadbeef')
        )
        metadata = qrl_pb2.BlockMetaData(
            is_orphan = False,
            block_difficulty = unhexlify('10'),
            cumulative_difficulty = unhexlify('1100')
        )
        node_resp = mining_pb2.GetBlockMiningCompatibleResp(
            blockheader=header,
            blockmetadata = metadata
        )

    pool_response = build_blockheader_response(node_info, node_resp)
    return pool_response

@grpc_exception_wrapper
@api.dispatcher.add_method
def getblockheaderbyheight(height):
    if not mock:
        # REAL
        node_info = node_public_api.GetNodeState(qrl_pb2.GetNodeStateReq())
        node_req = mining_pb2.GetBlockMiningCompatibleReq(height=height)
        node_resp = node_mining_api.GetBlockMiningCompatible(node_req)
    else:
        # MOCK
        node_info = qrl_pb2.GetNodeStateResp(info=qrl_pb2.NodeInfo(block_height=12))
        header = qrl_pb2.BlockHeader(
            block_number = 10,
            epoch = 1,
            hash_header = unhexlify('10101010'),
            hash_header_prev = unhexlify('09090909'),
            merkle_root = unhexlify('deadbeef'),
            mining_nonce = 539,
            reward_block = 50,
            reward_fee = 1,
            timestamp = qrl_pb2.Timestamp(seconds=1305712800, nanos=100),
            PK = unhexlify('deadbeefdeadbeefdeadbeef')
        )
        metadata = qrl_pb2.BlockMetaData(
            is_orphan = False,
            block_difficulty = unhexlify('10'),
            cumulative_difficulty = unhexlify('1100')
        )
        node_resp = mining_pb2.GetBlockMiningCompatibleResp(
            blockheader=header,
            blockmetadata = metadata
        )

    pool_response = build_blockheader_response(node_info, node_resp)
    return pool_response


app = Flask(__name__)
app.add_url_rule('/json_rpc', 'api', api.as_view(), methods=['POST'])

app.run(port=18081, debug=True)
