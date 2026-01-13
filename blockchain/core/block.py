
import hashlib
import json
from time import time
from typing import List, Optional


class Block:


    def __init__(self, timestamp: float, transactions: List, previous_hash: str = ''):

        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:

        # Convert transactions to dict for consistent hashing
        transactions_data = [
            tx.to_dict() if hasattr(tx, 'to_dict') else tx
            for tx in self.transactions
        ]

        block_string = json.dumps({
            'timestamp': self.timestamp,
            'transactions': transactions_data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:

        target = '0' * difficulty

        # Keep changing nonce until hash meets difficulty requirement
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

        print(f"Block mined: {self.hash}")

    def has_valid_transactions(self) -> bool:

        for tx in self.transactions:
            # Convert dict to Transaction if needed
            if isinstance(tx, dict):
                from .transaction import Transaction
                tx = Transaction.from_dict(tx)

            if not tx.is_valid():
                return False

        return True

    def to_dict(self) -> dict:

        transactions_data = [
            tx.to_dict() if hasattr(tx, 'to_dict') else tx
            for tx in self.transactions
        ]

        return {
            'timestamp': self.timestamp,
            'transactions': transactions_data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Block':

        from .transaction import Transaction


        transactions = [
            Transaction.from_dict(tx) if isinstance(tx, dict) else tx
            for tx in data['transactions']
        ]

        block = cls(
            timestamp=data['timestamp'],
            transactions=transactions,
            previous_hash=data['previous_hash']
        )
        block.nonce = data['nonce']
        block.hash = data['hash']

        return block

    def __str__(self) -> str:

        return f"Block(hash={self.hash[:20]}..., transactions={len(self.transactions)}, nonce={self.nonce})"

    def __repr__(self) -> str:

        return self.__str__()