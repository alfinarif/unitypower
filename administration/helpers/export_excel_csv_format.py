from django.http import HttpResponse
import itertools


# Export Payments data excel and csv format
def export_excel_csv(resource, format, format_name):
    model_resource = resource
    dataset = model_resource.export()
    if format == "csv":
        dataset_format = dataset.csv
        response = HttpResponse(dataset_format, content_type=f"text/{format}")
        response['Content-Disposition'] = f"attachment; filename={format_name}_report.{format}"
        return response
    else:
        dataset_format = dataset.xls
        response = HttpResponse(dataset_format, content_type=f"text/{format}")
        response['Content-Disposition'] = f"attachment; filename={format_name}_report.{format}"
        return response
