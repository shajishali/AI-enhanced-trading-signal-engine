from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.backends import ModelBackend
from allauth.socialaccount.models import SocialAccount
from .models import SubscriptionPlan, UserProfile, Payment, SubscriptionHistory
import json

def signup_view(request):
    """Landing page with social login options and traditional signup"""
    if request.user.is_authenticated:
        return redirect('subscription:subscription_choice')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify the authentication backend explicitly
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully! Please choose your subscription plan.')
            return redirect('subscription:subscription_choice')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'subscription/signup.html', {'form': form})

@login_required
def subscription_choice(request):
    """Show subscription options after login/signup"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get available plans
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    context = {
        'plans': plans,
        'user_profile': profile,
    }
    return render(request, 'subscription/subscription_choice.html', context)

@login_required
def start_trial(request):
    """Start free trial for user"""
    if request.method == 'POST':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Check if user already had a trial
        if profile.subscription_status != 'inactive':
            messages.error(request, 'You have already used your trial period.')
            return redirect('subscription:subscription_choice')
        
        # Get free plan
        free_plan = get_object_or_404(SubscriptionPlan, tier='free')
        
        # Set up trial
        profile.subscription_plan = free_plan
        profile.subscription_status = 'trial'
        profile.subscription_start_date = timezone.now()
        profile.trial_end_date = timezone.now() + timezone.timedelta(days=free_plan.trial_days)
        profile.save()
        
        # Record subscription history
        SubscriptionHistory.objects.create(
            user=request.user,
            new_plan=free_plan,
            action='created'
        )
        
        messages.success(request, f'Free trial started! You have {free_plan.trial_days} days to explore all features.')
        return redirect('dashboard:home')
    
    return redirect('subscription:subscription_choice')

@login_required
def upgrade_subscription(request, plan_id):
    """Upgrade user subscription"""
    if request.method == 'POST':
        plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        old_plan = profile.subscription_plan
        
        # Update subscription
        profile.subscription_plan = plan
        profile.subscription_status = 'active'
        profile.subscription_start_date = timezone.now()
        
        # Set end date based on billing cycle
        if plan.billing_cycle == 'monthly':
            profile.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
        else:  # yearly
            profile.subscription_end_date = timezone.now() + timezone.timedelta(days=365)
        
        profile.save()
        
        # Record subscription history
        SubscriptionHistory.objects.create(
            user=request.user,
            old_plan=old_plan,
            new_plan=plan,
            action='upgraded' if old_plan else 'created'
        )
        
        messages.success(request, f'Successfully upgraded to {plan.name}!')
        return redirect('dashboard:home')
    
    return redirect('subscription:subscription_choice')

@login_required
def subscription_management(request):
    """User subscription management page"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    
    # Get subscription history
    history = SubscriptionHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    # Get payment history
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'user_profile': profile,
        'plans': plans,
        'history': history,
        'payments': payments,
    }
    return render(request, 'subscription/management.html', context)

@login_required
def cancel_subscription(request):
    """Cancel user subscription"""
    if request.method == 'POST':
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if profile.subscription_status in ['active', 'trial']:
            old_plan = profile.subscription_plan
            profile.subscription_status = 'cancelled'
            profile.save()
            
            # Record subscription history
            SubscriptionHistory.objects.create(
                user=request.user,
                old_plan=old_plan,
                action='cancelled'
            )
            
            messages.success(request, 'Your subscription has been cancelled.')
        else:
            messages.error(request, 'No active subscription to cancel.')
    
    return redirect('subscription:subscription_management')

@csrf_exempt
def webhook_stripe(request):
    """Handle Stripe webhooks for payment processing"""
    if request.method == 'POST':
        try:
            # This is a simplified webhook handler
            # In production, you would verify the webhook signature
            data = json.loads(request.body)
            
            # Handle different webhook events
            event_type = data.get('type')
            
            if event_type == 'payment_intent.succeeded':
                # Handle successful payment
                payment_intent = data['data']['object']
                user_id = payment_intent['metadata'].get('user_id')
                plan_id = payment_intent['metadata'].get('plan_id')
                
                if user_id and plan_id:
                    user = User.objects.get(id=user_id)
                    plan = SubscriptionPlan.objects.get(id=plan_id)
                    
                    # Create payment record
                    Payment.objects.create(
                        user=user,
                        subscription_plan=plan,
                        amount=payment_intent['amount'] / 100,  # Convert from cents
                        currency=payment_intent['currency'].upper(),
                        status='completed',
                        provider='stripe',
                        provider_payment_id=payment_intent['id'],
                        metadata=data
                    )
                    
                    # Update user subscription
                    profile, created = UserProfile.objects.get_or_create(user=user)
                    profile.subscription_plan = plan
                    profile.subscription_status = 'active'
                    profile.subscription_start_date = timezone.now()
                    
                    if plan.billing_cycle == 'monthly':
                        profile.subscription_end_date = timezone.now() + timezone.timedelta(days=30)
                    else:
                        profile.subscription_end_date = timezone.now() + timezone.timedelta(days=365)
                    
                    profile.save()
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def social_signup_callback(request):
    """Handle post-social-login flow"""
    if request.user.is_authenticated:
        # Check if user has profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Update social auth info if available
        social_accounts = SocialAccount.objects.filter(user=request.user)
        if social_accounts.exists():
            social_account = social_accounts.first()
            profile.social_provider = social_account.provider
            profile.social_id = social_account.uid
            
            # Get profile picture if available
            if hasattr(social_account, 'extra_data') and 'picture' in social_account.extra_data:
                profile.profile_picture = social_account.extra_data['picture']
            
            profile.save()
        
        # If user doesn't have an active subscription, redirect to subscription choice
        if not profile.is_subscription_active:
            return redirect('subscription:subscription_choice')
        
        return redirect('dashboard:home')
    
    return redirect('subscription:signup')
