from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from datetime import datetime

from datetime import date
from dateutil.relativedelta import relativedelta

from membership.models import User, Profile
from .forms import CreateUserForm, ProfileInfoForm, NomineeInfoForm, ContactUsForm

from finance.models import PaymentRequestModel
from django.db.models import Q
from django.db.models import Sum

from django.contrib.auth import authenticate, login, logout

from administration.helpers.paid_unpaid_billings import calculate_per_user_billing


# Email backend package for sending email
from administration.helpers.emailSenders import send_email_notification



# Users Registration -> CREATE AN ACCOUNT
def user_registration(request):
    if request.user.is_hr or request.user.is_admin:
        form = CreateUserForm()
        if request.method == "POST":
            is_agree = request.POST.get('is_agree')
            if is_agree == "on":
                form = CreateUserForm(request.POST)
                if form.is_valid():
                    form.save()
                    current_user = form.cleaned_data.get('email')
                    messages.success(request, 'Account created for ' + current_user)
                    return redirect('administration:admin_user_list')
                else:
                    context = {
                        'form': form
                    }
                    messages.error(request, 'There is something wrong! try again.')
                    return render(request, 'auth/auth_register.html', context)

            else:
                form = CreateUserForm()

        context = {
            'form': form
        }
        return render(request, 'auth/auth_register.html', context)
    else:
        messages.warning(request, "You don't have access to create an user profile!")
        return redirect('membership:user_login')


# Users Authentication and Athurizations
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome {email} to your profile.")
            return redirect('membership:profile_view')
        else:
            messages.warning(request, 'Username or Password invalid..!')

    context = {}
    return render(request, 'auth/auth_login.html', context)


# USER LOGOUT -> WHENE USER IS LOGGED IN THEY CAN LOGOUT
def user_logout(request):
    logout(request)
    messages.info(request, 'Login to access your profile.')
    return redirect('membership:user_login')


# PROFILE VIEW FOR ALL TYPE OF USERS
def profile_view(request):
    if request.user.is_authenticated:
        if request.user.is_hr or request.user.is_admin or request.user.is_finance:
            messages.success(request, 'You have full access at Admin Panel.')
            return redirect('administration:admin_index')
        else:
            context = {
                'profile': request.user.profile
            }
            return render(request, 'auth/user_profile.html', context)
    else:
        return redirect('membership:user_login')


# INDEX VIEW FOR ALL TYPE OF USERS
def summary_view(request):
    if request.user.is_authenticated:
        # CALCULATING TOTAL MONEY TRANSACTIONS HERE ===============================
        
        # Calculate both totals in a single database query
        payment_totals = PaymentRequestModel.objects.aggregate(
            total_savings_cash=Sum('amount_of_money', filter=Q(calculation_type='Savings') & Q(user=request.user) & Q(payment_method='Cash') & Q(status='Approved') & Q(is_accept=True)),
            total_savings_bank=Sum('amount_of_money', filter=Q(calculation_type='Savings') & Q(user=request.user) & Q(payment_method='Bank') & Q(status='Approved') & Q(is_accept=True)),
            total_savings_bkash=Sum('amount_of_money', filter=Q(calculation_type='Savings') & Q(user=request.user) & Q(payment_method='Bkash') & Q(status='Approved') & Q(is_accept=True)),
            total_savings_rocket=Sum('amount_of_money', filter=Q(calculation_type='Savings') & Q(user=request.user) & Q(payment_method='Rocket') & Q(status='Approved') & Q(is_accept=True)),


            total_expense=Sum('amount_of_money', filter=Q(calculation_type='Expense') & Q(status='Approved') & Q(is_accept=True)),
            total_loan=Sum('amount_of_money', filter=Q(calculation_type='Loan') & Q(status='Approved') & Q(is_accept=True)),
            total_welfare=Sum('amount_of_money', filter=Q(calculation_type='Welfare') & Q(status='Approved') & Q(is_accept=True)),
            total_developments=Sum('amount_of_money', filter=Q(payment_method='Developments') & Q(status='Approved') & Q(is_accept=True)),

        )

        
        savings_total_cash = payment_totals['total_savings_cash'] or 0
        savings_total_bank = payment_totals['total_savings_bank'] or 0
        savings_total_bkash = payment_totals['total_savings_bkash'] or 0
        savings_total_rocket = payment_totals['total_savings_rocket'] or 0

        

        development_total = payment_totals['total_developments'] or 0
        expense_total = payment_totals['total_expense'] or 0
        loan_total = payment_totals['total_loan'] or 0
        welfare_total = payment_totals['total_welfare'] or 0

        # Sum savings_total_cash and savings_total_bank and savings_total_bkash and savings_total_rocket
        total_payment = (savings_total_cash + savings_total_bank + savings_total_bkash + savings_total_rocket)
        
        # END CALCULATING TOTAL MONEY TRANSACTIONS HERE ===============================
        last_five_transaction = PaymentRequestModel.objects.filter(user=request.user).order_by('-id')[:3]
        last_payment = PaymentRequestModel.objects.filter(Q(user=request.user) & Q(is_accept=True) & Q(status='Approved')).last()


    # ==================== get unpaid users, amounts reports ==================================
        unpaid_reports = calculate_per_user_billing(request.user)

        context = {
            'total_payment': total_payment,
            'last_payment': last_payment,
            'last_five_transaction': last_five_transaction,
            'unpaid_reports': unpaid_reports
            
        }
        messages.info(request, 'Your Finance A/C Summary.')
        return render(request, 'summary_page.html', context)
    else:
        return redirect('membership:user_login')


# PROFILE UPDATE VIEW FOR ALL TYPE OF USERS
def notice_to_update_profile(request):
    if request.user.is_authenticated:
        if request.user.profile.is_fully_filled:
            return redirect('membership:profile_view')
        else:
            username = request.user.email.split('@')[0]
            context = {
                'user': request.user,
                'username': username
            }
            return render(request, 'auth/info_to_update_profile.html', context)
    else:
        return redirect('membership:user_login')


# PROFILE UPDATE VIEW FOR ALL TYPE OF USERS
def update_profile(request, id):
    if request.user.is_authenticated:
        get_profile = Profile.objects.get(id=id)
        
        if request.method == "POST":
            form = ProfileInfoForm(request.POST, request.FILES, instance=get_profile)
            if form.is_valid:
                current_form = form.save(commit=False)
                current_form.avatar = request.FILES.get('avatar')
                current_form.updated_date = datetime.now()
                current_form.save()
                messages.success(request, 'Your profile info updated successfully')
                return redirect('membership:profile_view')
            else:
                messages.warning(request, 'Something is wrong! try again.')
                form = ProfileInfoForm(instance=get_profile)
                context = {
                    'form': form
                }
                return render(request, 'auth/update_profile_form.html', context)

        else:
            form = ProfileInfoForm(instance=get_profile)

        context = {
            'form': form
        }
        return render(request, 'auth/update_profile_form.html', context)

    else:
        return redirect('membership:user_login')


# CONTACT US PAGE VIEW
def contact_us(request):
    if request.user.is_authenticated:
        form = ContactUsForm()
        if request.method == "POST":
            form = ContactUsForm(request.POST)
            if form.is_valid():
                current_object = form.save(commit=False)
                current_object.user = request.user
                current_object.save()

                messages.success(request, 'Your message sended to admin successfully!')
                return redirect('membership:contact_us')
            else:
                context = {
                    'form': form
                }
                messages.error(request, 'There is something wrong! try again.')
                return render(request, 'contact_us.html', context)

        context = {
            'form': form
        }
        return render(request, 'contact_us.html', context)
    else:
        return redirect('membership:user_login')


# Throw error 404 not found 
def custom_page_404_not_found(request, exception):
    return render(request, '404.html', {'message': 'The page you requested was not found'}, status=404)


# Privacy or terms and condition page views
def terms_and_condition_page(request):
    return render(request, 'privacy.html')








