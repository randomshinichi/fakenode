import json
from flask import Flask
from jsonrpc.backend.flask import api
from jsonrpc.exceptions import JSONRPCDispatchException


app = Flask(__name__)
app.add_url_rule('/json_rpc', 'api', api.as_view(), methods=['POST'])


@api.dispatcher.add_method
def getlastblockheader(*args, **kwargs):
    lastblockheader = {
        "block_header": {
            "block_size": 251735,
            "depth": 0,
            "difficulty": 10,  # 34407423123
            "hash": '967a4b987cfd73a3707a0347664307700e7c989aa644ba380e3b44d980c6e47a',
            "height": 1,  # 1448983
            "major_version": 6,
            "minor_version": 6,
            "nonce": 25167459,
            "num_txes": 19,
            "orphan_status": False,
            "prev_hash": '68271d9edc7cc560dbb2adbc00f9dbe2ae67a630cc7146556a0c736d0316312c',
            "reward": 6556365000456,
            "timestamp": 1511404873
        },
        "status": 'OK'
    }
    return lastblockheader


@api.dispatcher.add_method
def getblocktemplate_coreisbusy(*args, **kwargs):
    raise JSONRPCDispatchException(code=-9, message="Core is busy")


@api.dispatcher.add_method
def getblocktemplate(*args, **kwargs):
    with open('block.json') as f:
        block = json.load(f)
        print("loaded JSON file")
    return block


@api.dispatcher.add_method
def submitblock(*args, **kwargs):
    return {"status": "OK"}
