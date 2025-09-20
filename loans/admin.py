from django.contrib import admin
from .models import Customer, Loan, PastLoan
admin.site.register(Customer)
admin.site.register(Loan)
admin.site.register(PastLoan)
