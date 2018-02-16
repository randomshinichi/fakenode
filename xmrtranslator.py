import os
import grpc
import argparse
from generated import mining_pb2, mining_pb2_grpc, qrl_pb2, qrl_pb2_grpc
from binascii import unhexlify
from flask import Flask
from jsonrpc.backend.flask import api
from grpcHelper import grpc_exception_wrapper
from qrl.core.Transaction import Transaction
from helpers import State, hexlifystr, build_blockheader_response, get_wallet_addressbundle

parser = argparse.ArgumentParser(description="Sits between node-cryptonote-pool and QRL node")
parser.add_argument("-w", "--wallet_dir", default=os.path.dirname(os.path.realpath(__file__)), help="the directory that contains pool's wallet.qrl")
parser.add_argument("-a", "--pool_address", default="", help="which address in the wallet.qrl to send payments from, otherwise it uses first address found")
parser.add_argument("--mock", action='store_true')
parser.add_argument("-n", "--node", default="127.0.0.1:9009", help="IP:Port of the QRL node's gRPC interface, default 127.0.0.1:9009")
parser.add_argument("-l", "--listen", default=18081, help="port on which the translator should listen for JSON-RPC calls from the pool, default 18081", type=int)
args = parser.parse_args()

print(vars(args))

channel = grpc.insecure_channel(args.node)
node_public_api = qrl_pb2_grpc.PublicAPIStub(channel)
node_mining_api = mining_pb2_grpc.MiningAPIStub(channel)
state = State()
pool_ab = get_wallet_addressbundle(args)

@grpc_exception_wrapper
@api.dispatcher.add_method
def getblocktemplate(wallet_address):
    if not args.mock:
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
    if not args.mock:
        # REAL
        node_req = mining_pb2.SubmitMinedBlockReq(
            blob=unhexlify(binary_blob),
            pool_address=state.pool_address,
            height=state.mining_height
        )
        node_resp = node_mining_api.SubmitMinedBlock(node_req)
    else:
        # MOCK
        node_resp = mining_pb2.SubmitMinedBlockResp()

    pool_response = {"status": "OK"}  # Let JSON-RPC library handle errors from gRPC
    return pool_response

@grpc_exception_wrapper
@api.dispatcher.add_method
def getlastblockheader():
    if not args.mock:
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
    if not args.mock:
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

@grpc_exception_wrapper
@api.dispatcher.add_method
def transfer(destinations, fee, mixin, unlock_time):
    """
    DO NOT FEED THIS FUNCTION MORE THAN 1 DESTINATION, YOUR MINERS WILL BE UNHAPPY.
    Because Monero supports TXs with multiple recipients, but QRL
    doesn't, this function will only payout to the one destination.

    :param destinations: [{"address":"Q...", "amount":1},]
    :param fee: pool hardcoded, ignored in Monero as well
    :param mixin: pool config, ignored
    :param unlock_time: pool config, ignored
    :return:
    """
    if len(destinations) > 1:
        raise Exception("Set payments.maxAddresses=1 in node-cryptonote-pool's config.json")
    dest = destinations[0]

    transferCoinsReq = qrl_pb2.TransferCoinsReq(
        address_from=pool_ab.address,
        address_to=dest["address"].encode(),
        amount=dest["amount"],
        fee=10,
        xmss_pk=pool_ab.xmss.pk(),
        xmss_ots_index=pool_ab.xmss.get_index()
    )
    transferCoinsResp = node_public_api.TransferCoins(transferCoinsReq)

    tx = Transaction.from_pbdata(transferCoinsResp.transaction_unsigned)
    tx.sign(pool_ab.xmss)

    pushTransactionReq = qrl_pb2.PushTransactionReq(transaction_signed=tx.pbdata)
    pushTransactionResp = node_public_api.PushTransaction(pushTransactionReq)

    if pushTransactionResp.some_response == 'True':
        return {"tx_hash": hexlifystr(tx.txhash)}
    else:
        raise Exception("Payout for {} didn't seem to go through".format(dest["address"]))

app = Flask(__name__)
app.add_url_rule('/json_rpc', 'api', api.as_view(), methods=['POST'])
app.run(port=args.listen, debug=True)
