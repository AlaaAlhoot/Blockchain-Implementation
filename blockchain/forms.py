

from django import forms
from decimal import Decimal


class CreateWalletForm(forms.Form):

    label = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Wallet label (optional)',
        }),
        label='Wallet Label'
    )


class CreateTransactionForm(forms.Form):

    from_address = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sender wallet address (public key)',
            'readonly': 'readonly',
        }),
        label='From Address'
    )

    private_key = forms.CharField(
        max_length=500,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your private key to sign the transaction',
        }),
        label='Private Key',
        help_text='Required to sign the transaction. Keep it secret!'
    )

    to_address = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Recipient wallet address',
        }),
        label='To Address'
    )

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
        }),
        label='Amount'
    )

    def clean_amount(self):

        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount

    def clean(self):

        cleaned_data = super().clean()
        from_address = cleaned_data.get('from_address')
        to_address = cleaned_data.get('to_address')

        if from_address and to_address and from_address == to_address:
            raise forms.ValidationError('Cannot send transaction to yourself.')

        return cleaned_data


class MineBlockForm(forms.Form):

    miner_address = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your wallet address to receive mining reward',
        }),
        label='Miner Address',
        help_text='The mining reward will be sent to this address'
    )


class CheckBalanceForm(forms.Form):

    address = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter wallet address',
        }),
        label='Wallet Address'
    )


class ImportWalletForm(forms.Form):

    label = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Wallet label (optional)',
        }),
        label='Wallet Label'
    )

    public_key = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Public key (address)',
        }),
        label='Public Key'
    )

    private_key = forms.CharField(
        max_length=500,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Private key',
        }),
        label='Private Key'
    )


class SaveSnapshotForm(forms.Form):

    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Snapshot name',
        }),
        label='Snapshot Name'
    )


class LoadSnapshotForm(forms.Form):

    snapshot_id = forms.IntegerField(
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        label='Select Snapshot'
    )

    def __init__(self, *args, **kwargs):
        snapshots = kwargs.pop('snapshots', [])
        super().__init__(*args, **kwargs)

        if snapshots:
            self.fields['snapshot_id'].widget.choices = [
                (snapshot.id, f"{snapshot.name} - {snapshot.created_at.strftime('%Y-%m-%d %H:%M')}")
                for snapshot in snapshots
            ]