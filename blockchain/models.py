

from django.db import models
from django.utils import timezone


class WalletModel(models.Model):

    public_key = models.CharField(max_length=500, unique=True, verbose_name="Public Key (Address)")
    private_key = models.CharField(max_length=500, verbose_name="Private Key")
    label = models.CharField(max_length=100, blank=True, null=True, verbose_name="Wallet Label")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.label or 'Wallet'} - {self.public_key[:20]}..."


class BlockchainSnapshot(models.Model):

    name = models.CharField(max_length=200, verbose_name="Snapshot Name")
    blockchain_data = models.JSONField(verbose_name="Blockchain Data")
    difficulty = models.IntegerField(verbose_name="Difficulty Level")
    mining_reward = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Mining Reward")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")

    class Meta:
        verbose_name = "Blockchain Snapshot"
        verbose_name_plural = "Blockchain Snapshots"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class TransactionLog(models.Model):

    from_address = models.CharField(max_length=500, verbose_name="From Address")
    to_address = models.CharField(max_length=500, verbose_name="To Address")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Timestamp")
    signature = models.TextField(verbose_name="Digital Signature")
    is_mined = models.BooleanField(default=False, verbose_name="Is Mined")
    block_index = models.IntegerField(null=True, blank=True, verbose_name="Block Index")

    class Meta:
        verbose_name = "Transaction Log"
        verbose_name_plural = "Transaction Logs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.from_address[:20]}... → {self.to_address[:20]}... ({self.amount})"