
from blockchain.core.wallet import Wallet
from blockchain.core.transaction import Transaction
from blockchain.core.blockchain import Blockchain

print("=" * 60)
print("Testing Blockchain Core Classes")
print("=" * 60)

# 1. Create wallets
print("\n1. Creating Wallets...")
wallet1 = Wallet()
wallet2 = Wallet()
wallet3 = Wallet()

print(f"Wallet 1: {wallet1.get_public_key()[:30]}...")
print(f"Wallet 2: {wallet2.get_public_key()[:30]}...")
print(f"Wallet 3: {wallet3.get_public_key()[:30]}...")

# 2. Create blockchain
print("\n2. Creating Blockchain...")
blockchain = Blockchain(difficulty=4, mining_reward=100)
print(f"Genesis block created: {blockchain.chain[0]}")

# 3. Mine first block (to get some coins)
print("\n3. Mining first block for Wallet 1...")
blockchain.mine_pending_transactions(wallet1.get_public_key())
print(f"Wallet 1 balance: {blockchain.get_balance_of_address(wallet1.get_public_key())}")

# 4. Create and sign transaction
print("\n4. Creating transaction: Wallet 1 → Wallet 2 (50 coins)...")
tx1 = Transaction(wallet1.get_public_key(), wallet2.get_public_key(), 50)
tx1.sign(wallet1)
blockchain.add_transaction(tx1)

# 5. Mine block
print("\n5. Mining block for Wallet 3...")
blockchain.mine_pending_transactions(wallet3.get_public_key())

# 6. Check balances
print("\n6. Final Balances:")
print(f"Wallet 1: {blockchain.get_balance_of_address(wallet1.get_public_key())}")
print(f"Wallet 2: {blockchain.get_balance_of_address(wallet2.get_public_key())}")
print(f"Wallet 3: {blockchain.get_balance_of_address(wallet3.get_public_key())}")

# 7. Validate chain
print("\n7. Validating Blockchain...")
is_valid = blockchain.is_chain_valid()
print(f"Blockchain is valid: {is_valid}")

# 8. Display chain
print("\n8. Blockchain Summary:")
print(f"Total blocks: {len(blockchain.chain)}")
print(f"Pending transactions: {len(blockchain.pending_transactions)}")

print("\n" + "=" * 60)
print("Test completed successfully!")
print("=" * 60)
