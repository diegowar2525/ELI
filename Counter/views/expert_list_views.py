import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import redirect
from ..models import Expert, ExpertWord


def expert_list_view(request):
    if not (request.user.is_superuser or Expert.objects.filter(user=request.user).exists()):
        return redirect('panel')

    experts = Expert.objects.prefetch_related("word_lists")
    return render(request, "expert_lists.html", {"experts": experts})


def create_list(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print('[CREATE] Recibido:', data)
        expert_id = data.get('expert_id')
        name = data.get('name')
        words = data.get('words', [])
        expert = get_object_or_404(Expert, id=expert_id)
        new_list = ExpertWord.objects.create(expert=expert, name=name, words=words)
        return JsonResponse({'success': True, 'id': new_list.id})
    return JsonResponse({'success': False}, status=400)


def get_list_json(request, list_id):
    lista = get_object_or_404(ExpertWord, id=list_id)
    return JsonResponse({
        "id": lista.id,
        "name": lista.name,
        "words": lista.words
    })


def update_list(request, list_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    data  = json.loads(request.body)

    try:
        lista = ExpertWord.objects.get(id=list_id)
    except ExpertWord.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)

    # Solo tocar los campos presentes en el JSON -------------------------
    if "name" in data and data["name"] is not None:
        lista.name = data["name"]

    if "words" in data:
        lista.words = data["words"]

    lista.save()
    return JsonResponse({"success": True})


def delete_list(request, list_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        lista = ExpertWord.objects.get(id=list_id)
        lista.delete()
        return JsonResponse({"success": True})
    except ExpertWord.DoesNotExist:
        return JsonResponse({"error": "not found"}, status=404)
