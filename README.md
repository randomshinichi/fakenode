# miniQRL: a mock QRL node that lets you play with stuff
miniqrl.State is the fake node, and fakenode.py is just the Flask JSON-RPC wrapper around it.

```
pip install -r requirements.txt
python3 fakenode.py
 * Running on http://127.0.0.1:18081/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
```

### JSON-RPC methods:
* `getlastblockheader` no params required
```
curl --data-binary '{"jsonrpc":"2.0","id":"0","method":"getlastblockheader","params":[]}' -H 'content-type:application/json;' http://127.0.0.1:18081/json_rpc | json_pp
```

* `getblocktemplate` pass in the Qaddress that the block's reward should go to
```
curl --data-binary '{"jsonrpc":"2.0","id":"0","method":"getblocktemplate","params":{"wallet_address": "Qe4320d5125b4032c8cb637fd556c415be32e8923f787812055b707f15263e7fd78c11ba0"}}' -H 'content-type:application/json;' http://127.0.0.1:18081/json_rpc | json_pp
```

* `submitblock` pass in a hexstring encoded binary blob with the nonce being the first 8 characters in the string.
```
curl --data-binary '{"jsonrpc":"2.0","id":"0","method":"submitblock","params":["0564fda5badebe92a966665276f026838ec3ca19bf16262d4a14bb63ff7f7f19"]}' -H 'content-type:application/json;' http://127.0.0.1:18081/json_rpc | json_pp
```

### HTTP methods (for debugging/control):
```
GET /add_block
s.blocks length: 6

GET /txpool/add (adds a random number of txs to the pool)
s.txpool length: 8

GET /txpool/empty
s.txpool length: 0

GET/POST /params
curl http://127.0.0.1:18081/params -X POST -d 'difficulty=10&synced=true&did_difficulty_calculation_pass=true'
s.synced = True
s.difficulty = 10
s.did_difficulty_calculation_pass = True
You do not have to pass all the params.

GET /ipdb
```