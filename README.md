# translator: translates mining calls between QRL and node-cryptonote-pool
Only the transfer function is tested so far. Use `--mock` to simulate communicating with the node.

### Installation
#### Pool

```
git clone -b qrl git@github.com:randomshinichi/node-cryptonote-pool.git
npm install
apt install -y redis-server
node init.js
```

config.json
* poolServer.poolAddress can be a Qaddress
* payments.maxAddresses must be 1
* daemon 127.0.0.1:18081
* wallet 127.0.0.1:18081

#### Translator

```
git clone -b grpc git@github.com:randomshinichi/fakenode.git
pip install -r requirements.txt
python xmrtranslator.py --mock
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

* `transfer` should fail with multiple destinations
```
curl --data-binary '{"jsonrpc":"2.0","id":"0","method":"transfer","params":{"destinations":[{"amount":10000,"address":"Q00000000000000000000000000000000000000000000000000000000000000000000001"}],"fee":5000000000,"mixin":3,"unlock_time":0}}' -H 'content-type:application/json;' http://127.0.0.1:18081/json_rpc | json_pp
curl --data-binary '{"jsonrpc":"2.0","id":"0","method":"transfer","params":{"destinations":[{"amount":10000,"address":"Q00000000000000000000000000000000000000000000000000000000000000000000001"},{"amount":20000,"address":"Q00000000000000000000000000000000000000000000000000000000000000000000002"}],"fee":5000000000,"mixin":3,"unlock_time":0}}' -H 'content-type:application/json;' http://127.0.0.1:18081/json_rpc | json_pp
```

