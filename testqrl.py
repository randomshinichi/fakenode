from miniqrl import *
s = State()

print("Mining")
blob = s.getblocktemplate("Qaddr")[0]
print(s.submitblock("12345678" + blob))

print("Mining - stale block")
blob = s.getblocktemplate("Qaddr")[0]
s.add_block()
print(s.submitblock("12345678" + blob))

print("Mining - node converges on other blocks")
blob = s.getblocktemplate("Qaddr")[0]
s.add_block()
s.add_block()
print(s.submitblock("12345678" + blob))