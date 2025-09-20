import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_customer(api_client):
    url = reverse("register")
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "phone_number": "9998887777",
        "monthly_income": 50000.0
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code in (200, 201)
    data = response.json()
    assert "customer_id" in data


@pytest.mark.django_db
def test_check_eligibility(api_client):
    # first register customer
    reg_url = reverse("register")
    customer = api_client.post(reg_url, {
        "first_name": "Alice",
        "last_name": "Smith",
        "age": 28,
        "phone_number": "9991234567",
        "monthly_income": 60000.0
    }, format="json").json()

    url = reverse("check_eligibility")
    payload = {
        "customer_id": customer["customer_id"],
        "loan_amount": 200000,
        "interest_rate": 12,
        "tenure": 12
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 200
    data = response.json()
    assert "approval" in data  # should return approved/rejected


@pytest.mark.django_db
def test_create_and_view_loan(api_client):
    # register customer
    reg_url = reverse("register")
    customer = api_client.post(reg_url, {
        "first_name": "Bob",
        "last_name": "Marley",
        "age": 35,
        "phone_number": "9995554444",
        "monthly_income": 70000.0
    }, format="json").json()

    # create loan
    url = reverse("create_loan")
    payload = {
        "customer_id": customer["customer_id"],
        "loan_amount": 100000,
        "interest_rate": 12,
        "tenure": 12
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code in (200, 201)  # accept both, but 201 is expected
    loan = response.json()
    assert "loan_id" in loan

    # view loan details
    loan_url = reverse("view_loan", args=[loan["loan_id"]])
    response = api_client.get(loan_url)
    assert response.status_code == 200
    loan_details = response.json()
    assert loan_details["loan_id"] == loan["loan_id"]

    # view all loans of customer
    all_loans_url = reverse("view_loans", args=[customer["customer_id"]])
    response = api_client.get(all_loans_url)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(l["loan_id"] == loan["loan_id"] for l in data)
