
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.admin.models import LogEntry
from django.db.models import Sum, Q
from django.utils import timezone

from administration.models import WhatsappNotificationModel
from finance.models import PaymentRequestModel, PropertiesBuySale
from membership.models import User, Profile, Nominee, ContactUs

from administration.forms import WhatsappNotificationForm, WhatsappNotificationToPerUserForm
from finance.forms import PropertiesForm
from membership.forms import UserUpdateForm, NomineeInfoForm


from finance.admin import PaymentRequestModelResource
from membership.admin import UserModelResource

import itertools
import random

import io
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


from django.http import JsonResponse
from .helpers.send_messages_whatsapp import send_whatsapp_messages
from .helpers.export_invoices import export_invoice_data, export_unpaid_data_as_pdf
from .helpers.export_excel_csv_format import export_excel_csv
from .helpers.unpaid_reports import get_unpaid_report, get_unpaid_report_per_user
from .helpers.paid_unpaid_billings import calculate_per_user_billing, calculate_all_users_billing
from .helpers.export_all_as_pdf import download_member_report, download_profile_report, download_nominee_report, download_invoice_report, download_transaction_list_report, download_unpaid_list_report


# ADMIN INDEX VIEWS TO SHOW ALL SUMMARY
def admin_index_view(request):
    if request.user.is_hr or request.user.is_admin or request.user.is_finance:
        # SHOWING DJANGO ACTIVITY LOGS
        logs = LogEntry.objects.all().order_by('-action_time')

        # SHOWING PAYMENT TRANSACTIONS
        transactions = PaymentRequestModel.objects.all().order_by('-created')[:6]

        # SHOWING HISTORY FROM ALL MODELS
        all_objects_list = list(itertools.chain(
            User.history.model.objects.all().order_by('-history_date'),
            Profile.history.model.objects.all().order_by('-history_date'),
            Nominee.history.model.objects.all().order_by('-history_date'),
            ContactUs.history.model.objects.all().order_by('-history_date'),
            PaymentRequestModel.history.model.objects.all().order_by('-history_date')
        ))

        history_list = list(all_objects_list)
        count = min(len(history_list), len(history_list))
        random_history_list = random.sample(history_list, count) if count > 0 else []
        # END HISTORY BLOCK HERE ========================

        # CALCULATING TOTAL MONEY TRANSACTIONS HERE ===============================

        # Calculate both totals in a single database query
        payment_totals = PaymentRequestModel.objects.aggregate(
            total_cash=Sum('amount_of_money', filter=Q(payment_method='Cash') & Q(status='Approved') & Q(is_accept=True)),
            total_bank=Sum('amount_of_money', filter=Q(payment_method='Bank') & Q(status='Approved') & Q(is_accept=True)),

            
            total_savings_cash=Sum('amount_of_money', filter=Q(calculation_type='Savings') & Q(payment_method='Cash') & Q(status='Approved') & Q(is_accept=True)),
            total_savings_bank=Sum('amount_of_money', filter=Q(calculation_type='Savings') & Q(payment_method='Bank') & Q(status='Approved') & Q(is_accept=True)),
            total_savings_bkash=Sum('amount_of_money', filter=Q(calculation_type='Savings') & Q(payment_method='Bkash') & Q(status='Approved') & Q(is_accept=True)),
            total_savings_rocket=Sum('amount_of_money', filter=Q(calculation_type='Savings') & Q(payment_method='Rocket') & Q(status='Approved') & Q(is_accept=True)),


            total_developments=Sum('amount_of_money', filter=Q(payment_method='Developments') & Q(status='Approved') & Q(is_accept=True)),
            total_expense=Sum('amount_of_money', filter=Q(calculation_type='Expense') & Q(status='Approved') & Q(is_accept=True)),
            total_loan=Sum('amount_of_money', filter=Q(calculation_type='Loan') & Q(status='Approved') & Q(is_accept=True)),
            total_welfare=Sum('amount_of_money', filter=Q(calculation_type='Welfare') & Q(status='Approved') & Q(is_accept=True)),

        )

        # Access the values (returns 0.00 instead of None if no transactions exist)
        cash_total = payment_totals['total_cash'] or 0
        bank_total = payment_totals['total_bank'] or 0

        
        savings_total_cash = payment_totals['total_savings_cash'] or 0
        savings_total_bank = payment_totals['total_savings_bank'] or 0
        savings_total_bkash = payment_totals['total_savings_bkash'] or 0
        savings_total_rocket = payment_totals['total_savings_rocket'] or 0

        development_total = payment_totals['total_developments'] or 0
        expense_total = payment_totals['total_expense'] or 0
        loan_total = payment_totals['total_loan'] or 0
        welfare_total = payment_totals['total_welfare'] or 0

        # Sum savings_total_cash and savings_total_bank and savings_total_bkash and savings_total_rocket
        total_received_balance = (savings_total_cash + savings_total_bank + savings_total_bkash + savings_total_rocket)
        total_cash_and_bank = (savings_total_cash + savings_total_bank)
        total_bkash_and_rocket = (savings_total_bkash + savings_total_rocket)

        # Current Balance --> Deductions Expense and Loan From total_received_balance
        current_balance = total_received_balance - (expense_total + loan_total + welfare_total)

        # Total Expanse --> expense + loan + welfare
        total_expense = (expense_total + loan_total + welfare_total)

        # END CALCULATING TOTAL MONEY TRANSACTIONS HERE ===============================

        recent_savings_list = PaymentRequestModel.objects.filter(calculation_type='Savings').order_by('-id')
        recent_members_list = Profile.objects.all().order_by('-id')



        # ==================================== Unpaid users and month =======================================
        
        
        # ==================================== Unpaid users and month =======================================

        
        context = {
            'logs': logs,
            'transactions': transactions,
            'all_objects_list': random_history_list,
            'total_received_balance': total_received_balance,
            'total_cash_and_bank': total_cash_and_bank,
            'total_bkash_and_rocket': total_bkash_and_rocket,
            'current_balance': current_balance,
            'total_expense': total_expense,
            'loan_total': loan_total,
            'welfare_total': welfare_total,
            'recent_savings_list': recent_savings_list,
            'recent_members_list': recent_members_list,
            }
        return render(request, 'admin_index.html', context)
    else:
        return redirect('membership:profile_view')  


# ADMIN USERS LIST VIEW
def admin_user_list_view(request):
    if request.user.is_hr or request.user.is_admin or request.user.is_finance:
        # SHOWING PAYMENT TRANSACTIONS
        users = User.objects.all().order_by('-date_joined')
        
        context = {
            'users': users
            }
        return render(request, 'user_list.html', context)
    else:
        return redirect('membership:profile_view')



def admin_user_update_view(request, id):
    if request.user.is_authenticated:
        if request.user.is_hr or request.user.is_admin or request.user.is_finance:
            get_user = User.objects.get(id=id)
            form = UserUpdateForm(instance=get_user)

            if request.method == "POST" or request.method == "post":
                form = UserUpdateForm(request.POST, instance=get_user)
                if form.is_valid():
                    form.save()
                    return redirect('administration:admin_user_list')
            
            context = {
                'form': form
                }
            return render(request, 'update_user_info.html', context)
        else:
            return redirect('membership:profile_view')
    else:
        return redirect('membership:user_login')



# ADMIN PROFILE LIST VIEW
def admin_profile_list_view(request):
    if request.user.is_hr or request.user.is_admin or request.user.is_finance:
        # SHOWING PAYMENT TRANSACTIONS
        profiles = Profile.objects.all().order_by('-created_date')
        
        context = {
            'profiles': profiles
            }
        return render(request, 'profile_list.html', context)
    else:
        return redirect('membership:profile_view')



# ADMIN NOMINEE LIST VIEW
def admin_nominee_list_view(request):
    if request.user.is_hr or request.user.is_admin or request.user.is_finance:
        # SHOWING ALL NOMINEE TO ADMIN
        nominee_list = Nominee.objects.all().order_by('-created_date')
        
        context = {
            'nominee_list': nominee_list
            }
        return render(request, 'nominee_list.html', context)
    else:
        return redirect('membership:profile_view')



# ADMIN NOMINEE UPDATE VIEW
def admin_nominee_update_view(request, id):
    if request.user.is_authenticated:
        if request.user.is_hr or request.user.is_admin or request.user.is_finance:
            get_user = Nominee.objects.get(id=id)
            form = NomineeInfoForm(instance=get_user.profile.nominee)

            if request.method == "POST" or request.method == "post":
                form = NomineeInfoForm(request.POST, instance=get_user.profile.nominee)
                if form.is_valid():
                    form.save()
                    return redirect('administration:admin_nominee_list')
            
            context = {
                'form': form
                }
            return render(request, 'update_nominee_info.html', context)
        else:
            return redirect('membership:profile_view')
    else:
        return redirect('membership:user_login')



# TRANSACTION LIST VIEW
def admin_transaction_list(request):
    if request.user.is_authenticated:
        if request.user.is_hr or request.user.is_admin or request.user.is_finance:
            all_transactions = PaymentRequestModel.objects.all().order_by('-id')
            

            context = {
                'all_transactions': all_transactions
            }

            return render(request, 'transaction_list.html', context)
        else:
                return redirect('membership:profile_view')
    else:
        return redirect('membership:user_login')




# PROPERTIES LIST VIEW
def admin_properties_list_view(request):
    if request.user.is_authenticated:
        if request.user.is_hr or request.user.is_admin or request.user.is_finance:
            form = PropertiesForm()
            if request.method == 'POST' or request.method == 'post':
                form = PropertiesForm(request.POST)
                all_users = User.objects.all()
                if form.is_valid():
                    form_obj = form.save(commit=False)
                    form_obj.save()
                    form_obj.user.set(all_users)
                    form_obj.save()
                    messages.success(request, "Properties document have been created successfully.")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


            properties_list = PropertiesBuySale.objects.all().order_by('-id')
            

            context = {
                'form': form,
                'properties_list': properties_list,
            }

            return render(request, 'properties_list.html', context)
        else:
                return redirect('membership:profile_view')
    else:
        return redirect('membership:user_login')



# TRANSACTION LIST VIEW
def admin_unpaid_report_list(request):
    if request.user.is_authenticated:
        if request.user.is_hr or request.user.is_admin or request.user.is_finance:
            users = User.objects.all().order_by('-id')
            reports_data = calculate_all_users_billing(users)

            context = {
                'reports_data': reports_data
            }

            return render(request, 'unpaid_reports.html', context)
        else:
            return redirect('membership:profile_view')
    else:
        return redirect('membership:user_login')



# ADMIN MESSAGES LIST VIEW
def admin_message_list_view(request):
    if request.user.is_hr or request.user.is_admin or request.user.is_finance:
        # SHOWING ALL MESSAGES THAT USER SEND TO ADMIN
        messages = ContactUs.objects.all().order_by('-created')
        
        context = {
            'messages': messages
            }
        return render(request, 'message_list.html', context)
    else:
        return redirect('membership:profile_view')



# ADMIN MESSAGES LIST VIEW
def admin_notification_view(request):
    if request.user.is_hr or request.user.is_admin or request.user.is_finance:
        to_all_members_form = WhatsappNotificationForm(request.POST)
        to_particular_member_form = WhatsappNotificationToPerUserForm(request.POST)

        if request.method == 'post' or request.method == 'POST':
            if 'btn-all_member' in request.POST:
                company = request.POST.get('company')
                message = request.POST.get('message')

                all_members = User.objects.all()
                for member in all_members:
                    # Example recipient: Include country code, remove leading zeros/plus signs
                    phone_number = member.profile.phone_number
                    
                    result = send_whatsapp_messages(
                        recipient_phone = phone_number,
                        text_body = f"*{company}* \n\n{message} \n\n*Best Regards,* \n*Finance Department*"
                    )

                
                # creating object of sended messages to whatsapp
                whatsapp_notification_obj = WhatsappNotificationModel.objects.create(company=company, message=message, is_sended=True)
                # set all users to whatsapp notification object
                whatsapp_notification_obj.users.set(all_members)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
            elif 'btn-per_member' in request.POST:
                company = request.POST.get('company')
                message = request.POST.get('message')
                get_user_id = request.POST.get('users')

                
                user_obj = User.objects.get(id=get_user_id) # this object will use for to get user phone number
                
                # recipient: Include country code, remove leading zeros/plus signs
                phone_number = user_obj.profile.phone_number
                result = send_whatsapp_messages(
                    recipient_phone = phone_number,
                    text_body = f"*{company}* \n\n {message} \n\n*Best Regards,* \n*Finance Department*"
                )

                if result["success"]:
                    # creating object of sended messages to whatsapp
                    whatsapp_notification_obj = WhatsappNotificationModel.objects.create(company=company, message=message, is_sended=True)
                    # set a perticular user to whatsapp notification object
                    whatsapp_notification_obj.users.set([user_obj])
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            all_whatsapp_notifications = WhatsappNotificationModel.objects.all().order_by('-id')

            to_all_members_form = WhatsappNotificationForm()
            to_particular_member_form = WhatsappNotificationToPerUserForm()

            context = {
                'all_whatsapp_notifications': all_whatsapp_notifications,
                'to_all_members_form': to_all_members_form,
                'to_particular_member_form': to_particular_member_form
            }
            return render(request, 'notification_list.html', context)
    else:
        return redirect('membership:profile_view')



# Export Payments data excel and csv format
def export_all_transactions_data(request, format):
    if request.user.is_authenticated:
        resource = PaymentRequestModelResource()
        format_name = 'transactions'
        export_response = export_excel_csv(resource, format, format_name)
        return export_response
    else:
        return redirect('membership:user_login')
    


# Export Members data excel and csv format
def export_user_access_data(request, format):
    if request.user.is_authenticated:
        resource = UserModelResource()
        format_name = 'member_access'
        export_response = export_excel_csv(resource, format, format_name)
        return export_response
    else:
        return redirect('membership:user_login')



# Export invoice data pdf format
def export_all_invoice_data(request, pk):
    if request.user.is_authenticated:
        response = download_invoice_report(pk)
        return response
    else:
        return redirect('membership:user_login')



# Send Whatsapp Message To All Users
def send_whatsapp_notification_to_unpaid_user(request, id):
    user_obj = User.objects.get(id=id)
    unpaid_user_report = calculate_per_user_billing(user_obj)


    # recipient: Include country code, remove leading zeros/plus signs
    unpaid_sms_text = "*অপরিশোধিত চাদা রিমাইন্ডার* \nঅনুগ্রহ করে আপনার নিম্ন উল্যেখ্য মাসের মাসিক চাদা সময় মত পরিসদ করুন।"
    unpaid_total_months = unpaid_user_report['unpaid_months']
    total_unpaid_due = unpaid_user_report['total_unpaid_due']
    unpaid_user_name = user_obj.profile.full_name
    # extract only month names
    due_month_list = [item['month_name'] for item in unpaid_total_months]
    display_due_months = "\n".join(due_month_list)


    message_body = f"*Hello Mr. {unpaid_user_name}* \n\n{unpaid_sms_text} \n\n*মোট অপরিশোধিত বকেয়া:* {total_unpaid_due}\n\n*অপরিশোধিত মাসের বিবরণ:*\n{display_due_months}\n\n\n\n*Best Regards*, \n*Finance Department*"

    phone_number = user_obj.profile.phone_number
    result = send_whatsapp_messages(
        recipient_phone = phone_number,
        text_body = message_body
    )
    
    if result["success"]:
        # creating object of sended messages to whatsapp
        whatsapp_notification_obj = WhatsappNotificationModel.objects.create(company="অপরিশোধিত চাদা রিমাইন্ডার ↓", message=message_body, is_sended=True)
        # set all users to whatsapp notification object
        whatsapp_notification_obj.users.set([user_obj])
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return JsonResponse({"status": "Failed to send message", "details": result["error"]}, status=400)


# Export member list PDF
def download_member_report_view(request):
    return download_member_report(request)

# Export profile list PDF
def download_profile_report_view(request):
    return download_profile_report(request)

# Export nominee list PDF
def download_nominee_report_view(request):
    return download_nominee_report(request)


# Export nominee list PDF
def download_transaction_report_view(request):
    return download_transaction_list_report(request)


# Export nominee list PDF
def download_unpaid_report_view(request):
    return download_unpaid_list_report(request)















