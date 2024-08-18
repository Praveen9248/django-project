from django import forms
from django.contrib.auth.models import User
from .models import Group, Expense, Payment

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "__all__"

class ExpenseForm(forms.ModelForm):
    SPLIT_CHOICES = [
        ('equal', 'Split Equally'),
    ]
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Select Group")
    split_method = forms.ChoiceField(choices=SPLIT_CHOICES, widget=forms.RadioSelect, label="Split Method")

    class Meta:
        model = Expense
        fields = ['group', 'amount', 'description', 'split_method']

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        if 'group' in self.data:
            try:
                group_id = int(self.data.get('group'))
                group = Group.objects.get(id=group_id)

                for member in group.members.all():
                    self.fields[f'split_{member.id}'] = forms.DecimalField(
                        label=f'Split for {member.username}',
                        max_digits=10,
                        decimal_places=2,
                        required=False,
                    )
            except (ValueError, TypeError, Group.DoesNotExist):
                pass
        elif self.instance.pk:
            group = self.instance.group
    
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        group = cleaned_data.get('group')
        split_method = cleaned_data.get('split_method')
        total_split = 0

        if group and split_method == 'custom':
            for member in group.members.all():
                member_split = cleaned_data.get(f'split_{member.id}')
                if member_split:
                    total_split += member_split
            
            if total_split != amount:
                raise forms.ValidationError(
                    f"The sum of custom splits ({total_split}) must equal the total amount ({amount})."
                )

        return cleaned_data

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['expense', 'paid_to', 'amount']
