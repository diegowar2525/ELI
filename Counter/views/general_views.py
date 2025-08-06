import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from ..models import Company, Expert
from ..forms import IndividualReportUploadForm, ZipUploadForm, ComparativeListsForm
from ..main import process_report, process_zip
from User.models import Expert, User
from django.contrib.auth import get_user_model

# * ---------------------------------------- VISTAS GENERALES ----------------------------------------
def index_view(request):
    return render(request, "index.html")


@login_required
def panel_view(request):
    return render(request, "panel.html")


@login_required
def upload_view(request):
    individual_form = IndividualReportUploadForm()
    zip_form = ZipUploadForm()
    companies = Company.objects.all()

    if request.method == "POST":
        if "upload_individual" in request.POST:
            print(request.POST)
            individual_form = IndividualReportUploadForm(request.POST, request.FILES)
            if individual_form.is_valid():
                reporte = individual_form.save()
                process_report(reporte.file.path, reporte)
                messages.success(request, f"Reporte subido y procesado correctamente.")
                return redirect("upload")

        elif "upload_zip" in request.POST:
            zip_form = ZipUploadForm(request.POST, request.FILES)
            if zip_form.is_valid():
                zip_file = zip_form.cleaned_data["zip_file"]
                company = zip_form.cleaned_data["company"]

                zip_dir = os.path.join(settings.MEDIA_ROOT, "zip_uploads")
                os.makedirs(zip_dir, exist_ok=True)
                zip_path = os.path.join(zip_dir, zip_file.name)

                with open(zip_path, "wb+") as destination:
                    for chunk in zip_file.chunks():
                        destination.write(chunk)

                process_zip(zip_path, company)

                messages.success(request, f"Archivo ZIP subido y procesado correctamente.")
                return redirect("upload")

    return render(
        request,
        "upload.html",
        {
            "individual_form": individual_form,
            "zip_form": zip_form,
            "companies": companies,
        },
    )


def comparative_analysis_view(request):
    if not (request.user.is_superuser or Expert.objects.filter(user=request.user).exists()):
        return redirect('panel')
    
    resultado = None
    def normalize_words(word_list):
        return set(w.strip().lower() for w in word_list if w)

    if request.method == "POST":
        form = ComparativeListsForm(request.POST)
        if form.is_valid():
            list1 = form.cleaned_data["list1"]
            list2 = form.cleaned_data["list2"]

            words1 = normalize_words(list1.words or [])
            words2 = normalize_words(list2.words or [])

            resultado = {
                "list1": list1,
                "list2": list2,
                "comunes": sorted(words1 & words2),
                "solo_en_1": sorted(words1 - words2),
                "solo_en_2": sorted(words2 - words1),
            }
    else:
        form = ComparativeListsForm()

    return render(request, "comparative_analysis.html", {
        "form": form,
        "resultado": resultado,
    })


User = get_user_model()

@login_required
def user_view(request):
    # Solo superusuarios
    if not request.user.is_superuser:
        return redirect('panel')
    users = User.objects.exclude(id=request.user.id)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        profession = request.POST.get("profession", "")

        user = get_object_or_404(User, id=user_id)

        if action == "make_expert":
            Expert.objects.get_or_create(user=user, defaults={"profession": profession})
        elif action == "remove_expert":
            Expert.objects.filter(user=user).delete()
        elif action == "make_superuser":
            user.is_superuser = True
            user.is_staff = True
            user.save()
        elif action == "remove_superuser":
            if request.user != user:
                user.is_superuser = False
                user.is_staff = False
                user.save()

        return redirect("users")  # recargar la página

    return render(request, "users.html", {"users": users})
