curl http://127.0.0.1:18081/create_block
curl http://127.0.0.1:18081/set_node_synced


#curl --data-binary '{"jsonrpc":"2.0","id":"0","method":"getlastblockheader","params":[]}' -H 'content-type:application/json;' http://127.0.0.1:18081/json_rpc | json_pp
#curl --data-binary '{"jsonrpc":"2.0","id":"0","method":"getblocktemplate","params":{"wallet_address": "Qe4320d5125b4032c8cb637fd556c415be32e8923f787812055b707f15263e7fd78c11ba0"}}' -H 'content-type:application/json;' http://127.0.0.1:18081/json_rpc | json_pp

curl --data-binary '{"jsonrpc":"2.0","id":"0","method":"submitblock","params":["01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff1302955d0f00456c6967697573005047dc6600000"]}' -H 'content-type:application/json;' http://127.0.0.1:18081/json_rpc | json_pp