from miniqrl import *
from flask import Flask, Response, request
from jsonrpc.backend.flask import api
from jsonrpc.exceptions import JSONRPCDispatchException


@api.dispatcher.add_method
def getlastblockheader():
    resp = s.getlastblockheader()
    return resp


@api.dispatcher.add_method
def getblocktemplate(wallet_address):
    try:
        blob, difficulty = s.getblocktemplate(wallet_address)
    except Exception:
        raise JSONRPCDispatchException(code=-9, message="Core is busy")

    resp = {
        "blocktemplate_blob": blob,
        "difficulty": difficulty
    }
    return resp


@api.dispatcher.add_method
def submitblock(binary_blob):
    msg = s.submitblock(binary_blob)

    if msg == "OK":
        return {"status": msg}
    else:
        raise Exception(msg)


s = State()

app = Flask(__name__)
app.add_url_rule('/json_rpc', 'api', api.as_view(), methods=['POST'])


@app.route('/add_block')
def add_block():
    s.add_block()
    resp = "s.blocks length: %s\n" % len(s.blocks)
    return Response(response=resp, status=200, mimetype='text/plain')


@app.route('/txpool/add')
def add_txpool():
    s.fill_txpool()
    resp = "s.txpool length: %s\n" % len(s.txpool)
    return Response(response=resp, status=200, mimetype='text/plain')


@app.route('/txpool/empty')
def empty_txpool():
    s.empty_txpool()
    resp = "s.txpool length: %s\n" % len(s.txpool)
    return Response(response=resp, status=200, mimetype='text/plain')


@app.route('/params', methods=['GET', 'POST'])
def set_params():
    def true_or_false(i):
        return True if i.lower() == 'true' else False

    if request.method == 'POST':
        if request.form.get("synced"):
            s.synced = true_or_false(request.form.get("synced"))
        if request.form.get("difficulty"):
            s.difficulty = request.form.get("difficulty")
        if request.form.get("did_difficulty_calculation_pass"):
            s.did_difficulty_calculation_pass = true_or_false(request.form.get("did_difficulty_calculation_pass"))

    resp = "s.synced = {}\ns.difficulty = {}\ns.did_difficulty_calculation_pass = {}\n".format(
        s.synced, s.difficulty, s.did_difficulty_calculation_pass)

    return Response(response=resp, status=200, mimetype='application/json')


@app.route('/ipdb')
def inspect_state():
    import ipdb
    ipdb.set_trace()
    return Response(response="done", status=200, mimetype='text/plain')


app.run(port=18081, debug=True)
