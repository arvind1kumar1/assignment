from django.db import models

# Create your models here.

class BankUsers(models.Model):
    email = models.EmailField(max_length = 150)
    password = models.TextField()
    userType = models.CharField(max_length=10)
    amount = models.IntegerField() #it will be fix amount when user will be created
    class Meta:
        db_table = "bankuser"


class Transactions(models.Model):
    amount = models.IntegerField()
    email = models.EmailField(max_length = 150)
    transactionType = models.CharField(max_length=10) #debit/credit
    date = models.DateTimeField()
    bankUsers = models.ForeignKey(BankUsers, on_delete=models.CASCADE)
    class Meta:
        db_table = "transactions"
