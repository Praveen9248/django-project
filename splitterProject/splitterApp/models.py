import jsonfield
from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='groups_members')

    def __str__(self):
        return self.name

class Expense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    payer = models.ForeignKey(User, related_name='expenses_paid', on_delete=models.CASCADE, default=1)  # Add this line
    custom_splits = jsonfield.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.description} - {self.amount} "

class Payment(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    paid_by = models.ForeignKey(User, related_name='payments', on_delete=models.CASCADE)
    paid_to = models.ForeignKey(User, related_name='receivables', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    settled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.paid_by} paid {self.amount} to {self.paid_to}"
