import json
import random
import smtplib
import textwrap

from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationFactory, WebhookNotificationEventType
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.db import DatabaseError, OperationalError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Sum
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from food_plan.settings import SHOP_KEY, SHOP_SECRET_KEY, SHOP_REDIRECT_URL
from home_menu.forms import PhotoUploadForm
from home_menu.models import (
    Customer,
    Dish,
    Subscription,
    Category,
    Allergy,
)


def save_to_cookies(request, key, payload):
    request.session[key] = payload
    request.session.modified = True
    response = HttpResponse("Your choice was saved as a cookie!")
    response.set_cookie('session_id', request.session.session_key)
    return response


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
    customer, _ = Customer.objects.get_or_create(user=user)
    subscriptions = Subscription.objects.filter(
        customer=customer,
        status=Subscription.ChoicesStatus.Paid
    )

    context = {
        'first_name': user.first_name,
        'email': user.email,
        'user': user,
        'subscriptions': subscriptions,
    }

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.instance = customer
            form.save()
            return redirect('lk')

    return render(request, 'lk.html', context)


def show_card(request, card_id):
    card_item = Dish.objects.filter(id=card_id)
    total_calories = sum(
        [product.weight for item in card_item for product in item.product.all()]
    )
    return render(request, 'card.html', context={
        'card_item': card_item,
        'total_calories': total_calories
    })


def show_subscription(request, subscription_id):
    subscription_item = Subscription.objects.filter(id=subscription_id)
    total_calories_per_dish = []
    for subscription in subscription_item:
        for dish in subscription.dish.all():
            total_calories = sum(
                [product.weight for product in dish.product.all()]
            )
            total_calories_per_dish.append(total_calories)
    total_calories_per_dish.reverse()
    return render(request, 'subscription.html', context={
        'subscription_item': subscription_item,
        'total_calories_per_dish': total_calories_per_dish,
    })


def show_order(request):
    context = {
        "one_month_price": settings.ONE_MONTH_PRICE,
        "three_months_price": settings.THREE_MONTHS_PRICE,
        "six_months_price": settings.SIX_MONTHS_PRICE,
        "twelve_months_price": settings.TWELVE_MONTHS_PRICE,
        "discount": settings.DISCOUNT,
    }
    return render(request, 'order.html', context)


def show_privacy_policy(request):
    return render(request, 'privacy.html')


def show_terms_of_use(request):
    return render(request, 'terms.html')


def checkout(request):
    if request.method == 'POST':
        for name, value in request.POST.items():
            save_to_cookies(request, name, value)
        del request.session['csrfmiddlewaretoken']
        save_to_cookies(request, 'checkout', True)
    elif request.session.get('checkout'):
        pass
    else:
        return render(request, 'order.html')

    if str(request.user) == "AnonymousUser":
        return redirect('authentication')
    try:
        total_amount = create_subscription(request)
        if type(total_amount) is int:
            save_to_cookies(request, "total_amount", total_amount)
        else:
            redirect('order')
    except:
        redirect('order')

    return redirect('pay')


def use_promo_code(request):
    promo_codes = {}  # TODO Promocode model
    promo_code = None
    if request.method == 'POST':
        promo_code = request.POST.get('promo_code')
    if promo_code and promo_codes.get(promo_code):
        discount = promo_codes.get(promo_code)
    else:
        discount = settings.DISCOUNT
    context = {
        "one_month_price": settings.ONE_MONTH_PRICE,
        "three_months_price": settings.THREE_MONTHS_PRICE,
        "six_months_price": settings.SIX_MONTHS_PRICE,
        "twelve_months_price": settings.TWELVE_MONTHS_PRICE,
        "discount": discount,
    }
    return render(request, 'order.html', context)


def create_subscription(request):
    customer = Customer.objects.get(user=request.user)
    persons = request.session.get('select5')
    number_meals = sum(
        [int(request.session.get(f'select{i}', 0)) for i in range(1, 5)]
    )
    type_food = request.session.get('foodtype')
    allergy_keys = [
        'allergy1',
        'allergy2',
        'allergy3',
        'allergy4',
        'allergy5',
        'allergy6',
    ]
    allergies = [
        request.session.get(key) for key in allergy_keys if request.session.get(key)
    ]
    validity = request.session.get('select')
    descriptions = {
        'Классическое': 'Вкусное и привычное сочетание блюд для тех, кто ценит традиционный вкус. Наши классические блюда подходят для всех возрастов и вкусов, идеальный выбор для тех, кто ищет знакомый вкус и удовольствие от еды.',
        'Низкоуглеводное': 'Забота о здоровье и фигуре начинается с того, что вы едите. Наше низкоуглеводное меню предлагает легкие и вкусные блюда, богатые белками и низким содержанием углеводов. Оно идеально подходит для тех, кто следит за своим уровнем углеводов.',
        'Вегетарианское': 'Наслаждайтесь вкусом и питательностью растительных блюд. Наше вегетарианское меню предлагает разнообразные варианты без мяса, но полные вкуса. От свежих салатов до креативных вегетарианских блюд - у нас есть что-то для каждого вегетарианца.',
        'Кето': 'Для тех, кто придерживается диеты с низким содержанием углеводов и высоким содержанием жиров. Наше кето-меню предлагает богатые вкусом блюда, которые помогут вам достичь ваших целей в отношении питания, сохраняя при этом уровень углеводов на минимальном уровне.'
    }
    description = descriptions.get(type_food)
    total_amount = request.session.get('total_amount')
    filtered_dishes = Dish.objects.exclude(allergy__in=allergies)[:number_meals]
    temporary_calorie_value = sum(
        [product.weight for dish in filtered_dishes for product in dish.product.all()]
    )
    try:
        type_dish = Category.objects.get(title=type_food)
        subscription = Subscription.objects.create(
            customer=customer,
            title=f'{type_food} на {validity}',
            description=description,
            persons=persons,
            calories=temporary_calorie_value,
            number_meals=number_meals,
            price=total_amount,
            type_dish=type_dish,
            # TODO promo_code=promo_code,
        )
        subscription.dish.set(filtered_dishes)
        if allergies:
            allergies_objects = Allergy.objects.filter(id__in=allergies)
            subscription.allergy.set(allergies_objects)

        del request.session['checkout']

        save_to_cookies(request, 'subscription_id', subscription.id)
        return total_amount, subscription.id

    except (DatabaseError, OperationalError) as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def pay(request):
    total_amount = request.session.get('total_amount')
    customer_id = Customer.objects.get(user=request.user).id
    subscription_id = request.session.get('subscription_id')
    Configuration.configure(SHOP_KEY, SHOP_SECRET_KEY)
    payment = Payment.create({
        "amount": {
            "value": total_amount,
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": SHOP_REDIRECT_URL
        },
        "metadata": {
            "customer_id": customer_id,
            "subscription_id": subscription_id,
        },
        "capture": True,
        "description": 'Оплата подписки'
    })
    return HttpResponseRedirect(payment.confirmation.confirmation_url)


@csrf_exempt
def status_pay(request):
    event_json = json.loads(request.body)
    try:
        notification_object = WebhookNotificationFactory().create(event_json)
        response_object = notification_object.object
        if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
            subscription_id = event_json['object']['metadata']['subscription_id']
            subscription = get_object_or_404(Subscription, id=subscription_id)
            subscription.status = "Оплачено"
            subscription.save()
            some_data = {
                'paymentId': response_object.id,
                'paymentStatus': response_object.status,
            }
        elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
            some_data = {
                'paymentId': response_object.id,
                'paymentStatus': response_object.status,
            }
        else:
            return HttpResponse(status=400)

        Configuration.configure(SHOP_KEY, SHOP_SECRET_KEY)
        payment_info = Payment.find_one(some_data['paymentId'])
        if payment_info:
            payment_status = payment_info.status
        else:
            return HttpResponse(status=400)
    except json.JSONDecodeError:
        return HttpResponse(status=400, content="Invalid JSON in request body")
    except Exception as e:
        return HttpResponse(status=500, content=f"An error occurred: {str(e)}")

    return HttpResponse(status=200)


def sign_up(request):
    context = {}
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('PasswordConfirm')

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
            if request.session.get('checkout'):
                return redirect('checkout')
            else:
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
        send_email(
            receiver_email,
            "Восстановление пароля FoodPlan",
            formatted_text
        )
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
