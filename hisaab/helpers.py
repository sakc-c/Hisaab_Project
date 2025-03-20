import os
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


def get_bill_context(bill):
    from hisaab.models import BillDetails
    bill_details = BillDetails.objects.filter(billID=bill)
    subtotal = sum(detail.amount for detail in bill_details)
    discount_amount = subtotal * (Decimal(bill.discount) / Decimal(100))
    discount_amount = discount_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total = subtotal - discount_amount
    total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    # Return the context that will be used for both creating and downloading the PDF
    context = {
        'bill': bill,
        'bill_details': bill_details,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total': total,
    }

    return context


class Render:
    @staticmethod
    def render_to_response(template_path, context, filename):
        template = get_template(template_path)
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            content_disposition = f'attachment; filename="{filename}.pdf"'
            response['Content-Disposition'] = content_disposition
            return response
        return HttpResponse('Error rendering PDF', status=400)