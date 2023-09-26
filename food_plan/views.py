from django.shortcuts import render, redirect


def index(request):
	return render(request, 'index.html')


def auth(request):
	return render(request, 'auth.html')


def card(request):
	return render(request, 'card.html')


def lk(request):
	return render(request, 'lk.html')


def order(request):
	return render(request, 'order.html')


def registration(request):
	return render(request, 'registration.html')


def login(request):
	return redirect('lk')


def logout(request):
	return redirect('main_page')


def pay(request):
	return render(request, 'pay.html')

