import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO


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