
import hashlib
from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError
from typing import Optional


class Wallet:


    def __init__(self, private_key: Optional[str] = None):

        if private_key:
            # Load existing wallet from private key
            self.signing_key = SigningKey.from_string(
                bytes.fromhex(private_key),
                curve=SECP256k1
            )
        else:
            # Generate new key pair
            self.signing_key = SigningKey.generate(curve=SECP256k1)

        # Get verifying key (public key)
        self.verifying_key = self.signing_key.get_verifying_key()

    def get_private_key(self) -> str:

        return self.signing_key.to_string().hex()

    def get_public_key(self) -> str:

        return self.verifying_key.to_string().hex()

    def sign_data(self, data: str) -> str:

        signature = self.signing_key.sign(data.encode())
        return signature.hex()

    @staticmethod
    def verify_signature(public_key: str, data: str, signature: str) -> bool:

        try:
            verifying_key = VerifyingKey.from_string(
                bytes.fromhex(public_key),
                curve=SECP256k1
            )
            verifying_key.verify(bytes.fromhex(signature), data.encode())
            return True
        except (BadSignatureError, ValueError):
            return False

    @classmethod
    def from_private_key(cls, private_key: str) -> 'Wallet':

        return cls(private_key=private_key)

    def to_dict(self) -> dict:

        return {
            'public_key': self.get_public_key(),
            'private_key': self.get_private_key()
        }

    def __str__(self) -> str:

        return f"Wallet(address={self.get_public_key()[:20]}...)"

    def __repr__(self) -> str:

        return self.__str__()


def generate_wallet() -> dict:

    wallet = Wallet()
    return {
        'public_key': wallet.get_public_key(),
        'private_key': wallet.get_private_key()
    }


def generate_multiple_wallets(count: int = 1) -> list:

    return [generate_wallet() for _ in range(count)]