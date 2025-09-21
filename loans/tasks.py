from celery import shared_task
from django.db import transaction
from loans.models import Customer, PastLoan
import pandas as pd
import os
from datetime import datetime

@shared_task
def ingest_initial_data_task():
    cust_path = '/data/customer_data.xlsx'
    loan_path = '/data/loan_data.xlsx'
    results = {'customers': 0, 'past_loans': 0}

    try:
        # --- Ingest Customers ---
        if os.path.exists(cust_path):
            df = pd.read_excel(cust_path)

            for _, row in df.iterrows():
                phone = None
                if pd.notna(row.get('phone_number')):
                    try:
                        phone = str(int(row.get('phone_number')))
                    except Exception:
                        phone = str(row.get('phone_number'))

                monthly_income = (
                    row.get('monthly_income')
                    or row.get('monthly_salary')
                    or 0
                )
                approved_limit = (
                    row.get('approved_limit')
                    if pd.notna(row.get('approved_limit'))
                    else 0
                )

                with transaction.atomic():
                    Customer.objects.create(
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                        age=row.get('age') if pd.notna(row.get('age')) else None,
                        phone_number=phone,
                        monthly_income=monthly_income,
                        approved_limit=approved_limit,
                        current_debt=row.get('current_debt') if pd.notna(row.get('current_debt')) else 0
                    )
                    results['customers'] += 1

        # --- Ingest Past Loans ---
        if os.path.exists(loan_path):
            df2 = pd.read_excel(loan_path)

            for _, row in df2.iterrows():
                with transaction.atomic():
                    PastLoan.objects.create(
                        customer_identifier=str(
                            row.get('customer id')
                            or row.get('customer_id')
                            or ''
                        ),
                        loan_id=str(row.get('loan id') or row.get('loan_id') or ''),
                        loan_amount=row.get('loan amount') or row.get('loan_amount') or 0,
                        tenure=int(row.get('tenure') or 0),
                        interest_rate=row.get('interest rate') or row.get('interest_rate') or 0,
                        monthly_repayment=row.get('monthly repayment') or row.get('monthly_repayment') or 0,
                        emis_paid_on_time=int(
                            row.get('EMIs paid on time')
                            or row.get('emis_paid_on_time')
                            or 0
                        ),
                        start_date=_safe_parse(row.get('start date')),
                        end_date=_safe_parse(row.get('end date'))
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
