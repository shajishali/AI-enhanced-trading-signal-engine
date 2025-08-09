from django.urls import path
from . import views

app_name = 'subscription'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('choice/', views.subscription_choice, name='subscription_choice'),
    path('trial/', views.start_trial, name='start_trial'),
    path('upgrade/<int:plan_id>/', views.upgrade_subscription, name='upgrade_subscription'),
    path('management/', views.subscription_management, name='subscription_management'),
    path('cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('webhook/stripe/', views.webhook_stripe, name='webhook_stripe'),
    path('social-callback/', views.social_signup_callback, name='social_signup_callback'),
]

