import json
from flask import Flask
from jsonrpc.backend.flask import api
from jsonrpc.exceptions import JSONRPCDispatchException

someblockheader = {
    "block_header": {
        "depth": 0,
        "difficulty": 10,
        "hash": 'deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef',
        "height": 1,
        "nonce": 00000000,
        "num_txes": 1,
        "orphan_status": False,
        "prev_hash": '0000000000000000000000000000000000000000000000000000000000000000',
        "reward": 50,
        "timestamp": 1511404873
    },
    "status": 'OK'
}


@api.dispatcher.add_method
def getlastblockheader():
    return someblockheader


@api.dispatcher.add_method
def getblockheaderbyheight(height):
    return someblockheader


@api.dispatcher.add_method
def getblocktemplate_coreisbusy(*args, **kwargs):
    raise JSONRPCDispatchException(code=-9, message="Core is busy")


@api.dispatcher.add_method
def getblocktemplate(wallet_address):
    with open('block.json') as f:
        block = json.load(f)
        print("loaded JSON file")
    return block


@api.dispatcher.add_method
def submitblock(blob):
    print("submitblock:", blob)
    return {"status": "OK"}


app = Flask(__name__)
app.add_url_rule('/json_rpc', 'api', api.as_view(), methods=['POST'])
app.run(port=18081)
