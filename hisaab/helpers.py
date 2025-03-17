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

    @staticmethod
    def render_to_file(template_path, context, filename):
        template = get_template(template_path)
        html = template.render(context)

        # Generate full file path
        pdf_directory = os.path.join(settings.MEDIA_ROOT, 'bills')
        file_path = os.path.join(pdf_directory, f"{filename}.pdf")

        # Create PDF
        with open(file_path, "wb") as file:
            pisa.CreatePDF(BytesIO(html.encode("UTF-8")), file)

        # Return the relative path to the file
        return os.path.join('bills', f"{filename}.pdf")