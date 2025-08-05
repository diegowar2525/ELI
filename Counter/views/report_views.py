from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import json
from ..models import Report, Company

@login_required
def report_view(request):
    reports = Report.objects.select_related("company").all()
    companies = Company.objects.all()
    return render(
        request,
        "reports.html",
        {
            "reports": reports,
            "companies": companies,
        },
    )


def see_report_json(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    if report.company:
        company_data = {
            "id": report.company.id,
            "name": report.company.name,
        }
    else:
        company_data = {
            "id": None,
            "name": None,
        }
    
    data = {
        "id": report.id,
        "name": report.name,
        "year": report.year,
        "company": company_data,
        "upload_date": report.upload_date.strftime("%Y-%m-%d"),
    }
    
    return JsonResponse(data)


def delete_report(request, report_id):
    Report.objects.filter(id=report_id).delete()
    return HttpResponse(status=204)


def update_report(request, report_id):
    data = json.loads(request.body)
    try:
        report = Report.objects.get(id=report_id)
        report.name = data["name"]
        report.year = data["year"]
        report.company = Company.objects.get(id=data["company"])
        report.save()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)
