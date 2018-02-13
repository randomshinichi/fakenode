import grpc
from generated import mining_pb2, mining_pb2_grpc
from binascii import hexlify, unhexlify
from flask import Flask
from jsonrpc.backend.flask import api
from jsonrpc.exceptions import JSONRPCDispatchException

channel = grpc.insecure_channel('localhost:50051')
stub = mining_pb2_grpc.MiningAPIStub(channel)


@api.dispatcher.add_method
def getblocktemplate(wallet_address):
    # REAL
    # try:
    #     node_req = mining_pb2.GetBlockToMineReq(wallet_address=wallet_address.encode())
    #     node_resp = stub.GetBlockToMine(node_req)
    # except grpc.RpcError as e:
    #     raise Exception("{} {}".format(e.code(), e.details())

    # MOCK
    node_resp = mining_pb2.GetBlockToMineResp(blocktemplate_blob=b'deadbeef', difficulty=b'0')

    pool_response = {
        "blocktemplate_blob": hexlify(node_resp.blocktemplate_blob),
        "difficulty": hexlify(node_resp.difficulty)
    }
    return pool_response


@api.dispatcher.add_method
def submitblock(binary_blob):
    # REAL
    # try:
    #     node_req = mining_pb2.SubmitMinedBlockReq(blob=unhexlify(binary_blob))
    #     stub.SubmitMinedBlock(node_req)
    # except grpc.RpcError as e:
    #     raise Exception("{} {}".format(e.code(), e.details())

    # MOCK
    node_resp = mining_pb2.SubmitMinedBlockResp()


    pool_response = {"status": "OK"}  # Let JSON-RPC library handle errors from gRPC
    return pool_response

app = Flask(__name__)
app.add_url_rule('/json_rpc', 'api', api.as_view(), methods=['POST'])

app.run(port=18081, debug=True)
