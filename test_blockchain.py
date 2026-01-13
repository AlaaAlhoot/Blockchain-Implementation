# test_blockchain.py
"""
Comprehensive Testing Script for Blockchain Implementation
Tests all core functionality including wallets, transactions, mining, and validation
"""

import sys
import os

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blockchain_project.settings')
import django

django.setup()

from blockchain.core.wallet import Wallet
from blockchain.core.transaction import Transaction
from blockchain.core.blockchain import Blockchain

print("=" * 70)
print(" " * 15 + "BLOCKCHAIN COMPREHENSIVE TEST")
print("=" * 70)

# ============================================================================
# Test 1: Wallet Generation
# ============================================================================
print("\n" + "=" * 70)
print("TEST 1: Wallet Generation")
print("=" * 70)

try:
    wallet1 = Wallet()
    wallet2 = Wallet()
    wallet3 = Wallet()

    print(f"✓ Wallet 1 created")
    print(f"  Public Key:  {wallet1.get_public_key()[:40]}...")
    print(f"  Private Key: {wallet1.get_private_key()[:40]}...")

    print(f"\n✓ Wallet 2 created")
    print(f"  Public Key:  {wallet2.get_public_key()[:40]}...")

    print(f"\n✓ Wallet 3 created")
    print(f"  Public Key:  {wallet3.get_public_key()[:40]}...")

    print("\n✅ PASSED: Wallet generation successful")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 2: Blockchain Initialization
# ============================================================================
print("\n" + "=" * 70)
print("TEST 2: Blockchain Initialization")
print("=" * 70)

try:
    blockchain = Blockchain(difficulty=4, mining_reward=100)

    print(f"✓ Blockchain created")
    print(f"  Difficulty: {blockchain.difficulty}")
    print(f"  Mining Reward: {blockchain.mining_reward}")
    print(f"  Chain Length: {len(blockchain.chain)}")

    genesis = blockchain.chain[0]
    print(f"\n✓ Genesis Block:")
    print(f"  Timestamp: {genesis.to_dict()['timestamp']}")
    print(f"  Hash: {genesis.hash[:40]}...")
    print(f"  Transactions: {len(genesis.transactions)}")

    print("\n✅ PASSED: Blockchain initialized with Genesis block")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 3: Mining Initial Blocks
# ============================================================================
print("\n" + "=" * 70)
print("TEST 3: Mining Initial Blocks for Coins")
print("=" * 70)

try:
    print("Mining Block 1 for Wallet 1...")
    blockchain.mine_pending_transactions(wallet1.get_public_key())
    print(f"✓ Block 1 mined")

    print("\nMining Block 2 for Wallet 1...")
    blockchain.mine_pending_transactions(wallet1.get_public_key())
    print(f"✓ Block 2 mined")

    # Check balance after second mining
    balance1 = blockchain.get_balance_of_address(wallet1.get_public_key())
    print(f"\n✓ Wallet 1 Balance: {balance1} coins")

    # Mining reward appears after next block is mined
    # So after mining 2 blocks, wallet should have at least 100 coins
    if balance1 < 100:
        raise Exception(f"Expected at least 100 coins, got {balance1}")

    print("\n✅ PASSED: Mining and reward system working")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 4: Transaction Creation and Signing
# ============================================================================
print("\n" + "=" * 70)
print("TEST 4: Transaction Creation and Signing")
print("=" * 70)

try:
    # Create transaction
    tx1 = Transaction(
        from_address=wallet1.get_public_key(),
        to_address=wallet2.get_public_key(),
        amount=30
    )

    print(f"✓ Transaction created:")
    print(f"  From: {tx1.from_address[:40]}...")
    print(f"  To: {tx1.to_address[:40]}...")
    print(f"  Amount: {tx1.amount} coins")

    # Sign transaction
    tx1.sign(wallet1)
    print(f"\n✓ Transaction signed")
    print(f"  Signature: {tx1.signature[:40]}...")

    # Verify signature
    is_valid = tx1.is_valid()
    print(f"\n✓ Signature verification: {is_valid}")

    if not is_valid:
        raise Exception("Transaction signature is invalid!")

    # Add to blockchain
    blockchain.add_transaction(tx1)
    print(f"\n✓ Transaction added to pending transactions")
    print(f"  Pending count: {len(blockchain.pending_transactions)}")

    print("\n✅ PASSED: Transaction creation and signing successful")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 5: Mining Transactions
# ============================================================================
print("\n" + "=" * 70)
print("TEST 5: Mining Transactions into Block")
print("=" * 70)

try:
    print("Mining pending transactions...")
    blockchain.mine_pending_transactions(wallet3.get_public_key())

    print(f"✓ Block mined")
    print(f"  Chain Length: {len(blockchain.chain)}")

    # Check balances
    balance1 = blockchain.get_balance_of_address(wallet1.get_public_key())
    balance2 = blockchain.get_balance_of_address(wallet2.get_public_key())
    balance3 = blockchain.get_balance_of_address(wallet3.get_public_key())

    print(f"\n✓ Updated Balances:")
    print(f"  Wallet 1: {balance1} coins (initial balance minus 30)")
    print(f"  Wallet 2: {balance2} coins (received 30)")
    print(f"  Wallet 3: {balance3} coins (mining reward pending)")

    # Wallet 2 should have 30 coins
    if balance2 != 30:
        raise Exception(f"Wallet 2 balance incorrect: expected 30, got {balance2}")

    print("\n✅ PASSED: Transaction mining successful")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 6: Multiple Transactions
# ============================================================================
print("\n" + "=" * 70)
print("TEST 6: Multiple Transactions in One Block")
print("=" * 70)

try:
    # Transaction 2: Wallet 2 -> Wallet 3
    tx2 = Transaction(
        from_address=wallet2.get_public_key(),
        to_address=wallet3.get_public_key(),
        amount=10
    )
    tx2.sign(wallet2)
    blockchain.add_transaction(tx2)
    print(f"✓ Transaction 2 added: Wallet 2 → Wallet 3 (10 coins)")

    # Transaction 3: Wallet 1 -> Wallet 3
    tx3 = Transaction(
        from_address=wallet1.get_public_key(),
        to_address=wallet3.get_public_key(),
        amount=20
    )
    tx3.sign(wallet1)
    blockchain.add_transaction(tx3)
    print(f"✓ Transaction 3 added: Wallet 1 → Wallet 3 (20 coins)")

    print(f"\n✓ Pending transactions: {len(blockchain.pending_transactions)}")

    # Mine block
    print("\nMining block with multiple transactions...")
    blockchain.mine_pending_transactions(wallet1.get_public_key())

    # Mine one more block to process the mining reward
    print("Mining one more block to process rewards...")
    blockchain.mine_pending_transactions(wallet1.get_public_key())

    # Check final balances
    balance1 = blockchain.get_balance_of_address(wallet1.get_public_key())
    balance2 = blockchain.get_balance_of_address(wallet2.get_public_key())
    balance3 = blockchain.get_balance_of_address(wallet3.get_public_key())

    print(f"\n✓ Final Balances:")
    print(f"  Wallet 1: {balance1} coins")
    print(f"  Wallet 2: {balance2} coins")
    print(f"  Wallet 3: {balance3} coins")

    # Wallet 2 should have 20 (30 - 10)
    if balance2 != 20:
        raise Exception(f"Wallet 2 balance incorrect: expected 20, got {balance2}")

    # Wallet 3 should have at least 30 (10 + 20 from transactions)
    if balance3 < 30:
        raise Exception(f"Wallet 3 balance incorrect: expected at least 30, got {balance3}")

    print("\n✅ PASSED: Multiple transactions successful")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 7: Blockchain Validation
# ============================================================================
print("\n" + "=" * 70)
print("TEST 7: Blockchain Validation")
print("=" * 70)

try:
    is_valid = blockchain.is_chain_valid()
    print(f"✓ Blockchain validation result: {is_valid}")

    if not is_valid:
        raise Exception("Blockchain is invalid!")

    print("\n✅ PASSED: Blockchain is valid")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 8: Tampering Detection
# ============================================================================
print("\n" + "=" * 70)
print("TEST 8: Tampering Detection")
print("=" * 70)

try:
    print("Attempting to tamper with a transaction in the blockchain...")

    # Find a block with transactions
    target_block = None
    target_block_index = None
    for i, block in enumerate(blockchain.chain):
        if len(block.transactions) > 0 and block.transactions[0].from_address is not None:
            target_block = block
            target_block_index = i
            break

    if target_block:
        original_amount = target_block.transactions[0].amount
        print(f"✓ Found block {target_block_index} with transaction amount: {original_amount}")

        # Tamper with the amount
        target_block.transactions[0].amount = 9999
        print(f"✓ Changed transaction amount to: 9999")

        # Validate chain
        is_valid_after_tamper = blockchain.is_chain_valid()
        print(f"✓ Validation after tampering: {is_valid_after_tamper}")

        if is_valid_after_tamper:
            raise Exception("Blockchain should be invalid after tampering!")

        # Restore original value
        target_block.transactions[0].amount = original_amount
        print(f"✓ Restored original amount: {original_amount}")

        # Verify restoration
        is_valid_after_restore = blockchain.is_chain_valid()
        print(f"✓ Validation after restoration: {is_valid_after_restore}")

        if not is_valid_after_restore:
            raise Exception("Blockchain should be valid after restoration!")
    else:
        print("✓ No suitable block found for tampering test (skipped)")

    print("\n✅ PASSED: Tampering detection working")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 9: Insufficient Balance Prevention
# ============================================================================
print("\n" + "=" * 70)
print("TEST 9: Insufficient Balance Prevention")
print("=" * 70)

try:
    # Get current balance
    current_balance = blockchain.get_balance_of_address(wallet2.get_public_key())
    print(f"✓ Wallet 2 current balance: {current_balance} coins")

    # Try to spend more than balance
    overspend_amount = current_balance + 1000
    tx_overspend = Transaction(
        from_address=wallet2.get_public_key(),
        to_address=wallet3.get_public_key(),
        amount=overspend_amount
    )
    tx_overspend.sign(wallet2)

    print(f"Attempting to send {overspend_amount} coins (more than balance)...")

    try:
        blockchain.add_transaction(tx_overspend)
        raise Exception("Should have rejected transaction with insufficient balance!")
    except Exception as e:
        if "Not enough balance" in str(e):
            print(f"✓ Transaction rejected: {str(e)}")
        else:
            raise e

    print("\n✅ PASSED: Insufficient balance prevention working")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 10: Invalid Signature Detection
# ============================================================================
print("\n" + "=" * 70)
print("TEST 10: Invalid Signature Detection")
print("=" * 70)

try:
    # Create transaction from wallet1
    tx_fake = Transaction(
        from_address=wallet1.get_public_key(),
        to_address=wallet3.get_public_key(),
        amount=10
    )

    # Try to sign with wrong wallet
    print("Attempting to sign Wallet 1 transaction with Wallet 2 private key...")

    try:
        tx_fake.sign(wallet2)  # Wrong wallet!
        raise Exception("Should have rejected signing with wrong key!")
    except Exception as e:
        if "cannot sign transactions for other wallets" in str(e).lower():
            print(f"✓ Signature rejected: {str(e)}")
        else:
            raise e

    print("\n✅ PASSED: Invalid signature detection working")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 11: Transaction History
# ============================================================================
print("\n" + "=" * 70)
print("TEST 11: Transaction History")
print("=" * 70)

try:
    transactions = blockchain.get_all_transactions_for_wallet(wallet1.get_public_key())

    print(f"✓ Wallet 1 transaction history:")
    print(f"  Total transactions: {len(transactions)}")

    if len(transactions) > 0:
        print(f"\n  Recent transactions:")
        for i, tx in enumerate(transactions[:5], 1):  # Show first 5
            tx_data = tx.to_dict()
            from_addr = tx_data['from'][:20] if tx_data['from'] else 'MINING REWARD'
            to_addr = tx_data['to'][:20]
            print(f"    {i}. {from_addr}... → {to_addr}... : {tx_data['amount']} coins")

    print("\n✅ PASSED: Transaction history retrieval successful")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Test 12: Blockchain Summary
# ============================================================================
print("\n" + "=" * 70)
print("TEST 12: Blockchain Summary")
print("=" * 70)

try:
    print(f"✓ Total Blocks: {len(blockchain.chain)}")
    print(f"✓ Pending Transactions: {len(blockchain.pending_transactions)}")
    print(f"✓ Difficulty: {blockchain.difficulty}")
    print(f"✓ Mining Reward: {blockchain.mining_reward}")
    print(f"✓ Is Valid: {blockchain.is_chain_valid()}")

    print("\n✓ Block Summary:")
    for i, block in enumerate(blockchain.chain):
        block_data = block.to_dict()
        print(
            f"  Block {i}: {len(block_data['transactions'])} tx, nonce: {block_data['nonce']}, hash: {block_data['hash'][:20]}...")

    print("\n✓ Final Wallet Balances:")
    print(f"  Wallet 1: {blockchain.get_balance_of_address(wallet1.get_public_key())} coins")
    print(f"  Wallet 2: {blockchain.get_balance_of_address(wallet2.get_public_key())} coins")
    print(f"  Wallet 3: {blockchain.get_balance_of_address(wallet3.get_public_key())} coins")

    print("\n✅ PASSED: Blockchain summary generated")
except Exception as e:
    print(f"\n❌ FAILED: {str(e)}")
    sys.exit(1)

# ============================================================================
# Final Summary
# ============================================================================
print("\n" + "=" * 70)
print(" " * 20 + "TEST SUMMARY")
print("=" * 70)

print("\n🎉 ALL TESTS PASSED!")
print("\nTests Completed:")
print("  1. ✓ Wallet Generation")
print("  2. ✓ Blockchain Initialization")
print("  3. ✓ Mining Initial Blocks")
print("  4. ✓ Transaction Creation and Signing")
print("  5. ✓ Mining Transactions")
print("  6. ✓ Multiple Transactions")
print("  7. ✓ Blockchain Validation")
print("  8. ✓ Tampering Detection")
print("  9. ✓ Insufficient Balance Prevention")
print(" 10. ✓ Invalid Signature Detection")
print(" 11. ✓ Transaction History")
print(" 12. ✓ Blockchain Summary")

print("\n" + "=" * 70)
print("✅ Blockchain implementation is working correctly!")
print("=" * 70)
print("\nYou can now run the Django server:")
print("  python manage.py runserver")
print("\nThen visit: http://127.0.0.1:8000/")
print("=" * 70)