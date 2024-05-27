import os
import json
import hashlib
import time

DIFFICULTY_TARGET = "0000ffff00000000000000000000000000000000000000000000000000000000"
PREV_BLOCK_HASH = "0000000000000000000000000000000000000000000000000000000000000000"
BLOCK_REWARD = 50 * 10**8  # 50 BTC in satoshis
VERSION = 1

def sha256(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data.encode('utf-8')).digest()).hexdigest()

def validate_transaction(tx):
    try:
        input_total = sum([inp['prevout']['value'] for inp in tx['vin']])
        output_total = sum([out['value'] for out in tx['vout']])
        return input_total >= output_total and 'txid' in tx and tx['txid']
    except KeyError as e:
        print(f"Transaction validation error: missing key {e}")
        return False

def serialize_transaction(tx):
    return json.dumps(tx, sort_keys=True)

def create_coinbase_transaction():
    coinbase_tx = {
        "txid": "",
        "vin": [{
            "coinbase": "04ffff001d0104455468652054696d65732030332f4a616e2f32303233204368616e63656c6c6f72206f6e20626974636f696e2062756c6c",
            "sequence": 4294967295
        }],
        "vout": [{
            "value": BLOCK_REWARD,
            "scriptPubKey": "4104678afdb0fe5548271967f1a67130b7105cd6a828e03909a67962e0ea1f61deb649f6bc3f4cef38c4f35504e51ec112de5c384df7ba0b8d578a4c702b6bf11d5fac"
        }]
    }
    coinbase_tx["txid"] = double_sha256(serialize_transaction(coinbase_tx))
    return coinbase_tx

def calculate_merkle_root(txids):
    if len(txids) == 1:
        return txids[0]
    new_txids = []
    for i in range(0, len(txids) - 1, 2):
        new_txid = double_sha256(txids[i] + txids[i+1])
        new_txids.append(new_txid)
    if len(txids) % 2 == 1:
        new_txid = double_sha256(txids[-1] + txids[-1])
        new_txids.append(new_txid)
    return calculate_merkle_root(new_txids)

def mine_block(block_header):
    nonce = 0
    while True:
        block_header_with_nonce = block_header + format(nonce, '08x')
        block_hash = double_sha256(block_header_with_nonce)
        if block_hash < DIFFICULTY_TARGET:
            return block_hash, nonce
        nonce += 1

def main():
    mempool_dir = "mempool"
    transactions = []
    
    for filename in os.listdir(mempool_dir):
        with open(os.path.join(mempool_dir, filename), 'r') as file:
            tx = json.load(file)
            if validate_transaction(tx):
                tx['txid'] = double_sha256(serialize_transaction(tx))
                transactions.append(tx)
    
    coinbase_tx = create_coinbase_transaction()
    transactions.insert(0, coinbase_tx)
    
    txids = [tx['txid'] for tx in transactions]
    merkle_root = calculate_merkle_root(txids)
    
    timestamp = int(time.time())
    block_header = (
        format(VERSION, '08x') +
        PREV_BLOCK_HASH +
        merkle_root +
        format(timestamp, '08x') +
        DIFFICULTY_TARGET +
        "00000000"
    )
    
    block_hash, nonce = mine_block(block_header)
    
    block_header_output = {
        "version": VERSION,
        "previous_block_hash": PREV_BLOCK_HASH,
        "merkle_root": merkle_root,
        "timestamp": timestamp,
        "difficulty_target": DIFFICULTY_TARGET,
        "nonce": nonce
    }
    
    with open('output.txt', 'w') as output_file:
        output_file.write("Block Header:\n")
        output_file.write(json.dumps(block_header_output, indent=2) + '\n')
        output_file.write("\nSerialized Coinbase Transaction:\n")
        output_file.write(serialize_transaction(coinbase_tx) + '\n')
        output_file.write("\nTransaction IDs:\n")
        for txid in txids:
            output_file.write(txid + '\n')

if __name__ == "__main__":
    main()
