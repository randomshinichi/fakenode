from binascii import hexlify, unhexlify

class State:
    def __init__(self):
        self.pool_address = None
        self.mining_height = None

def hexlifystr(data):
    return hexlify(data).decode()

def build_blockheader_response(node_info, node_resp):
    pool_response = {
        "height": node_resp.blockheader.block_number,
        "timestamp": node_resp.blockheader.timestamp.seconds,
        "hash": hexlifystr(node_resp.blockheader.hash_header),
        "prev_hash": hexlifystr(node_resp.blockheader.hash_header_prev),
        "block_reward": node_resp.blockheader.reward_block,
        "epoch": node_resp.blockheader.epoch,
        "PK": hexlifystr(node_resp.blockheader.PK),
        "mining_nonce": node_resp.blockheader.mining_nonce,
        "difficulty": hexlifystr(node_resp.blockmetadata.cumulative_difficulty),
        "depth": node_info.info.block_height - node_resp.blockheader.block_number,
        "orphan_status": node_resp.blockmetadata.is_orphan,
        "status": "OK"
    }
    return pool_response