

from typing import List, Optional
from time import time
import json


class Blockchain:


    def __init__(self, difficulty: int = 2, mining_reward: float = 100):

        self.chain = []
        self.difficulty = difficulty
        self.pending_transactions = []
        self.mining_reward = mining_reward

        # Create genesis block
        self.create_genesis_block()

    def create_genesis_block(self) -> None:

        from .block import Block

        # Genesis block with no transactions
        genesis_block = Block(
            timestamp=1483228800,  # 2017-01-01 (like in SavjeeCoin)
            transactions=[],
            previous_hash='0'
        )
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self):

        return self.chain[-1]

    def mine_pending_transactions(self, mining_reward_address: str) -> None:

        from .block import Block
        from .transaction import Transaction

        # Create reward transaction
        reward_tx = Transaction(
            from_address=None,
            to_address=mining_reward_address,
            amount=self.mining_reward
        )
        self.pending_transactions.append(reward_tx)

        # Create new block
        block = Block(
            timestamp=time(),
            transactions=self.pending_transactions,
            previous_hash=self.get_latest_block().hash
        )

        # Mine the block
        block.mine_block(self.difficulty)

        print('Block successfully mined!')

        # Add block to chain
        self.chain.append(block)

        # Reset pending transactions
        self.pending_transactions = []

    def add_transaction(self, transaction) -> None:

        # Validate addresses
        if not transaction.from_address or not transaction.to_address:
            raise Exception('Transaction must include from and to address')

        # Verify transaction
        if not transaction.is_valid():
            raise Exception('Cannot add invalid transaction to chain')

        # Validate amount
        if transaction.amount <= 0:
            raise Exception('Transaction amount should be higher than 0')

        # Check wallet balance
        wallet_balance = self.get_balance_of_address(transaction.from_address)
        if wallet_balance < transaction.amount:
            raise Exception('Not enough balance')

        # Check pending transactions for this wallet
        pending_tx_for_wallet = [
            tx for tx in self.pending_transactions
            if tx.from_address == transaction.from_address
        ]

        # Calculate total pending amount
        if len(pending_tx_for_wallet) > 0:
            total_pending_amount = sum(tx.amount for tx in pending_tx_for_wallet)
            total_amount = total_pending_amount + transaction.amount

            if total_amount > wallet_balance:
                raise Exception('Pending transactions for this wallet is higher than its balance.')

        # Add to pending transactions
        self.pending_transactions.append(transaction)
        print(f'Transaction added: {transaction}')

    def get_balance_of_address(self, address: str) -> float:

        balance = 0

        for block in self.chain:
            for trans in block.transactions:
                # Convert dict to Transaction if needed
                if isinstance(trans, dict):
                    trans_data = trans
                else:
                    trans_data = trans.to_dict()

                # Subtract sent amount
                if trans_data.get('from') == address:
                    balance -= trans_data.get('amount', 0)

                # Add received amount
                if trans_data.get('to') == address:
                    balance += trans_data.get('amount', 0)

        print(f'Balance of {address[:20]}...: {balance}')
        return balance

    def get_all_transactions_for_wallet(self, address: str) -> List:

        transactions = []

        for block in self.chain:
            for tx in block.transactions:
                # Convert dict to Transaction if needed
                if isinstance(tx, dict):
                    from .transaction import Transaction
                    tx = Transaction.from_dict(tx)

                if tx.from_address == address or tx.to_address == address:
                    transactions.append(tx)

        print(f'Transactions for wallet: {len(transactions)}')
        return transactions

    def is_chain_valid(self) -> bool:

        from .block import Block

        # Check Genesis block
        real_genesis = Block(
            timestamp=1483228800,
            transactions=[],
            previous_hash='0'
        )
        real_genesis.mine_block(self.difficulty)

        # Compare genesis blocks
        if json.dumps(real_genesis.to_dict(), sort_keys=True) != json.dumps(self.chain[0].to_dict(), sort_keys=True):
            print('Genesis block has been tampered with')
            return False

        # Check remaining blocks
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                print(f'Invalid previous hash at block {i}')
                return False

            # Check if transactions are valid
            if not current_block.has_valid_transactions():
                print(f'Invalid transactions at block {i}')
                return False

            # Check if hash is correct
            if current_block.hash != current_block.calculate_hash():
                print(f'Invalid hash at block {i}')
                return False

            # Check if block meets difficulty requirement
            if current_block.hash[:self.difficulty] != '0' * self.difficulty:
                print(f'Block {i} was not mined properly')
                return False

        return True

    def to_dict(self) -> dict:

        return {
            'chain': [block.to_dict() for block in self.chain],
            'difficulty': self.difficulty,
            'mining_reward': self.mining_reward,
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Blockchain':

        from .block import Block
        from .transaction import Transaction

        # Create blockchain without genesis block
        blockchain = cls.__new__(cls)
        blockchain.difficulty = data['difficulty']
        blockchain.mining_reward = data['mining_reward']

        # Restore chain
        blockchain.chain = [Block.from_dict(block_data) for block_data in data['chain']]

        # Restore pending transactions
        blockchain.pending_transactions = [
            Transaction.from_dict(tx_data) for tx_data in data['pending_transactions']
        ]

        return blockchain

    def __str__(self) -> str:

        return f"Blockchain(blocks={len(self.chain)}, difficulty={self.difficulty}, pending={len(self.pending_transactions)})"

    def __repr__(self) -> str:

        return self.__str__()