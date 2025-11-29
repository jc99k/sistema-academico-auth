from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from .forms import LoginForm, TwoFactorForm, BackupCodeForm, Enable2FAForm
from .models import User
import qrcode
import qrcode.image.svg
from io import BytesIO


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.is_2fa_enabled:
                    # Store user ID in session for 2FA verification
                    request.session['pre_2fa_user_id'] = user.id
                    return redirect('verify_2fa')
                else:
                    # Login directly if 2FA is not enabled
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    return redirect('dashboard')
    else:
        form = LoginForm()

    return render(request, 'sistema_academico/login.html', {'form': form})


def verify_2fa_view(request):
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    use_backup = request.GET.get('backup', False)

    if request.method == 'POST':
        if use_backup:
            form = BackupCodeForm(user=user, data=request.POST)
        else:
            form = TwoFactorForm(user=user, data=request.POST)

        if form.is_valid():
            # 2FA verification successful
            del request.session['pre_2fa_user_id']
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')
    else:
        if use_backup:
            form = BackupCodeForm(user=user)
        else:
            form = TwoFactorForm(user=user)

    return render(request, 'sistema_academico/verify_2fa.html', {
        'form': form,
        'use_backup': use_backup
    })


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    return render(request, 'sistema_academico/dashboard.html', {
        'user': request.user
    })


@login_required
def setup_2fa_view(request):
    user = request.user

    if user.is_2fa_enabled:
        messages.info(request, '2FA is already enabled for your account.')
        return redirect('dashboard')

    # Generate TOTP secret if not exists
    if not user.totp_secret:
        user.generate_totp_secret()
        user.save()

    if request.method == 'POST':
        form = Enable2FAForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            if user.verify_totp(token):
                # Enable 2FA
                user.enable_2fa()
                backup_codes = user.backup_codes
                messages.success(request, '2FA has been enabled successfully!')
                return render(request, 'sistema_academico/backup_codes.html', {
                    'backup_codes': backup_codes
                })
            else:
                messages.error(request, 'Invalid code. Please try again.')
    else:
        form = Enable2FAForm()

    return render(request, 'sistema_academico/setup_2fa.html', {
        'form': form,
        'totp_uri': user.get_totp_uri()
    })


@login_required
def qr_code_view(request):
    user = request.user
    if not user.totp_secret:
        return HttpResponse('No TOTP secret found', status=400)

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(user.get_totp_uri())
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO object
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')


@login_required
def disable_2fa_view(request):
    user = request.user

    if not user.is_2fa_enabled:
        messages.info(request, '2FA is not enabled for your account.')
        return redirect('dashboard')

    if request.method == 'POST':
        user.disable_2fa()
        messages.success(request, '2FA has been disabled.')
        return redirect('dashboard')

    return render(request, 'sistema_academico/disable_2fa.html')


@login_required
def view_backup_codes_view(request):
    user = request.user

    if not user.is_2fa_enabled:
        messages.error(request, '2FA is not enabled for your account.')
        return redirect('dashboard')

    return render(request, 'sistema_academico/view_backup_codes.html', {
        'backup_codes': user.backup_codes
    })


@login_required
def regenerate_backup_codes_view(request):
    user = request.user

    if not user.is_2fa_enabled:
        messages.error(request, '2FA is not enabled for your account.')
        return redirect('dashboard')

    if request.method == 'POST':
        backup_codes = user.generate_backup_codes()
        user.save()
        messages.success(request, 'New backup codes have been generated.')
        return render(request, 'sistema_academico/backup_codes.html', {
            'backup_codes': backup_codes
        })

    return render(request, 'sistema_academico/regenerate_backup_codes.html')
