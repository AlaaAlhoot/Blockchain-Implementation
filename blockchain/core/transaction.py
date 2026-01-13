

import hashlib
import json
from time import time
from typing import Optional


class Transaction:


    def __init__(self, from_address: Optional[str], to_address: str, amount: float):

        self.from_address = from_address
        self.to_address = to_address
        self.amount = amount
        self.timestamp = time()
        self.signature = None

    def calculate_hash(self) -> str:

        transaction_string = f"{self.from_address}{self.to_address}{self.amount}{self.timestamp}"
        return hashlib.sha256(transaction_string.encode()).hexdigest()

    def sign(self, wallet):

        # Verify the wallet owns this address
        if wallet.get_public_key() != self.from_address:
            raise Exception('You cannot sign transactions for other wallets!')

        # Calculate hash and sign it
        tx_hash = self.calculate_hash()
        self.signature = wallet.sign_data(tx_hash)

    def is_valid(self) -> bool:

        # Mining reward transactions don't need signature
        if self.from_address is None:
            return True

        # Check if signature exists
        if not self.signature or len(self.signature) == 0:
            raise Exception('No signature in this transaction')

        # Verify signature
        from .wallet import Wallet
        return Wallet.verify_signature(
            self.from_address,
            self.calculate_hash(),
            self.signature
        )

    def to_dict(self) -> dict:

        return {
            'from': self.from_address,
            'to': self.to_address,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'signature': self.signature
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':

        tx = cls(
            from_address=data.get('from'),
            to_address=data['to'],
            amount=data['amount']
        )
        tx.timestamp = data.get('timestamp', time())
        tx.signature = data.get('signature')
        return tx

    def __str__(self) -> str:

        return f"Transaction({self.from_address[:20] if self.from_address else 'MINING'}... → {self.to_address[:20]}... : {self.amount})"

    def __repr__(self) -> str:

        return self.__str__()