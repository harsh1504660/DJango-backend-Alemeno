from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('check-eligibility/', views.CheckEligibilityView.as_view(), name='check_eligibility'),
    path('create-loan/', views.CreateLoanView.as_view(), name='create_loan'),
    path('view-loan/<int:loan_id>/', views.ViewLoan.as_view(), name='view_loan'),
    path('view-loans/<int:customer_id>/', views.ViewLoansByCustomer.as_view(), name='view_loans'),
]
