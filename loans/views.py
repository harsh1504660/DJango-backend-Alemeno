from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan, PastLoan
from .serializers import RegisterSerializer, CheckEligibilitySerializer, CreateLoanSerializer, LoanSerializer, CustomerSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Sum
import math
from datetime import date, timedelta
from .tasks import ingest_initial_data_task

# helper: compound interest monthly installment formula
def monthly_installment(principal, annual_rate_percent, months):
    r = annual_rate_percent / 100.0 / 12.0
    if r == 0:
        return principal / months
    return principal * (r * (1 + r) ** months) / ((1 + r) ** months - 1)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        approved = 36 * data['monthly_income']
        # round to nearest lakh (100000)
        approved = round(approved / 100000.0) * 100000.0
        customer = Customer.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data['age'],
            monthly_income=data['monthly_income'],
            phone_number=data['phone_number'],
            approved_limit=approved
        )
        # kick off ingestion in background if not already run (best-effort)
        try:
            ingest_initial_data_task.delay()
        except Exception:
            pass
        out = {
            "customer_id": customer.id,
            "name": f"{customer.first_name} {customer.last_name}",
            "age": customer.age,
            "monthly_income": customer.monthly_income,
            "approved_limit": customer.approved_limit,
            "phone_number": customer.phone_number
        }
        return Response(out, status=status.HTTP_201_CREATED)

class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = CheckEligibilitySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        customer = get_object_or_404(Customer, id=data['customer_id'])
        # compute sum of current loans' monthly_installment
        current_emis_sum = Loan.objects.filter(customer=customer).aggregate(sum=Sum('monthly_installment'))['sum'] or 0
        if current_emis_sum > 0.5 * customer.monthly_income:
            return Response({
                "customer_id": customer.id,
                "approval": False,
                "interest_rate": data['interest_rate'],
                "corrected_interest_rate": data['interest_rate'],
                "tenure": data['tenure'],
                "monthly_installment": None,
                "message": "Total EMIs exceed 50% of monthly income"
            }, status=status.HTTP_200_OK)
        # if sum of current loans > approved limit -> score 0
        total_current_loans = Loan.objects.filter(customer=customer).aggregate(total=Sum('loan_amount'))['total'] or 0
        if total_current_loans > customer.approved_limit:
            score = 0
        else:
            # simple scoring using PastLoan table
            past = PastLoan.objects.filter(customer_identifier=str(customer.id))
            total_past = past.count()
            ontime = past.aggregate(sum_on=Sum('emis_paid_on_time'))['sum_on'] or 0
            # components
            score = 50
            # past loans paid on time ratio
            if total_past > 0:
                ratio = ontime / (total_past * 1.0)
                score += min(20, ratio * 20)
            # fewer loans => bonus
            if total_past <=2:
                score += 10
            # loan activity in current year
            this_year = date.today().year
            active = past.filter(start_date__year=this_year).count()
            if active>0:
                score -= active*5
            # loan approved volume relative to approved_limit
            if customer.approved_limit>0:
                vol = (total_current_loans / customer.approved_limit) * 20
                score -= min(20, vol)
            score = max(0, min(100, int(score)))
        # decide interest slab
        corrected_rate = data['interest_rate']
        approved = False
        if score > 50:
            approved = True
        elif 30 < score <= 50:
            if data['interest_rate'] > 12:
                approved = True
            else:
                corrected_rate = 12.0
        elif 10 < score <= 30:
            if data['interest_rate'] > 16:
                approved = True
            else:
                corrected_rate = 16.0
        else:
            approved = False
        # monthly installment with corrected rate
        mi = monthly_installment(data['loan_amount'], corrected_rate, data['tenure'])
        return Response({
            "customer_id": customer.id,
            "approval": bool(approved),
            "interest_rate": data['interest_rate'],
            "corrected_interest_rate": float(corrected_rate),
            "tenure": data['tenure'],
            "monthly_installment": round(mi,2),
            "credit_score": score
        }, status=status.HTTP_200_OK)

class CreateLoanView(APIView):
    def post(self, request):
        serializer = CreateLoanSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data
        # reuse eligibility logic
        from .views import CheckEligibilityView
        # create a fake request dict
        eligibility_view = CheckEligibilityView()
        fake_req = type('R',(object,),{'data':data})
        resp = eligibility_view.post(fake_req)
        resp_data = resp.data
        if not resp_data.get('approval'):
            return Response({
                "loan_id": None,
                "customer_id": data['customer_id'],
                "loan_approved": False,
                "message": resp_data.get('message','Not approved'),
                "monthly_installment": resp_data.get('monthly_installment')
            }, status=status.HTTP_200_OK)
        # approve loan -> create Loan
        customer = get_object_or_404(Customer, id=data['customer_id'])
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=data['loan_amount'],
            interest_rate=resp_data['corrected_interest_rate'],
            tenure=data['tenure'],
            monthly_installment=resp_data['monthly_installment'],
            start_date=date.today(),
            end_date=(date.today() + timedelta(days=30*data['tenure']))
        )
        # update customer's current_debt
        customer.current_debt = (Loan.objects.filter(customer=customer).aggregate(total=Sum('loan_amount'))['total'] or 0)
        customer.save()
        return Response({
            "loan_id": loan.id,
            "customer_id": customer.id,
            "loan_approved": True,
            "message": "Loan approved",
            "monthly_installment": round(loan.monthly_installment,2)
        }, status=status.HTTP_201_CREATED)

class ViewLoan(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, id=loan_id)
        cust = loan.customer
        customer_json = {
            "id": cust.id,
            "first_name": cust.first_name,
            "last_name": cust.last_name,
            "phone_number": cust.phone_number,
            "age": cust.age
        }
        return Response({
            "loan_id": loan.id,
            "customer": customer_json,
            "loan_amount": loan.loan_amount,
            "interest_rate": loan.interest_rate,
            "monthly_installment": loan.monthly_installment,
            "tenure": loan.tenure
        }, status=status.HTTP_200_OK)

class ViewLoansByCustomer(APIView):
    def get(self, request, customer_id):
        cust = get_object_or_404(Customer, id=customer_id)
        loans = cust.loans.all()
        out = []
        for loan in loans:
            # calculate repayments left naively
            total_months = loan.tenure
            paid = loan.emIs_paid or 0
            left = max(0, total_months - paid)
            out.append({
                "loan_id": loan.id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_installment,
                "repayments_left": left
            })
        return Response(out, status=status.HTTP_200_OK)
