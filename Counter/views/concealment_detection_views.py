from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import Report
from ..main import find_paragraph
from django.shortcuts import get_object_or_404


@login_required
def concealment_detection_view(request):
    reports = Report.objects.all()
    selected_report = None
    paragraphs = []
    palabra = request.GET.get("palabra")
    report_id = request.GET.get("report_id")

    if palabra and report_id:
        selected_report = get_object_or_404(Report, id=report_id)
        paragraphs = find_paragraph(selected_report, palabra)

    return render(
        request,
        "concealment_detection.html",
        {
            "reports": reports,
            "selected_report": selected_report,
            "paragraphs": paragraphs,
            "palabra": palabra,
        },
    )
