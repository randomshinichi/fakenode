from math import floor
import os
import time
import random

from pyqrllib.pyqrllib import sha2_256, str2bin, hstr2bin, bin2hstr


class Transaction:
    def __init__(self, tx="tx"):
        self._timestamp = time.time()
        self.tx = tx

    def __repr__(self):
        return self.tx

    def __str__(self):
        return self.tx

    @property
    def hash(self):
        hashable_repr = "{}{}".format(self._timestamp, self.tx)
        return bin2hstr(sha2_256(hashable_repr.encode('utf8')))


class Blockheader:
    def __init__(self, block_number, epoch, prev_hash, tx_merkle_root=None):
        self.PK = bin2hstr(os.urandom(4))
        self.epoch = epoch
        self.block_reward = 50
        self.fee_reward = 1
        self.timestamp = int(time.time())
        self.block_number = block_number  # this is like height, except other blocks can exist with the same block_number competing for this height
        self.prev_hash = prev_hash
        self.tx_merkle_root = tx_merkle_root

        self.hash = None

    @property
    def mining_hash(self):
        data = "{0}{1}{2}{3}{4}{5}{6}{7}".format(
            self.PK,
            self.epoch,
            self.block_reward,
            self.fee_reward,
            self.timestamp,
            self.block_number,
            self.prev_hash,
            self.tx_merkle_root
        )
        return bin2hstr(bytes(sha2_256(str2bin(data))))


class BlockMetadata:
    def __init__(self, difficulty, orphan=False):
        self.orphan = orphan
        self.difficulty = difficulty


class Block:
    def __init__(self, block_number, epoch, prev_hash, transactions):
        self.blockheader = Blockheader(
            block_number,
            epoch,
            prev_hash,
            self._generate_tx_merkle_root(transactions)
        )

        self.transactions = transactions

    @staticmethod
    def _generate_tx_merkle_root(transactions):
        result = str2bin("".join(tx.hash for tx in transactions))
        return bin2hstr(sha2_256(result))

    def hash(self, nonce, preview=False):
        nonce_blob = hstr2bin(nonce + self.blockheader.mining_hash)
        blockhash = bin2hstr(bytes(sha2_256(nonce_blob)))
        if not preview:
            self.blockheader.hash = blockhash
        return blockhash


class GetBlockTemplateJob:
    def __init__(self, block=None, blockmetadata=None, blob=""):
        self.block = block
        self.blockmetadata = blockmetadata
        self.blob = blob

    def __bool__(self):
        return bool(self.block) and bool(self.blockmetadata)

    def clear(self):
        self.block = None
        self.blockmetadata = None


class State:
    def __init__(self):
        self.synced = True
        self.difficulty = 1
        self.blocks = []
        self.blockmetadata = {}
        self.txpool = {}

        self.job = GetBlockTemplateJob()

        self.did_difficulty_calculation_pass = True

        # Generate Genesis block
        genesis = Block(1, 1, None, [])
        genesis.hash(nonce="00000000")
        self.blocks.append(genesis)
        self.blockmetadata[genesis.blockheader.hash] = BlockMetadata(self.difficulty)

    @property
    def epoch(self):
        return floor(self.height / 10)

    @property
    def height(self):
        return len(self.blocks)

    def fill_txpool(self):
        for _ in range(random.randint(1, 6)):
            tx = Transaction()
            self.txpool[tx.hash] = tx

    def empty_txpool(self):
        self.txpool.clear()

    def set_difficulty(self, difficulty):
        # Difficulty only changes when a block is added to the chain.
        # Do not change difficulty without adding a block/blockmetadata(difficulty) to the node's state
        self.difficulty = difficulty

    def add_block(self):
        """
        Convenience function to quickly make the state's blockchain longer.
        """
        previous_block = self.blocks[-1]
        block = Block(previous_block.blockheader.block_number, self.epoch, previous_block.blockheader.hash, list(self.txpool.values()))
        blockmetadata = BlockMetadata(difficulty=self.difficulty)

        block.blockheader.hash = block.hash(nonce="00000000", preview=False)

        self.add_block_to_state(block, blockmetadata)

    def add_block_to_state(self, block, blockmetadata):
        """
        To add to the blockchain, you have to record the Block and its BlockMetadata.
        This function makes it atomic.
        """
        blockhash = block.blockheader.hash
        if not blockhash:
            raise Exception("Block has an empty hash! calculate the hash first")

        self.blocks.append(block)
        self.blockmetadata[blockhash] = blockmetadata

        # Remove the Block's Transactions from the Node's txpool
        for tx in block.transactions:
            self.txpool.pop(tx.hash, None)

    def getlastblockheader(self):
        header = self.blocks[-1].blockheader
        blockmetadata = self.blockmetadata[header.hash]
        answer = {
            "height": self.height,  # not sure if it should come from State or last block's BLockHeader.block_number
            "timestamp": header.timestamp,
            "hash": header.hash,
            "prev_hash": header.prev_hash,
            "block_reward": header.block_reward,
            "epoch": header.epoch,
            "PK": header.PK,
            "difficulty": blockmetadata.difficulty,
            "depth": "DUMMY",
            "orphan_status": blockmetadata.orphan
        }
        return answer

    def getblocktemplate(self, wallet_address):
        # Are we synced? If not, don't even try...
        if not self.synced:
            raise Exception("Core is busy")

        # Do we need to create a new Job?
        if self.job:
            block = self.job.block
            # Has the chain changed in the meantime?
            chain_still_the_same = block.blockheader.prev_hash == self.blocks[-1].blockheader.hash
            # is the current job too old?
            timestamp_delta = int(time.time()) - block.blockheader.timestamp
            job_still_fresh = timestamp_delta <= 10

            if (chain_still_the_same and job_still_fresh):
                return block.blockheader.mining_hash, self.job.blockmetadata.difficulty

        # Create a new Job
        prev_block = self.blocks[-1]
        coinbase = Transaction(wallet_address)
        block = Block(self.height + 1, self.epoch, prev_block.blockheader.hash, [coinbase] + list(self.txpool.values()))
        blockmetadata = BlockMetadata(self.difficulty)

        # Keep track of the Job we're sending out
        self.job.block = block
        self.job.blockmetadata = blockmetadata
        self.job.blob = block.blockheader.mining_hash

        return self.job.blob, blockmetadata.difficulty

    def submitblock(self, blob):
        # We did send out a binary blob to be hashed before, right?
        # otherwise it's just a duplicate submission
        if not self.job:
            return "Umm, I didn't send out any block to be hashed."

        # If the blob is passed in as hex, take the first 8 chars. Otherwise, take the first 4 bytes.
        nonce = blob[:8]

        # rebuild the rest of the blob from self.job, and make make sure they're the same
        if self.job.blob != blob[8:]:
            return "This is not the blob I sent you to hash."

        # put the nonce and mining_hash together. then make sure it meets the difficulty
        blockhash = self.job.block.hash(nonce, preview=True)

        if not self.did_difficulty_calculation_pass:
            return "The submitted nonce did not meet the network's difficulty"

        if self.job.block.blockheader.prev_hash != self.blocks[-1].blockheader.hash:
            return "We've moved on to other blocks since then"

        # Everything passed. Give the block its hard earned hash
        self.job.block.blockheader.hash = blockhash

        # Add the block to the chain, and its metadata to our db
        self.add_block_to_state(self.job.block, self.job.blockmetadata)

        # clear our saved Job
        self.job.clear()

        return "OK"
