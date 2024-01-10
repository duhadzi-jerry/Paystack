from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
import datetime
import requests
# Create your views here.

def home(request):  
    return render(request, 'core/home.html')

def pay(request, pk):
    email = 'davidson@gmail.com'
    api_key = 'API_KEY_HERE'
    base_url = 'https://api.paystack.co/'

    amount = float(pk) * 100
    currency = 'GHS'
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    payload = {
        'amount': amount,
        'email': email,
        'currency': currency,
        'callback_url': request.build_absolute_uri(reverse('paystack_callback')),
    }

    response = requests.post(
        f'{base_url}transaction/initialize',
        json=payload,
        headers={'Authorization': f'Bearer {api_key}'}
    )

    if response.status_code == 200:
        data = response.json()
        authorization_url = data['data']['authorization_url']
        return redirect(authorization_url)
    else:
        error_message = response.json()['message']
        messages.error(request, f'Error: {error_message}')
        return redirect('home')

def paystack_callback(request):
    reference = request.GET.get('reference')
    api_key = 'API_KEY_HERE'
    base_url = 'https://api.paystack.co/'
    verify_url = f'{base_url}transaction/verify/{reference}'
    verify_response = requests.get(verify_url, headers={'Authorization': f'Bearer {api_key}'})

    if verify_response.status_code == 200:
        verification_data = verify_response.json()
        status = verification_data['data']['status']

        if status == 'success':
            messages.success(request, 'Payment successful')
            return redirect('home')
        else:
            messages.error(request, 'Payment failed')
            return redirect('home')
    else:
        messages.error(request, 'Transaction verification failed')
        return redirect('home')