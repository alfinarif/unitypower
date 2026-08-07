from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils import timezone

import os
from django.conf import settings

import io
from django.http import FileResponse
from django.template.loader import render_to_string
from weasyprint import HTML, CSS

from finance.models import PaymentRequestModel
from finance.forms import PaymentRequestForm, PaymentViaAdminForm

# TRANSACTION LIST VIEW
def transaction_list(request):
    if request.user.is_authenticated:
        all_transactions = request.user.payment_request.all().order_by('-created')
        

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
                    return redirect('finance:transaction_list')
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
                    current_submited_form.save()
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                else:
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                form = PaymentRequestForm()

        # showing all payment request for current user
        user = request.user
        all_payments = user.payment_request.all()
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
        if status == 'Approved':
            PaymentRequestModel.objects.filter(id=id).update(
                status=status,
                is_accept = True,
                approved_by = request.user,
                approved_at = timezone.now()
                )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        elif status == 'Rejected':
            PaymentRequestModel.objects.filter(id=id).update(
                status=status,
                is_accept = False,
                approved_by = request.user,
                approved_at = timezone.now()
                )
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'There is something went wrong, try again!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('membership:user_login')


# INVOICE PREVIEW VIEW
def invoice_preview(request, pk):
    if request.user.is_authenticated:
        current_invoice_object = get_object_or_404(PaymentRequestModel, pk=pk)

        context = {
            'invoice': current_invoice_object
        }
        return render(request, 'invoice_preview.html', context)
    else:
        return redirect('membership:user_login')
    

# INVOICE DOWNLOAD FUNCTION VIEW
def invoice_download(request, pk):
    if request.user.is_authenticated:
        invoice = get_object_or_404(PaymentRequestModel, pk=pk)

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

















