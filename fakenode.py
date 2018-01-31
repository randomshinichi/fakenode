import os
import binascii
import random
import time
from flask import Flask, Response
from jsonrpc.backend.flask import api
from jsonrpc.exceptions import JSONRPCDispatchException


@api.dispatcher.add_method
def getlastblockheader():
    if not fake_node.blocks:
        fake_node.create_block()

    return fake_node.blocks[-1].__dict__


@api.dispatcher.add_method
def getblocktemplate(wallet_address):
    if not fake_node.synced:
        raise JSONRPCDispatchException(code=-9, message="Core is busy")

    block = fake_node.blocks[-1]
    result = {
        "blocktemplate_blob": '00000000' + block.raw_block_merkle_root,
        "difficulty": fake_node.difficulty,
        "status": "OK"
    }

    return result


@api.dispatcher.add_method
def submitblock(raw_block_merkle_root_w_nonce):
    if fake_node.accept_submitted_blocks:
        return {"status": "OK"}
    else:
        return {"status": "Network accepted another block already"}


class FakeBlock:
    def __init__(self, height, epoch):
        self.height = height
        self.timestamp = int(time.time())
        self.hash = binascii.hexlify(os.urandom(5)).decode()
        self.prev_hash = binascii.hexlify(os.urandom(5)).decode()
        self.block_reward = random.randint(100000, 200000)

        self.epoch = epoch
        self.PK = binascii.hexlify(os.urandom(4)).decode()

        self.raw_block_merkle_root = binascii.hexlify(os.urandom(15)).decode()
        self.raw_block_all_txs = binascii.hexlify(os.urandom(25)).decode()

    @property
    def mining_nonce(self):
        return self.raw[:4]


class NodeState:
    def __init__(self):
        self.height = 0
        self.epoch = 1
        self.blocks = []

        self.synced = False
        self.accept_submitted_blocks = True
        self.difficulty = random.randint(0, 1000)

    def _increment_height(self):
        self.height += 1
        if self.height % 10 == 0:
            self.epoch += 1

    def create_block(self):
        b = FakeBlock(self.height, self.epoch)
        self._increment_height()
        self.blocks.append(b)
        self.difficulty = random.randint(0, 1000)


fake_node = NodeState()

app = Flask(__name__)
app.add_url_rule('/json_rpc', 'api', api.as_view(), methods=['POST'])


@app.route('/create_block')
def create_block():
    fake_node.create_block()
    resp = "fake_node.blocks length: %s\n" % len(fake_node.blocks)
    return Response(response=resp, status=200, mimetype='text/plain')


@app.route('/synced')
def set_fake_node_synced():
    fake_node.synced = True
    resp = "fake_node.synced: %s\n" % fake_node.synced
    return Response(response=resp, status=200, mimetype='text/plain')


@app.route('/unsynced')
def set_fake_node_unsynced():
    fake_node.synced = False
    resp = "fake_node.synced: %s\n" % fake_node.synced
    return Response(response=resp, status=200, mimetype='text/plain')


@app.route('/accept_submitted_blocks')
def set_node_accept_submitted_blocks():
    fake_node.accept_submitted_blocks = True
    resp = "fake_node.accept_submitted_blocks: %s\n" % fake_node.accept_submitted_blocks
    return Response(response=resp, status=200, mimetype='text/plain')


@app.route('/reject_submitted_blocks')
def set_node_reject_submitted_blocks():
    fake_node.accept_submitted_blocks = False
    resp = "fake_node.accept_submitted_blocks: %s\n" % fake_node.accept_submitted_blocks
    return Response(response=resp, status=200, mimetype='text/plain')


@app.route('/inspect_state')
def inspect_state():
    import ipdb
    ipdb.set_trace()
    return Response(response="done", status=200, mimetype='text/plain')


@app.route('/reset_state')
def reset_state():
    fake_node.blocks = []
    return Response(response="done", status=200, mimetype='text/plain')


app.run(port=18081, debug=True)
