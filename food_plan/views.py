from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from functools import wraps


def index(request):
	return render(request, 'index.html')


def authentication(request):
	return render(request, 'auth.html')


def card(request):
	return render(request, 'card.html')


@login_required
def lk(request):
	return render(request, 'lk.html')


def order(request):
	return render(request, 'order.html')


def registration(request):
	return render(request, 'registration.html')


@login_required
def pay(request):
	return render(request, 'pay.html')


def sign_up(request, context={}):
	if request.method == 'POST':
		name = request.POST['name']
		email = request.POST['email']
		password = request.POST['password']
		confirm_password = request.POST['PasswordConfirm']

		if User.objects.filter(email=email).exists():
			context['error'] = """Такой пользователь уже зарегистрирован.
			Если вы не помните свой пароль,
			сделайте, пожалуйста, запрос на восстановление."""
			return render(request, 'registration.html', context)
		elif password == confirm_password:
			user = User.objects.create_user(
				first_name=name,
				username=email,
				email=email,
				password=password,
			)
			login(request, user)
			return redirect('lk')
		else:
			context['error'] = """Пароли не совпадают.
			Пожалуйста, попробуйте снова."""
			return render(request, 'registration.html', context)
	else:
		context['error'] = 'Ошибка: неверный тип запроса.'
		return render(request, 'registration.html', context)


def sign_in(request, context={}):
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')

		user = auth.authenticate(username=email, password=password)

		if user is not None:
			auth.login(request, user)
			return redirect('lk')
		else:
			context['error'] = 'Неверный логин или пароль'
			return render(request, 'auth.html', context)
	else:
		context['error'] = 'Ошибка: неверный тип запроса.'
		return render(request, 'auth.html', context)


def sign_out(request):
	logout(request)
	return redirect('main_page')
