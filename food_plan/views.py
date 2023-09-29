import random
import smtplib
import textwrap

from django.views.decorators.csrf import csrf_exempt
from yookassa import Configuration, Payment
import json

from yookassa.domain.notification import WebhookNotificationFactory, WebhookNotificationEventType

from food_plan.settings import SHOP_KEY, SHOP_SECRET_KEY, URL
from home_menu.forms import PhotoUploadForm
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db import DatabaseError, OperationalError
from django.shortcuts import render, redirect

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from home_menu.models import Customer

from functools import wraps
from home_menu.models import Dish, Subscription, Category, Allergy


def show_index(request):
	card_items = Dish.objects.all()
	return render(request, 'index.html', context={
		'card_items': card_items
	})


def show_registration(request):
	return render(request, 'registration.html')


def show_auth(request):
	return render(request, 'auth.html')


def show_recovery(request):
	return render(request, 'recovery.html')


@login_required
def show_lk(request):
    user = request.user
    context = {
        'first_name': user.first_name,
        'email': user.email,
        'user': user,
    }

    try:
        customer = Customer.objects.get(user=user)
    except Customer.DoesNotExist:
        customer = None

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            if customer:
                form.instance = customer
            else:
                form.instance = Customer(user=user)

            form.save()
            return redirect('lk')

    return render(request, 'lk.html', context)


def show_card(request, card_id):
	card_item = Dish.objects.filter(id=card_id)
	total_calories = sum([product.weight for dish in card_item for product in dish.product.all()])
	return render(request, 'card.html', context={
		'card_item': card_item,
		'total_calories': total_calories
	})


def show_order(request):
	if request.method == 'POST':
		persons = request.POST.get('select5')
		number_meals = sum([int(request.POST.get(f'select{i}', 0)) for i in range(1, 5)])
		type_food = request.POST.get('foodtype')
		allergy_keys = ['allergy1', 'allergy2', 'allergy3', 'allergy4', 'allergy5', 'allergy6']
		allergies = [request.POST.get(key) for key in allergy_keys if request.POST.get(key)]
		validity = request.POST.get('select')
		prices = {
			'1 мес.': 1000,
			'3 мес.': 2750,
			'6 мес.': 5500,
			'12 мес.': 11000
		}
		descriptions = {
			'Классическое': 'Вкусное и привычное сочетание блюд для тех, кто ценит традиционный вкус. Наши классические блюда подходят для всех возрастов и вкусов, идеальный выбор для тех, кто ищет знакомый вкус и удовольствие от еды.',
			'Низкоуглеводное': 'Забота о здоровье и фигуре начинается с того, что вы едите. Наше низкоуглеводное меню предлагает легкие и вкусные блюда, богатые белками и низким содержанием углеводов. Оно идеально подходит для тех, кто следит за своим уровнем углеводов.',
			'Вегетарианское': 'Наслаждайтесь вкусом и питательностью растительных блюд. Наше вегетарианское меню предлагает разнообразные варианты без мяса, но полные вкуса. От свежих салатов до креативных вегетарианских блюд - у нас есть что-то для каждого вегетарианца.',
			'Кето': 'Для тех, кто придерживается диеты с низким содержанием углеводов и высоким содержанием жиров. Наше кето-меню предлагает богатые вкусом блюда, которые помогут вам достичь ваших целей в отношении питания, сохраняя при этом уровень углеводов на минимальном уровне.'
		}
		description = descriptions.get(type_food)
		price = prices.get(validity, 0)
		total_amount = int(persons) * int(number_meals) * int(price)
		temporary_calorie_value = 1400  # Связать логику Dish и Subscription
		try:
			type_dish = Category.objects.get(title=type_food)
			order, created = Subscription.objects.get_or_create(
				title=f'{type_food} на {validity}',
				description=description,
				persons=persons,
				calories=temporary_calorie_value,
				number_meals=number_meals,
				price=total_amount,
				type_dish=type_dish,
				# promo_code=promo_code,
			)
			if allergies:
				allergies_objects = Allergy.objects.filter(id__in=allergies)
				order.allergy.set(allergies_objects)
			if created:
				pass  # TODO Заглушка для вывода окна об успешной подписке!
		except (DatabaseError, OperationalError) as e:
			return JsonResponse({'error': str(e)}, status=500)
	return render(request, 'order.html')


def show_privacy_policy(request):
	return render(request, 'privacy.html')


def show_terms_of_use(request):
	return render(request, 'terms.html')


@login_required
def pay(request):
	Configuration.configure(SHOP_KEY, SHOP_SECRET_KEY)
	payment = Payment.create({
		"amount": {
			"value": 1000,
		"currency": "RUB"
	},
		"payment_method_data": {
		"type": "bank_card"
	},
	"confirmation": {
		"type": "redirect",
		"return_url": URL
	},
	"metadata": {
		"user_id": 15,
		"subscription_id": 120,
	},
	"capture": True,
	"description": 'Оплата подписки'
	})
	return HttpResponseRedirect(payment.confirmation.confirmation_url)
	# return render(request, 'pay.html')


@csrf_exempt
def status_pay(request):
	event_json = json.loads(request.body)
	try:
		# Создание объекта класса уведомлений в зависимости от события
		notification_object = WebhookNotificationFactory().create(event_json)
		response_object = notification_object.object
		if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
			some_data = {
				'paymentId': response_object.id,
				'paymentStatus': response_object.status,
			}
			# metadata = response_object.json()['metadata']
			# print(metadata)
			# user_id = metadata['user_id']
			# subscription_id = metadata['subscription_id']
			# print(user_id, subscription_id)
			# if response_object.json()['metadata']:
			# 	print(response_object.json()['metadata'])
			for x in response_object.json():
				print(x)
			print(response_object.json())
			print('PAYMENT_SUCCEEDED')
		# Специфичная логика
		# ...
		elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
			some_data = {
				'paymentId': response_object.id,
				'paymentStatus': response_object.status,
			}
			print('PAYMENT_CANCELED')
		# Специфичная логика
		# ...
		elif notification_object.event == WebhookNotificationEventType.DEAL_CLOSED:
			some_data = {
				'dealId': response_object.id,
				'dealStatus': response_object.status,
			}
		# Специфичная логика
		else:
			# Обработка ошибок
			return HttpResponse(status=400)  # Сообщаем кассе об ошибке

		Configuration.configure(SHOP_KEY, SHOP_SECRET_KEY)
		# Получим актуальную информацию о платеже
		payment_info = Payment.find_one(some_data['paymentId'])
		if payment_info:
			payment_status = payment_info.status
			print(f'{payment_status=}')
		# Специфичная логика
		# ...
		else:
			# Обработка ошибок
			return HttpResponse(status=400)  # Сообщаем кассе об ошибке

	except Exception:
		# Обработка ошибок
		return HttpResponse(status=400)  # Сообщаем кассе об ошибке
	return HttpResponse(status=200)  # Сообщаем кассе, что все хорошо


def sign_up(request, context={}):
	if request.method == 'POST':
		name = request.POST['name']
		email = request.POST['email']
		password = request.POST['password']
		password_confirm = request.POST['PasswordConfirm']

		if User.objects.filter(email=email).exists():
			context['error'] = """Такой пользователь уже зарегистрирован.
			Если вы не помните свой пароль,
			сделайте, пожалуйста, запрос на восстановление."""
			return render(request, 'registration.html', context)
		elif password == password_confirm:
			user = User.objects.create_user(
				first_name=name,
				username=email,
				email=email,
				password=password,
			)
			Customer.objects.create(
				user=user,
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


def recover_password(request, context={}):
	if request.method == 'POST':
		receiver_email = request.POST.get('email')

		try:
			user = User.objects.get(username=receiver_email)
		except User.DoesNotExist:
			context['error'] = 'Данный email не зарегистрирован в системе.'
			return render(request, 'recovery.html', context)

		new_password = random.randint(100000, 999999)
		user.set_password(f"{new_password}")
		user.save()
		text = f"""Здравствуйте! Ваш новый пароль: {new_password}.
			Пожалуйста, поменяйте его на более надёжный как можно скорее."""
		formatted_text = textwrap.fill(text, 48)

		try:
			send_email(receiver_email, "Восстановление пароля FoodPlan", formatted_text)
			context['message'] = 'Новый пароль отправлен на указанный email.'
		except Exception as error:
			print('Ошибка при отправке почты:', str(error))

		return render(request, 'auth.html', context)

	else:
		context['error'] = 'Ошибка: неверный тип запроса.'
		return render(request, 'recovery.html', context)


def send_email(receiver_email, subject, text):
	sender_email = settings.SENDER_EMAIL
	sender_password = settings.SENDER_PASSWORD

	smtp_server = 'smtp.yandex.ru'
	smtp_port = 587

	message = MIMEMultipart()
	message['From'] = sender_email
	message['To'] = receiver_email
	message['Subject'] = subject

	message.attach(MIMEText(text, 'plain'))

	server = smtplib.SMTP(smtp_server, smtp_port)
	server.starttls()
	server.login(sender_email, sender_password)
	server.sendmail(sender_email, receiver_email, message.as_string())
	server.quit()


def change_info(request, context={}):
	if request.method == 'POST':
		new_name = request.POST.get('name')
		new_email = request.POST.get('email')
		new_password = request.POST.get('password')
		new_password_confirm = request.POST.get('PasswordConfirm')

		user = request.user

		if user.first_name != new_name:
			user.first_name = new_name
		if user.email != new_email:
			user.email = new_email
		if new_password and new_password == new_password_confirm:
			user.set_password(new_password)

		user.save()
		login(request, user)
		return redirect('lk')
	else:
		context['error'] = 'Ошибка: неверный тип запроса.'
		return render(request, 'lk.html', context)
