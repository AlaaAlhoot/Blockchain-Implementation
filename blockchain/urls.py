

from django.urls import path
from . import views

app_name = 'blockchain'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),

    # Wallet management
    path('wallet/', views.wallet_list, name='wallet_list'),
    path('wallet/create/', views.wallet_create, name='wallet_create'),
    path('wallet/import/', views.wallet_import, name='wallet_import'),
    path('wallet/delete/<str:address>/', views.wallet_delete, name='wallet_delete'),

    # Transaction management
    path('transaction/create/', views.transaction_create, name='transaction_create'),
    path('transaction/pending/', views.transaction_pending, name='transaction_pending'),

    # Mining
    path('mine/', views.mine_block, name='mine_block'),

    # Balance and details
    path('balance/', views.check_balance, name='check_balance'),
    path('balance/<str:address>/', views.address_detail, name='address_detail'),

    # Block details
    path('block/<int:index>/', views.block_detail, name='block_detail'),

    # Blockchain operations
    path('validate/', views.validate_chain, name='validate_chain'),
    path('reset/', views.reset_blockchain, name='reset_blockchain'),

    # Snapshot management (optional)
    path('snapshot/save/', views.save_snapshot, name='save_snapshot'),
    path('snapshot/load/', views.load_snapshot, name='load_snapshot'),
    path('snapshot/list/', views.snapshot_list, name='snapshot_list'),

    # API endpoints (for AJAX)
    path('api/chain/', views.api_get_chain, name='api_get_chain'),
    path('api/pending-transactions/', views.api_get_pending_transactions, name='api_get_pending_transactions'),
]