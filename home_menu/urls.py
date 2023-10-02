from django.urls import path
from home_menu import views


urlpatterns = [
    path('', views.show_index, name="main_page"),
    path('auth/', views.show_auth, name="authentication"),
    path('card/<int:card_id>', views.show_card, name="card"),
    path('lk/', views.show_lk, name="lk"),
    path('order/', views.show_order, name="order"),
    path('registration/', views.show_registration, name="registration"),
    path('checkout/', views.checkout, name="checkout"),
    path('use_promo_code/', views.use_promo_code, name="use_promo_code"),
    path('pay/', views.pay, name="pay"),
    path('status_pay/', views.status_pay, name="status_pay"),
    path('sign_up/', views.sign_up, name="sign_up"),
    path('sign_in/', views.sign_in, name="sign_in"),
    path('sign_out/', views.sign_out, name="sign_out"),
    path('recovery/', views.show_recovery, name="recovery"),
    path('recover_password/', views.recover_password, name="recover_password"),
    path('privacy_policy/', views.show_privacy_policy, name="privacy"),
    path('terms_of_use/', views.show_terms_of_use, name="terms"),
    path('change_info/', views.change_info, name="change_info"),
]
