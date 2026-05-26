from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
import secrets
from django.conf import settings
from .models import LostFoundItem, CustomUser, EmailVerificationToken, PasswordResetToken, Claim
from .forms import CustomUserCreationForm, ItemPostForm, ForgotPasswordForm, ResetPasswordForm, ClaimForm, ProfileUpdateForm, AccountPasswordChangeForm


def send_verification_email(user, request):
    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(hours=24)

    EmailVerificationToken.objects.create(
        token=token,
        user=user,
        expires_at=expires_at
    )

    verification_link = request.build_absolute_uri(f'/verify-email/{token}/')
    subject = 'Verify your email - OTU Found'
    message = f"""
Hello {user.first_name},

Thank you for registering at OTU Found! To complete your registration, please verify your email address by clicking the link below:

{verification_link}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
OTU Found Team
    """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_password_reset_email(user, request):
    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(hours=24)

    PasswordResetToken.objects.create(
        token=token,
        user=user,
        expires_at=expires_at
    )

    reset_link = request.build_absolute_uri(f'/reset-password/{token}/')
    subject = 'Reset your password - OTU Found'
    message = f"""
Hello {user.first_name},

You requested to reset your password. Click the link below to create a new password:

{reset_link}

This link will expire in 24 hours.

If you didn't request this, please ignore this email and your password will remain unchanged.

Best regards,
OTU Found Team
    """

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def login_view(request):
    if request.user.is_authenticated:
        return redirect('item_list')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email:
            email = email.strip().lower()
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if not user.is_verified:
                messages.error(request, 'Please verify your email before logging in. Check your inbox for the verification link.')
                return redirect(f"{reverse('resend_verification')}?email={email}")
            login(request, user)
            return redirect('item_list')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'account/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('item_list')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            try:
                send_verification_email(user, request)
            except Exception as e:
                messages.warning(request, f'Account created, but verification email could not be sent: {e}')
                return redirect('account_login')
            return redirect(f"{reverse('verification_sent')}?email={user.email}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'account/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('account_login')


def verify_email_view(request, token):
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('resend_verification')

    if not verification_token.is_valid():
        messages.error(request, 'This verification link has expired. Please request a new one.')
        return redirect('resend_verification')

    user = verification_token.user
    user.is_verified = True
    user.email_verified_at = timezone.now()
    user.save()

    verification_token.is_used = True
    verification_token.save()

    messages.success(request, 'Email verified successfully! You can now login.')
    return redirect('account_login')


def verification_sent_view(request):
    email = request.GET.get('email', '')
    context = {'email': email}
    return render(request, 'items/verification_sent.html', context)


def resend_verification_view(request):
    # Auto-detect unverified email and send automatically
    if request.method == 'GET':
        email = request.GET.get('email')
        if email:
            email = email.strip().lower()
            try:
                user = CustomUser.objects.get(email__iexact=email)
                if not user.is_verified:
                    try:
                        send_verification_email(user, request)
                        messages.success(request, f'Verification email sent automatically to {email}. Please check your inbox.')
                        return redirect(f"{reverse('verification_sent')}?email={email}")
                    except Exception as e:
                        messages.error(request, f'Failed to auto-send email: {e}')
                else:
                    messages.info(request, 'This email is already verified. You can login now.')
                    return redirect('account_login')
            except CustomUser.DoesNotExist:
                pass

    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            email = email.strip().lower()
        try:
            user = CustomUser.objects.get(email__iexact=email)
            if user.is_verified:
                messages.info(request, 'This email is already verified. You can login now.')
                return redirect('account_login')
            try:
                send_verification_email(user, request)
                messages.success(request, f'Verification email sent to {email}. Please check your inbox.')
                return redirect(f"{reverse('verification_sent')}?email={email}")
            except Exception as e:
                messages.error(request, f'Failed to send email: {e}')
                return redirect('resend_verification')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Email not found. Please register first.')
            return redirect('account_signup')
    return render(request, 'items/resend_verification.html')


def forgot_password_view(request):
    if request.user.is_authenticated:
        return redirect('item_list')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email__iexact=email)
            try:
                send_password_reset_email(user, request)
                return redirect(f"{reverse('password_reset_sent')}?email={email}")
            except Exception as e:
                messages.error(request, f'Failed to send password reset email: {e}')
    else:
        form = ForgotPasswordForm()
    return render(request, 'account/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    if request.user.is_authenticated:
        return redirect('item_list')

    try:
        reset_token = PasswordResetToken.objects.get(token=token)
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('account_reset_password')

    if not reset_token.is_valid():
        messages.error(request, 'This password reset link has expired. Please request a new one.')
        return redirect('account_reset_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password1'])
            user.save()

            reset_token.is_used = True
            reset_token.save()

            messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
            return redirect('account_login')
    else:
        form = ResetPasswordForm()

    return render(request, 'account/reset_password.html', {'form': form, 'token': token})


def reset_password_sent_view(request):
    email = request.GET.get('email', '')
    context = {'email': email}
    return render(request, 'account/reset_password_sent.html', context)


def resend_reset_email_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            email = email.strip().lower()
        try:
            user = CustomUser.objects.get(email__iexact=email)
            try:
                send_password_reset_email(user, request)
                messages.success(request, f'Password reset email sent to {email}. Please check your inbox.')
                return redirect(f"{reverse('password_reset_sent')}?email={email}")
            except Exception as e:
                messages.error(request, f'Failed to send email: {e}')
                return redirect('password_reset_sent')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Email not found.')
            return redirect('account_reset_password')
    return redirect('password_reset_sent')



@login_required(login_url='account_login')
def item_list_view(request):
    items = LostFoundItem.objects.all()

    item_type = request.GET.get('type')
    if item_type in ['lost', 'found']:
        items = items.filter(item_type=item_type)

    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)

    context = {
        'items': items,
        'categories': LostFoundItem.CATEGORY_CHOICES,
        'selected_type': item_type,
        'selected_category': category,
    }
    return render(request, 'items/item_list.html', context)


@login_required(login_url='account_login')
def post_item_view(request):
    if request.method == 'POST':
        form = ItemPostForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.posted_by = request.user
            item.save()
            messages.success(request, 'Item posted successfully!')
            return redirect('item_list')
    else:
        form = ItemPostForm()
    return render(request, 'items/post_item.html', {'form': form})


@login_required(login_url='account_login')
def item_detail_view(request, pk):
    item = get_object_or_404(LostFoundItem, pk=pk)
    context = {'item': item}
    if item.posted_by == request.user:
        context['claims'] = item.claims.all()
    else:
        context['user_claim'] = item.claims.filter(claimant=request.user).first()
    return render(request, 'items/item_detail.html', context)


@login_required(login_url='account_login')
def claim_item_view(request, pk):
    item = get_object_or_404(LostFoundItem, pk=pk)
    if item.posted_by == request.user:
        messages.error(request, 'You cannot claim your own item.')
        return redirect('item_detail', pk=pk)

    existing_claim = Claim.objects.filter(item=item, claimant=request.user).first()
    if existing_claim:
        messages.info(request, 'You have already claimed this item.')
        return redirect('item_detail', pk=pk)

    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item = item
            claim.claimant = request.user
            claim.save()
            
            # Update item status to claim_pending
            item.status = 'claim_pending'
            item.save()
            
            messages.success(request, 'Claim submitted successfully!')
            return redirect('item_detail', pk=pk)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.replace("_", " ").capitalize()}: {error}')
    else:
        form = ClaimForm()

    context = {
        'item': item,
        'form': form
    }
    return render(request, 'items/claim_item.html', context)


@login_required(login_url='account_login')
def approve_claim_view(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    if claim.item.posted_by != request.user:
        messages.error(request, 'You can only approve claims for your own items.')
        return redirect('item_list')

    if request.method == 'POST':
        claim.status = 'approved'
        claim.approved_at = timezone.now()
        claim.save()

        # Update item status to resolved
        item = claim.item
        item.status = 'resolved'
        item.save()

        # Reject all other pending claims for this item
        other_claims = item.claims.exclude(pk=claim.pk).filter(status='pending')
        for other_claim in other_claims:
            other_claim.status = 'rejected'
            other_claim.save()

        messages.success(request, 'Claim approved successfully!')
        return redirect('item_detail', pk=item.pk)

    return render(request, 'items/approve_claim.html', {'claim': claim})


@login_required(login_url='account_login')
def reject_claim_view(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    if claim.item.posted_by != request.user:
        messages.error(request, 'You can only reject claims for your own items.')
        return redirect('item_list')

    if request.method == 'POST':
        claim.status = 'rejected'
        claim.save()

        # If there are no other pending claims, revert item status back to open
        item = claim.item
        if not item.claims.filter(status='pending').exists():
            item.status = 'open'
            item.save()

        messages.success(request, 'Claim rejected.')
        return redirect('item_detail', pk=item.pk)

    return render(request, 'items/reject_claim.html', {'claim': claim})


@login_required(login_url='account_login')
def claim_approved_view(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    # Check authorization: user must be the poster or the claimant
    if request.user != claim.item.posted_by and request.user != claim.claimant:
        messages.error(request, 'You are not authorized to view this page.')
        return redirect('item_list')

    if claim.status != 'approved':
        messages.error(request, 'This claim has not been approved.')
        return redirect('item_detail', pk=claim.item.pk)

    return render(request, 'items/claim_approved.html', {'claim': claim})


@login_required(login_url='account_login')
def my_claims_view(request):
    my_claims = Claim.objects.filter(claimant=request.user)
    return render(request, 'items/my_claims.html', {'my_claims': my_claims})


@login_required(login_url='account_login')
def user_items_view(request):
    items = request.user.items.all()
    context = {'items': items}
    return render(request, 'items/my_items.html', context)


@login_required(login_url='account_login')
def edit_item_view(request, pk):
    item = get_object_or_404(LostFoundItem, pk=pk)
    if item.posted_by != request.user:
        messages.error(request, 'You can only edit your own items.')
        return redirect('item_list')

    if request.method == 'POST':
        form = ItemPostForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('item_detail', pk=pk)
    else:
        form = ItemPostForm(instance=item)
    return render(request, 'items/post_item.html', {'form': form, 'is_edit': True})


@login_required(login_url='account_login')
def delete_item_view(request, pk):
    item = get_object_or_404(LostFoundItem, pk=pk)
    if item.posted_by != request.user:
        messages.error(request, 'You can only delete your own items.')
        return redirect('item_list')

    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item deleted successfully!')
        return redirect('item_list')
    return render(request, 'items/delete_item.html', {'item': item})


@login_required(login_url='account_login')
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = ProfileUpdateForm(instance=request.user)

    # Stats for the profile page
    posted_items = request.user.items.count()
    active_items = request.user.items.filter(status='open').count()
    resolved_items = request.user.items.filter(status='resolved').count()
    claims_made = Claim.objects.filter(claimant=request.user).count()
    approved_claims = Claim.objects.filter(claimant=request.user, status='approved').count()

    context = {
        'form': form,
        'posted_items': posted_items,
        'active_items': active_items,
        'resolved_items': resolved_items,
        'claims_made': claims_made,
        'approved_claims': approved_claims,
    }
    return render(request, 'account/profile.html', context)


@login_required(login_url='account_login')
def account_change_password_view(request):
    if request.method == 'POST':
        form = AccountPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after password change
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = AccountPasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {'form': form})


@login_required(login_url='account_login')
def delete_account_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        if not password:
            messages.error(request, 'Please enter your password to confirm account deletion.')
            return redirect('delete_account')
        
        user = request.user
        if user.check_password(password):
            logout(request)
            user.delete()
            messages.success(request, 'Your account was deleted successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect password. Account was not deleted.')
            return redirect('delete_account')
            
    return render(request, 'account/delete_account.html')


# ==========================================
# Admin Dashboard Views
# ==========================================
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count

@staff_member_required(login_url='account_login')
def admin_dashboard_view(request):
    total_users = CustomUser.objects.count()
    verified_users = CustomUser.objects.filter(is_verified=True).count()
    
    total_items = LostFoundItem.objects.count()
    active_items = LostFoundItem.objects.filter(status='open').count()
    resolved_items = LostFoundItem.objects.filter(status='resolved').count()
    
    total_claims = Claim.objects.count()
    pending_claims = Claim.objects.filter(status='pending').count()
    
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_items = LostFoundItem.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'verified_users': verified_users,
        'total_items': total_items,
        'active_items': active_items,
        'resolved_items': resolved_items,
        'total_claims': total_claims,
        'pending_claims': pending_claims,
        'recent_users': recent_users,
        'recent_items': recent_items,
    }
    return render(request, 'admin_dashboard/overview.html', context)


@staff_member_required(login_url='account_login')
def admin_users_view(request):
    query = request.GET.get('q', '')
    if query:
        users = CustomUser.objects.filter(email__icontains=query) | CustomUser.objects.filter(first_name__icontains=query) | CustomUser.objects.filter(last_name__icontains=query)
    else:
        users = CustomUser.objects.all().order_by('-date_joined')
        
    context = {'users': users, 'query': query}
    return render(request, 'admin_dashboard/users.html', context)


@staff_member_required(login_url='account_login')
def admin_toggle_user_status(request, pk):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=pk)
        if user == request.user:
            messages.error(request, 'You cannot deactivate your own account.')
        elif user.is_superuser:
            messages.error(request, 'You cannot deactivate a superuser.')
        else:
            user.is_active = not user.is_active
            user.save()
            status = 'activated' if user.is_active else 'suspended'
            messages.success(request, f'User {user.email} has been {status}.')
    return redirect('admin_users')


@staff_member_required(login_url='account_login')
def admin_items_view(request):
    query = request.GET.get('q', '')
    if query:
        items = LostFoundItem.objects.filter(title__icontains=query) | LostFoundItem.objects.filter(description__icontains=query)
    else:
        items = LostFoundItem.objects.all().order_by('-created_at')
        
    context = {'items': items, 'query': query}
    return render(request, 'admin_dashboard/items.html', context)


@staff_member_required(login_url='account_login')
def admin_delete_item(request, pk):
    if request.method == 'POST':
        item = get_object_or_404(LostFoundItem, pk=pk)
        item.delete()
        messages.success(request, 'Item deleted permanently.')
    return redirect('admin_items')

