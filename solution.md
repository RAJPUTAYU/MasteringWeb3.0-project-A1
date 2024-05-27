first i imports library then added constants then reading transactions from a mempool then validating them. then creat a coinbase transaction for the block reward then calculating the merkle root of the transactions then construct the block header then mine find a nonce.
For each transaction in the mempool, validate it by checking if the sum of input values is greater than or equal to the sum of output values.
 Create a coinbase transaction for the block reward.
 Calculate the Merkle root using a recursive approach. then Create the block header.
 Continuously hash the block header with increasing nonce values until a hash is found that meets the difficulty target.
then output.