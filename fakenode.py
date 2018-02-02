from .miniqrl import *
from flask import Flask, Response
from jsonrpc.backend.flask import api
from jsonrpc.exceptions import JSONRPCDispatchException


@api.dispatcher.add_method
def getlastblockheader():
    pass


@api.dispatcher.add_method
def getblocktemplate(wallet_address):
    pass


@api.dispatcher.add_method
def submitblock(raw_block_merkle_root_w_nonce):
    pass


fake_node = State()

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
