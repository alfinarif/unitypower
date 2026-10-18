from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone
import calendar
import os
from django.conf import settings

import io
from django.http import FileResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

from finance.models import PaymentModel, DuePayment
from finance.forms import PaymentRequestForm, PaymentViaAdminForm

from administration.helpers.send_messages_whatsapp import send_whatsapp_messages
from administration.helpers.push_notification import send_notification_to_finance
from membership.models import User


# TRANSACTION LIST VIEW
def transaction_list(request):
    if request.user.is_authenticated:
        all_transactions = request.user.payments.all().order_by('-created')
        

        context = {
            'all_transactions': all_transactions,
        }

        return render(request, 'transaction_list_page.html', context)
    else:
        return redirect('membership:user_login')


# PAYMENT REQUEST VIEW
def payment_request(request):
    if request.user.is_authenticated:
        form = PaymentRequestForm()
        admin_form = PaymentViaAdminForm()
        
        if request.user.is_hr or request.user.is_admin or request.user.is_finance:
            if request.method == 'post' or request.method == 'POST':
                admin_form = PaymentViaAdminForm(request.POST)
                
                if admin_form.is_valid():
                    admin_form.save()
                    messages.success(request, 'Your payment request submited successfully.')
                    return redirect('administration:admin_transaction_list')
                else:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                admin_form = PaymentViaAdminForm()
        else:
            if request.method == 'post' or request.method == 'POST':
                form = PaymentRequestForm(request.POST)
                if form.is_valid():
                    
                    current_submited_form = form.save(commit=False)
                    current_submited_form.user = request.user
                    
                    # 2. Save the instance to the DB correctly (modifies the object in place)
                    current_submited_form.save()
                    

                    # 3. Cache the values to prevent N+1 database queries inside the loop
                    payment_amount = current_submited_form.amount_of_money
                    user_email = request.user.email  # We already have request.user loaded!
                    document_url = current_submited_form.document.url if current_submited_form.document else "/"

                    # 4. Fetch the finance users
                    type_list = ['Member', 'Chief-Adviser', 'Organizing-Committee']
                    users_type_finance = User.objects.exclude(user_type__in=type_list)
                    domain = request.build_absolute_uri() 
                    # 5. Send notifications safely
                    for user in users_type_finance:
                        send_notification_to_finance(
                            user_id = user.id,
                            title = f"{payment_amount}BDT Payment Submited.❤️",
                            body = f"{user_email} Has Submited Monthly Payment, Kindly Request To Check And Return Any Feedback Thank You.",
                            click_action = f"{document_url}"
                        )
                        
                    messages.success(request, 'Your payment request submited successfully.')
                    return redirect('finance:transaction_list')
                else:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                form = PaymentRequestForm()

        # showing all payment request for current user
        all_payments = request.user.payments.all()
        context = {
            'form': form,
            'admin_form': admin_form,
            'all_payments': all_payments
        }
        return render(request, 'payment_request_page.html', context)
    else:
        messages.warning(request, 'To access features pleaase login to your account.')
        return redirect('membership:user_login')
    

# APPROVE OR REJECT PAYMENT REQUEST
def approve_or_reject_payment_request(request, id, status):
    if request.user.is_authenticated:
        current_user_payment_request = get_object_or_404(PaymentModel, pk=id)
        if current_user_payment_request.user == request.user:
            messages.error(request, "You cannot approve or rejects your own payment request.")
            return redirect('administration:admin_transaction_list')
        else:
            if status == 'Approved':
                # 1. Fetch the actual object instance along with user information up front
                pay_obj = PaymentModel.objects.select_related('user').filter(id=id).first()

                if not pay_obj:
                    # Handle the error if the record does not exist
                    messages.error(request, "Payment record not found.")
                    return redirect('administration:admin_transaction_list')

                # 2. Update the fields on the instance directly
                pay_obj.status = status
                pay_obj.is_accept = True
                pay_obj.approved_by = request.user
                pay_obj.approved_at = timezone.now()
                pay_obj.save()  # Commits the changes to the database
                

                # 3. Cache the values safely from the actual object instance
                payment_amount = pay_obj.amount_of_money
                user_email = pay_obj.user.email  
                obj_id = pay_obj.id

                # 4. Safely check if a document exists before grabbing its URL string
                document_url = pay_obj.document.url if pay_obj.document else "/"

                # 5. Send notifications safely using the updated model values
                send_notification_to_finance(
                    user_id = pay_obj.user.id,
                    title = "Payment Request Approved. ❤️",
                    body = f"{user_email} Your Submitted Monthly Fee {payment_amount}BDT Payment Has Been Approved, Thank You.",
                    click_action = document_url
                )


                payment_date = f"{calendar.month_name[current_user_payment_request.pay_month]} {current_user_payment_request.pay_year}"
                sms_body = f"*Payment Notification* \n\n*Hello {current_user_payment_request.user.profile.full_name}* \nYour payment request month of *{payment_date}* and amount is *TK-{current_user_payment_request.amount_of_money}* has been approved successfully.\n\n*Thank You*\n\n*Best Regards*\n*UnityPower Finance Department*"
                
                send_whatsapp_messages(current_user_payment_request.user.profile.phone_number, sms_body)
                messages.success(request, "Payment request has been approved.")
                return redirect('administration:admin_transaction_list')
            elif status == 'Rejected':
                PaymentModel.objects.filter(id=id).update(
                    status=status,
                    is_accept = False,
                    approved_by = request.user,
                    approved_at = timezone.now()
                    )
                messages.warning(request, "Your payment request has been rejected.")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                messages.warning(request, 'There is something went wrong, try again!')
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('membership:user_login')


# INVOICE PREVIEW VIEW
def invoice_preview(request, pk):
    if request.user.is_authenticated:
        current_invoice_object = get_object_or_404(PaymentModel, pk=pk)

        context = {
            'invoice': current_invoice_object
        }
        return render(request, 'invoice_preview_page.html', context)
    else:
        return redirect('membership:user_login')
    

# INVOICE DOWNLOAD FUNCTION VIEW
def invoice_download(request, pk):
    if request.user.is_authenticated:
        invoice = get_object_or_404(PaymentModel, pk=pk)

        context = {
            'invoice': invoice
            }

        # Render HTML template to string
        html_string = render_to_string('invoice_preview.html', context, request=request)
        # Render CSS template to string
        css_path = os.path.join(settings.STATIC_ROOT, 'assets/css/apps/invoice-preview.css')
        # Generate PDF in memory
        html = HTML(string=html_string)
        pdf_file = html.write_pdf() # add this inside write_pdf() to set CSS -> stylesheets=[CSS(css_path)]
        
        # Return FileResponse for downloading
        response = FileResponse(
            io.BytesIO(pdf_file), 
            as_attachment=True, 
            filename=f'invoice_{invoice.invoice_number}.pdf'
        )
        return response

    else:
        return redirect('membership:user_login')

















