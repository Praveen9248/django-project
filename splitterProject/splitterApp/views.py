from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import GroupForm, ExpenseForm, PaymentForm
from .models import Group, Expense, Payment
from django.contrib import messages

def dashboard(request):
    return render(request, 'dashboard.html')

def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})
    
def GroupDetailView(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    expenses = Expense.objects.filter(group=group)

    # Calculate balances
    balances = {member.id: 0 for member in group.members.all()}
    
    for expense in expenses:
        split_amount = expense.amount / group.members.count()
        balances[expense.payer.id] -= expense.amount  # Payer is owed this amount
        for member in group.members.all():
            if member.id != expense.payer.id:
                balances[member.id] += split_amount  # Non-payers owe this amount

    # Convert balances to be displayed in the template
    # Using a dictionary for quick lookups
    balances_display = {member.id: balances.get(member.id, 0) for member in group.members.all()}

    return render(request, 'group_detail.html', {
        'group': group,
        'expenses': expenses,
        'balances': balances_display,
    })

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.members.add(request.user)
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'create_group.html', {'form': form})

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(group__members=request.user)
    return render(request, 'expense_list.html', {'expenses': expenses})

@login_required
def create_expense(request):
    custom_split_fields = {}
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.payer = request.user  # Set the current user as the payer
            
            group = form.cleaned_data['group']
            split_method = form.cleaned_data['split_method']
            custom_splits = {}

            if split_method == 'equal':
                equal_split = form.cleaned_data['amount'] / group.members.count()
                for member in group.members.all():
                    custom_splits[member.id] = equal_split
            else:
                for member in group.members.all():
                    split_amount = form.cleaned_data.get(f'split_{member.id}')
                    if split_amount:
                        custom_splits[member.id] = split_amount

            expense.custom_splits = custom_splits
            expense.save()
            messages.success(request, 'Expense created successfully!')
            return redirect('group_detail', group_id=expense.group.id)
    else:
        form = ExpenseForm()
        if 'group' in request.GET:
            group_id = int(request.GET.get('group'))
            group = Group.objects.get(id=group_id)
            for member in group.members.all():
                custom_split_fields[member.id] = 0
    
    return render(request, 'create_expense.html', {'form': form, 'custom_split_fields': custom_split_fields})

@login_required
def payment_list(request):
    payments = Payment.objects.filter(paid_by=request.user)
    return render(request, 'payment_list.html', {'payments': payments})

@login_required
def create_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.paid_by = request.user
            payment.save()
            return redirect('payment_list')
    else:
        form = PaymentForm()
    return render(request, 'create_payment.html', {'form': form})

@login_required
def settle_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.paid_by == request.user:
        payment.settled = True
        payment.save()
    return redirect('payment_list')


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

import csv

def export_payments_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments.csv"'

    writer = csv.writer(response)
    writer.writerow(['Paid By', 'Amount', 'Paid To', 'Settled'])

    payments = Payment.objects.all()
    for payment in payments:
        writer.writerow([payment.paid_by.username, payment.amount, payment.paid_to.username, payment.settled])

    return response

