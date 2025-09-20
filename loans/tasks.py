from celery import shared_task
import pandas as pd
import os
from .models import Customer, PastLoan
from datetime import datetime
from django.db import transaction

@shared_task
def ingest_initial_data_task():
    # look for files at /data/customer_data.xlsx and /data/loan_data.xlsx
    cust_path = '/data/customer_data.xlsx'
    loan_path = '/data/loan_data.xlsx'
    results = {'customers':0,'past_loans':0}
    try:
        if os.path.exists(cust_path):
            df = pd.read_excel(cust_path)
            for _, row in df.iterrows():
                # safe create or update by phone_number or customer_id if present
                phone = str(int(row.get('phone_number'))) if not pd.isna(row.get('phone_number')) else None
                approved_limit = row.get('approved_limit') if not pd.isna(row.get('approved_limit')) else 0
                with transaction.atomic():
                    Customer.objects.update_or_create(
                        phone_number=phone,
                        defaults={
                            'first_name': row.get('first_name',''),
                            'last_name': row.get('last_name',''),
                            'monthly_income': row.get('monthly_salary') if not pd.isna(row.get('monthly_salary')) else row.get('monthly_income',0),
                            'approved_limit': approved_limit,
                            'current_debt': row.get('current_debt') if not pd.isna(row.get('current_debt')) else 0
                        }
                    )
                    results['customers'] += 1
        if os.path.exists(loan_path):
            df2 = pd.read_excel(loan_path)
            for _, row in df2.iterrows():
                with transaction.atomic():
                    PastLoan.objects.update_or_create(
                        customer_identifier=str(row.get('customer id') or row.get('customer_id') or ''),
                        loan_id=str(row.get('loan id') or row.get('loan_id') or ''),
                        defaults={
                            'loan_amount': row.get('loan amount') or row.get('loan_amount') or 0,
                            'tenure': int(row.get('tenure') or 0),
                            'interest_rate': row.get('interest rate') or row.get('interest_rate') or 0,
                            'monthly_repayment': row.get('monthly repayment') or row.get('monthly_repayment') or 0,
                            'emis_paid_on_time': int(row.get('EMIs paid on time') or row.get('emis_paid_on_time') or 0),
                            'start_date': _safe_parse(row.get('start date')),
                            'end_date': _safe_parse(row.get('end date'))
                        }
                    )
                    results['past_loans'] += 1
    except Exception as e:
        return {'error': str(e)}
    return results

def _safe_parse(val):
    try:
        if pd.isna(val):
            return None
        if isinstance(val, datetime):
            return val.date()
        return pd.to_datetime(val).date()
    except Exception:
        return None
