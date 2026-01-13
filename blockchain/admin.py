

from django.contrib import admin
from .models import WalletModel, BlockchainSnapshot, TransactionLog


@admin.register(WalletModel)
class WalletAdmin(admin.ModelAdmin):

    list_display = ['label', 'public_key_short', 'created_at']
    list_filter = ['created_at']
    search_fields = ['label', 'public_key']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Wallet Information', {
            'fields': ('label', 'public_key', 'private_key')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )

    def public_key_short(self, obj):
        """Display shortened public key"""
        return f"{obj.public_key[:30]}..."

    public_key_short.short_description = 'Public Key'


@admin.register(BlockchainSnapshot)
class BlockchainSnapshotAdmin(admin.ModelAdmin):

    list_display = ['name', 'difficulty', 'mining_reward', 'created_at']
    list_filter = ['created_at', 'difficulty']
    search_fields = ['name']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Snapshot Information', {
            'fields': ('name', 'difficulty', 'mining_reward')
        }),
        ('Blockchain Data', {
            'fields': ('blockchain_data',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):

    list_display = ['from_address_short', 'to_address_short', 'amount', 'is_mined', 'timestamp']
    list_filter = ['is_mined', 'timestamp']
    search_fields = ['from_address', 'to_address']
    readonly_fields = ['timestamp']

    fieldsets = (
        ('Transaction Details', {
            'fields': ('from_address', 'to_address', 'amount')
        }),
        ('Signature', {
            'fields': ('signature',),
            'classes': ('collapse',)
        }),
        ('Blockchain Info', {
            'fields': ('is_mined', 'block_index')
        }),
        ('Metadata', {
            'fields': ('timestamp',)
        }),
    )

    def from_address_short(self, obj):
        """Display shortened from address"""
        return f"{obj.from_address[:20]}..."

    from_address_short.short_description = 'From'

    def to_address_short(self, obj):
        """Display shortened to address"""
        return f"{obj.to_address[:20]}..."

    to_address_short.short_description = 'To'