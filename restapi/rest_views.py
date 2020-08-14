from django.contrib.auth import authenticate
from django.shortcuts import  render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.request import Request
# from rest_framework.decorators import api_view
from rest_framework import status
from .models import Tag, TokenStat
import json
from .serializers import TagSerializer
from .forms import SignUpForm

from rest_framework.views import APIView
from rest_framework.response import Response



from celery import shared_task
from celery.exceptions import Ignore
# from worker import app
# @app.task(bind=True)
@shared_task
def adding_task(x, y):
    return x + y

# @csrf_exempt
class HelloView(APIView):
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            # login(request, user)

            # return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
    return HttpResponse("diya re!!")


# @api_view(['GET'])
def api_overview(request):
    return JsonResponse("Kuch diya!!")
    # details = {
    #     "name": "zaid",
    #     "password": "algorithm"
    # }
    # return HttpResponse(details)


def validate_token(token_id):
    token_stat = TokenStat.objects.get(token_id=str(token_id))
    if token_stat is not None:
        if token_stat.status is True:
            return token_stat.user_id
        else:
            return None
    return None


# @require_http_methods(['GET', 'POST'])
def tags(request: Request) -> HttpResponse:
    token_id = request.META['HTTP_AUTHORIZATION']
    user_id = validate_token(token_id)
    if user_id is not None:
        if request.method == 'POST':
            tag_data = json.loads(request.body)
            name = tag_data['name']
            tag_instance = Tag(tag_name=name)
            tag_instance.save()
            return HttpResponse(json.dumps({'id': tag_instance.id}), status=status.HTTP_200_OK)
        if request.method == 'GET':
            tag_ids = []
            for tag_instance in list(Tag.objects.all()):
                tag_ids.append(tag_instance.id)
            all_data = json.dumps({'tag_ids': tag_ids})
            return HttpResponse(all_data, status=status.HTTP_200_OK)
    return HttpResponse(status=status.HTTP_404_NOT_FOUND)


# @require_http_methods(['GET', 'PUT', 'DELETE'])
def tag(request: Request, tag_id: int):
    try:
        token_id = request.META['HTTP_AUTHORIZATION']
        user_id = validate_token(token_id)
        if user_id is not None:
            if request.method == 'GET':
                tag_instance = Tag.objects.get(pk=tag_id)
                return HttpResponse(json.dumps({"id": tag_instance.id, "name": tag_instance.tag_name}))
            if request.method == 'PUT':
                tag_name = json.loads(request.body)['name']
                print(tag_name)
                tag_instance = Tag.objects.get(pk=tag_id)
                tag_instance.tag_name = tag_name
                tag_instance.save()
                return HttpResponse(json.dumps({'result': 'success'}))
            if request.method == 'DELETE':
                tag_instance = Tag.objects.get(pk=tag_id)
                tag_instance.delete()
                return HttpResponse(status=status.HTTP_200_OK)
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except Exception as exp:
        return HttpResponse('nahi aayega result!!', status=status.HTTP_404_NOT_FOUND)
