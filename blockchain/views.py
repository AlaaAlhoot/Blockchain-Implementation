# blockchain/views.py
"""
Views for blockchain app
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings

from .forms import (
    CreateWalletForm,
    CreateTransactionForm,
    MineBlockForm,
    CheckBalanceForm,
    ImportWalletForm,
    SaveSnapshotForm,
    LoadSnapshotForm
)
from .models import WalletModel, BlockchainSnapshot, TransactionLog

import json
from datetime import datetime


# ============================================================================
# Helper Functions for Session Management
# ============================================================================

def get_blockchain(request):
    """
    Get or create blockchain instance from session
    """
    from .core.blockchain import Blockchain

    blockchain_data = request.session.get(settings.BLOCKCHAIN_SESSION_KEY)

    if blockchain_data:
        # Load existing blockchain from session
        blockchain = Blockchain.from_dict(blockchain_data)
    else:
        # Create new blockchain
        blockchain = Blockchain(
            difficulty=settings.BLOCKCHAIN_DIFFICULTY,
            mining_reward=settings.MINING_REWARD
        )
        # Save to session
        save_blockchain(request, blockchain)

    return blockchain


def save_blockchain(request, blockchain):
    """
    Save blockchain instance to session
    """
    request.session[settings.BLOCKCHAIN_SESSION_KEY] = blockchain.to_dict()
    request.session.modified = True


def get_wallets(request):
    """
    Get wallets from session
    """
    return request.session.get(settings.WALLETS_SESSION_KEY, [])


def save_wallets(request, wallets):
    """
    Save wallets to session
    """
    request.session[settings.WALLETS_SESSION_KEY] = wallets
    request.session.modified = True


def add_wallet(request, wallet_data):
    """
    Add wallet to session
    """
    wallets = get_wallets(request)
    wallets.append(wallet_data)
    save_wallets(request, wallets)


def remove_wallet(request, address):
    """
    Remove wallet from session
    """
    wallets = get_wallets(request)
    wallets = [w for w in wallets if w['public_key'] != address]
    save_wallets(request, wallets)


# ============================================================================
# Main Views
# ============================================================================

def home(request):
    """
    Home page - Display blockchain overview
    """
    blockchain = get_blockchain(request)

    context = {
        'blockchain': blockchain,
        'chain': blockchain.to_dict()['chain'],
        'difficulty': blockchain.difficulty,
        'mining_reward': blockchain.mining_reward,
        'pending_count': len(blockchain.pending_transactions),
        'is_valid': blockchain.is_chain_valid(),
        'total_blocks': len(blockchain.chain),
    }

    return render(request, 'blockchain/home.html', context)


def about(request):
    """
    About page - Information about the blockchain
    """
    return render(request, 'blockchain/about.html')


# ============================================================================
# Wallet Views
# ============================================================================

def wallet_list(request):
    """
    List all wallets
    """
    wallets = get_wallets(request)
    blockchain = get_blockchain(request)

    # Calculate balance for each wallet
    for wallet in wallets:
        wallet['balance'] = blockchain.get_balance_of_address(wallet['public_key'])

    context = {
        'wallets': wallets,
        'create_form': CreateWalletForm(),
        'import_form': ImportWalletForm(),
    }

    return render(request, 'blockchain/wallet_list.html', context)


@require_http_methods(["POST"])
def wallet_create(request):
    """
    Create a new wallet
    """
    from .core.wallet import Wallet

    form = CreateWalletForm(request.POST)

    if form.is_valid():
        label = form.cleaned_data.get('label', '')

        # Generate new wallet
        wallet = Wallet()

        # Prepare wallet data
        wallet_data = {
            'label': label or f'Wallet {len(get_wallets(request)) + 1}',
            'public_key': wallet.get_public_key(),
            'private_key': wallet.get_private_key(),
            'created_at': datetime.now().isoformat(),
        }

        # Add to session
        add_wallet(request, wallet_data)

        messages.success(request, f'Wallet "{wallet_data["label"]}" created successfully!')
    else:
        messages.error(request, 'Failed to create wallet. Please try again.')

    return redirect('blockchain:wallet_list')


@require_http_methods(["POST"])
def wallet_import(request):
    """
    Import an existing wallet
    """
    form = ImportWalletForm(request.POST)

    if form.is_valid():
        wallet_data = {
            'label': form.cleaned_data.get('label', '') or f'Imported Wallet {len(get_wallets(request)) + 1}',
            'public_key': form.cleaned_data['public_key'],
            'private_key': form.cleaned_data['private_key'],
            'created_at': datetime.now().isoformat(),
        }

        # Check if wallet already exists
        wallets = get_wallets(request)
        if any(w['public_key'] == wallet_data['public_key'] for w in wallets):
            messages.warning(request, 'This wallet already exists!')
        else:
            add_wallet(request, wallet_data)
            messages.success(request, f'Wallet "{wallet_data["label"]}" imported successfully!')
    else:
        messages.error(request, 'Invalid wallet data. Please check your input.')

    return redirect('blockchain:wallet_list')


@require_http_methods(["POST"])
def wallet_delete(request, address):
    """
    Delete a wallet
    """
    remove_wallet(request, address)
    messages.success(request, 'Wallet deleted successfully!')
    return redirect('blockchain:wallet_list')


# ============================================================================
# Transaction Views
# ============================================================================

def transaction_create(request):
    """
    Create a new transaction
    """
    blockchain = get_blockchain(request)
    wallets = get_wallets(request)

    if request.method == 'POST':
        form = CreateTransactionForm(request.POST)

        if form.is_valid():
            from .core.transaction import Transaction
            from .core.wallet import Wallet

            try:
                # Create transaction
                transaction = Transaction(
                    from_address=form.cleaned_data['from_address'],
                    to_address=form.cleaned_data['to_address'],
                    amount=float(form.cleaned_data['amount'])
                )

                # Load wallet to sign transaction
                wallet = Wallet.from_private_key(form.cleaned_data['private_key'])

                # Sign transaction
                transaction.sign(wallet)

                # Add to blockchain
                blockchain.add_transaction(transaction)
                save_blockchain(request, blockchain)

                messages.success(request, 'Transaction created and signed successfully!')
                return redirect('blockchain:transaction_pending')

            except Exception as e:
                messages.error(request, f'Error creating transaction: {str(e)}')
    else:
        # Pre-fill from_address if wallet is selected
        initial_data = {}
        selected_wallet = request.GET.get('wallet')
        if selected_wallet:
            wallet = next((w for w in wallets if w['public_key'] == selected_wallet), None)
            if wallet:
                initial_data['from_address'] = wallet['public_key']

        form = CreateTransactionForm(initial=initial_data)

    context = {
        'form': form,
        'wallets': wallets,
    }

    return render(request, 'blockchain/transaction_create.html', context)


def transaction_pending(request):
    """
    Display pending transactions
    """
    blockchain = get_blockchain(request)

    # Convert transactions to dict for display
    pending_transactions = [tx.to_dict() for tx in blockchain.pending_transactions]

    context = {
        'pending_transactions': pending_transactions,
        'pending_count': len(pending_transactions),
        'mine_form': MineBlockForm(),
    }

    return render(request, 'blockchain/transaction_pending.html', context)


# ============================================================================
# Mining Views
# ============================================================================

def mine_block(request):

    blockchain = get_blockchain(request)

    if request.method == 'POST':
        form = MineBlockForm(request.POST)

        if form.is_valid():
            try:
                miner_address = form.cleaned_data['miner_address']

                # Mine the block
                print(f"Mining for: {miner_address}")  # للتشخيص
                blockchain.mine_pending_transactions(miner_address)
                save_blockchain(request, blockchain)

                messages.success(request, f'Block mined successfully! Reward sent to {miner_address[:20]}...')
                return redirect('blockchain:home')

            except Exception as e:
                print(f"Mining error: {str(e)}")  # للتشخيص
                messages.error(request, f'Error mining block: {str(e)}')
        else:
            print(f"Form errors: {form.errors}")  # للتشخيص
    else:
        form = MineBlockForm()

    context = {
        'form': form,
        'pending_count': len(blockchain.pending_transactions),
    }

    return render(request, 'blockchain/mine_block.html', context)



# ============================================================================
# Balance and Details Views
# ============================================================================

def check_balance(request):
    """
    Check balance of an address
    """
    blockchain = get_blockchain(request)
    balance = None
    address = None
    transactions = []

    if request.method == 'POST':
        form = CheckBalanceForm(request.POST)

        if form.is_valid():
            address = form.cleaned_data['address']
            balance = blockchain.get_balance_of_address(address)
            transactions = blockchain.get_all_transactions_for_wallet(address)
            transactions = [tx.to_dict() for tx in transactions]
    else:
        form = CheckBalanceForm()

    context = {
        'form': form,
        'balance': balance,
        'address': address,
        'transactions': transactions,
    }

    return render(request, 'blockchain/check_balance.html', context)


def address_detail(request, address):
    """
    Display details for a specific address
    """
    blockchain = get_blockchain(request)

    balance = blockchain.get_balance_of_address(address)
    transactions = blockchain.get_all_transactions_for_wallet(address)
    transactions = [tx.to_dict() for tx in transactions]

    context = {
        'address': address,
        'balance': balance,
        'transactions': transactions,
        'transaction_count': len(transactions),
    }

    return render(request, 'blockchain/address_detail.html', context)


def block_detail(request, index):
    """
    Display details of a specific block
    """
    blockchain = get_blockchain(request)

    # Validate index
    if index >= len(blockchain.chain) or index < 0:
        messages.error(request, f'Block {index} does not exist!')
        return redirect('blockchain:home')

    # Get block
    block = blockchain.chain[index]

    # Convert block to dict using to_dict() method
    if hasattr(block, 'to_dict'):
        block_dict = block.to_dict()
    else:
        # Manual conversion
        block_dict = {
            'timestamp': block.timestamp,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce,
            'hash': block.hash,
            'transactions': []
        }

        # Convert transactions
        for tx in block.transactions:
            if hasattr(tx, 'to_dict'):
                block_dict['transactions'].append(tx.to_dict())
            else:
                block_dict['transactions'].append({
                    'from': getattr(tx, 'from_address', None),
                    'to': getattr(tx, 'to_address', ''),
                    'amount': getattr(tx, 'amount', 0),
                    'timestamp': getattr(tx, 'timestamp', 0),
                    'signature': getattr(tx, 'signature', None)
                })

    # Debug - طباعة للتأكد
    print(f"\n=== SENDING TO TEMPLATE ===")
    print(f"index: {index}")
    print(f"block_dict keys: {block_dict.keys()}")
    print(f"timestamp: {block_dict.get('timestamp')}")
    print(f"nonce: {block_dict.get('nonce')}")
    print(f"hash: {block_dict.get('hash', '')[:20]}")
    print(f"transactions count: {len(block_dict.get('transactions', []))}")
    print(f"===========================\n")

    context = {
        'index': index,
        'is_genesis': index == 0,
        'prev_block': index - 1 if index > 0 else None,
        'next_block': index + 1 if index + 1 < len(blockchain.chain) else None,
        'block': block_dict,
    }

    return render(request, 'blockchain/block_detail.html', context)

# ============================================================================
# Blockchain Operations
# ============================================================================

def validate_chain(request):
    """
    Validate the blockchain
    """
    blockchain = get_blockchain(request)
    is_valid = blockchain.is_chain_valid()

    if is_valid:
        messages.success(request, 'Blockchain is valid! ✓')
    else:
        messages.error(request, 'Blockchain is invalid! Chain has been tampered with.')

    return redirect('blockchain:home')


@require_http_methods(["POST"])
def reset_blockchain(request):
    """
    Reset the blockchain to genesis block
    """
    # Clear blockchain from session
    if settings.BLOCKCHAIN_SESSION_KEY in request.session:
        del request.session[settings.BLOCKCHAIN_SESSION_KEY]

    messages.success(request, 'Blockchain has been reset!')
    return redirect('blockchain:home')


# ============================================================================
# Snapshot Management (Optional)
# ============================================================================

def save_snapshot(request):
    """
    Save current blockchain state as a snapshot
    """
    if request.method == 'POST':
        form = SaveSnapshotForm(request.POST)

        if form.is_valid():
            blockchain = get_blockchain(request)

            snapshot = BlockchainSnapshot.objects.create(
                name=form.cleaned_data['name'],
                blockchain_data=blockchain.to_dict(),
                difficulty=blockchain.difficulty,
                mining_reward=blockchain.mining_reward,
            )

            messages.success(request, f'Snapshot "{snapshot.name}" saved successfully!')
            return redirect('blockchain:snapshot_list')
    else:
        form = SaveSnapshotForm()

    context = {
        'form': form,
    }

    return render(request, 'blockchain/save_snapshot.html', context)


def load_snapshot(request):
    """
    Load a blockchain snapshot
    """
    snapshots = BlockchainSnapshot.objects.all()

    if request.method == 'POST':
        form = LoadSnapshotForm(request.POST, snapshots=snapshots)

        if form.is_valid():
            snapshot_id = form.cleaned_data['snapshot_id']
            snapshot = get_object_or_404(BlockchainSnapshot, id=snapshot_id)

            # Load blockchain from snapshot
            request.session[settings.BLOCKCHAIN_SESSION_KEY] = snapshot.blockchain_data

            messages.success(request, f'Snapshot "{snapshot.name}" loaded successfully!')
            return redirect('blockchain:home')
    else:
        form = LoadSnapshotForm(snapshots=snapshots)

    context = {
        'form': form,
        'snapshots': snapshots,
    }

    return render(request, 'blockchain/load_snapshot.html', context)


def snapshot_list(request):
    """
    List all blockchain snapshots
    """
    snapshots = BlockchainSnapshot.objects.all()

    context = {
        'snapshots': snapshots,
    }

    return render(request, 'blockchain/snapshot_list.html', context)


# ============================================================================
# API Endpoints (for AJAX)
# ============================================================================

def api_get_chain(request):
    """
    API endpoint to get blockchain data as JSON
    """
    blockchain = get_blockchain(request)
    return JsonResponse(blockchain.to_dict(), safe=False)


def api_get_pending_transactions(request):
    """
    API endpoint to get pending transactions as JSON
    """
    blockchain = get_blockchain(request)
    pending = [tx.to_dict() for tx in blockchain.pending_transactions]
    return JsonResponse({'pending_transactions': pending}, safe=False)

