# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpRequest, JsonResponse

from .models import Tag, User, TokenStat, Image, Album
from rest_framework import status
from rest_framework.request import Request
import uuid
import json
from django.views.decorators.http import require_http_methods
from .serializers import UserSerializer, TagSerializer, ImageSerializer
from rest_framework.decorators import api_view
from django.forms import URLField
from django.core.exceptions import ValidationError
import logging

import boto3
from botocore.exceptions import ClientError
from urllib.request import urlopen
import requests


def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3_client = boto3.client('s3', aws_access_key_id='AKIAYESYDY5VLEYZMTWQ',
                             aws_secret_access_key='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')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logging.error(response)
    except ClientError as e:
        logging.error(e)
        return False
    return True


@api_view(['GET'])
def api_overview(request):
    print('Andar aaya!')
    return JsonResponse("Kuch diya!!", safe=False, status=status.HTTP_200_OK)


def validate_token(token_id):
    token_id = token_id.split(' ')[-1]
    token_stat = TokenStat.objects.get(token_id=str(token_id))
    if token_stat is not None:
        if token_stat.status is True:
            return token_stat.user_id
        else:
            return None
    return None


def log_and_print(log):
    logging.error(str(log))


@require_http_methods(['POST'])
def sign_up(request: Request) -> HttpResponse:
    try:
        log_and_print(str(request) + ' is the request')
        log_and_print(str(request.body) + 'is the request body')
        user_serializer = UserSerializer(data=json.loads(request.body))

        if not user_serializer.is_valid_for_insertion():
            logging.error('Data ' + str(request.body) + ' not valid due to ' + str(user_serializer.errors))
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        log_and_print('request is valid')
    except Exception as ex:
        logging.error('Logging string')
        logging.error(ex)
        # TODO: Since business error validations are already taken care of by serializers any other exceptions is on the
        #  server sides and client has no role to play in it.  i think it should be 500
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    try:
        user_instance = user_serializer.save()
        log_and_print(str(request.body) + " request properly saved")
        return HttpResponse(json.dumps({'id': user_serializer.instance.id}), status=status.HTTP_201_CREATED)
    except Exception as exp:
        log_and_print(str(request.body) + 'failed to save')
        logging.error(str(exp))
        return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@require_http_methods(['POST'])
def login(request: Request) -> HttpResponse:
    try:
        log_and_print(str(request) + ' is the request')
        log_and_print(str(request.body) + 'is the request body')
        user_serializer = UserSerializer(data=json.loads(request.body))
        if not user_serializer.is_valid_for_retrieval():
            logging.error('Data ' + str(request.body) + ' not valid due to ' + str(user_serializer.errors))
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        log_and_print('request is valid')
    except Exception as ex:
        logging.error('Logging string')
        logging.error(ex)
        # TODO: Since business error validations are already taken care of by serializers any other exceptions is on the
        #  server sides and client has no role to play in it.  i think it should be 500
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    log_and_print("Request is valid for " + str(request.body))
    user_ground_truth = User.objects.get(username=user_serializer.data['username'])
    if user_serializer.data['password'] == user_ground_truth.password:
        log_and_print('Validated for request!! ' + str(request.body))
        token_id = str(uuid.uuid4())
        user_id = user_ground_truth.id
        status_of_token = True
        token = TokenStat(token_id=token_id, user_id=user_id, status=status_of_token)
        token.save()
        logging.error(str(token_id) + " token id of token")
        return HttpResponse(json.dumps({"token": token_id}), status=status.HTTP_200_OK)
    logging.error("Password is wrong")
    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)


@require_http_methods(['POST'])
def logout(request: Request) -> HttpResponse:
    token_id = request.META['HTTP_AUTHORIZATION'].split(' ')[-1]
    token_stat = TokenStat.objects.get(token_id=str(token_id))
    logging.error('Request' + str(request))
    logging.error("Token instance " + str(token_stat))
    logging.error(str(token_id) + ' TOKEN ID')
    print(token_stat)
    try:
        if token_stat is not None:
            logging.error('Token exist for: ' + str(request.body))
            if token_stat.status is True:
                token_stat.status = False
                token_stat.save()
                logging.error('TOken saved ' + str(token_stat))
                return HttpResponse(status=status.HTTP_204_NO_CONTENT)
            else:
                return HttpResponse('Token expired!!')
    except Exception as exp:
        return HttpResponse('No such token!!', status=status.HTTP_204_NO_CONTENT)
    return HttpResponse('No such token!!', status=status.HTTP_204_NO_CONTENT)


def index(request):
    return HttpResponse("Hello, world. You're at Rest.")


@require_http_methods(['GET', 'POST'])
def tags(request: HttpRequest) -> HttpResponse:
    try:
        token_id = request.META['HTTP_AUTHORIZATION']
        logging.error(request)
        logging.error(token_id)
        user_id = validate_token(token_id)
        if user_id is not None:
            if request.method == 'POST':
                try:
                    logging.error(request.body)
                    tag_data = {'user_id': user_id, 'tag_name': json.loads(request.body)['name']}
                    # tag_data = json.loads(request.body)
                    logging.error(tag_data)
                    tag_serializer = TagSerializer(data=tag_data)
                    if not tag_serializer.is_valid():
                        logging.error('Tag is not valid!!')
                        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
                except Exception as exp:
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
                try:
                    tag_instance = tag_serializer.save()
                    logging.error(str(json.dumps({'id': tag_instance.id})))
                    return HttpResponse(json.dumps({'id': tag_instance.id}), status=status.HTTP_201_CREATED)
                except Exception as exp:
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
            if request.method == 'GET':
                logging.error(request)
                tag_ids = []
                for tag_instance in list(Tag.objects.all()):
                    if tag_instance.user_id == user_id:
                        tag_ids.append(tag_instance.id)
                all_data = json.dumps({'tag_ids': tag_ids})
                logging.error(str(all_data))
                return HttpResponse(all_data, status=status.HTTP_200_OK)
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as exec:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


@require_http_methods(['GET', 'PUT', 'DELETE'])
def tag(request: Request, tag_id: int):
    try:
        logging.error(request)
        logging.error(request.body)
        try:
            token_id = request.META['HTTP_AUTHORIZATION']
            logging.error(token_id)
            user_id = validate_token(token_id)
            logging.error('userId: ' + str(user_id))
        except Exception as exp:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        if user_id is not None:
            if request.method == 'GET':
                tag_instance = Tag.objects.get(pk=tag_id)
                if tag_instance.user_id == user_id:
                    logging.error(str(json.dumps({"id": tag_instance.id, "name": tag_instance.tag_name})))
                    return HttpResponse(json.dumps({"id": tag_instance.id, "name": tag_instance.tag_name}),
                                        status=status.HTTP_200_OK)
                logging.error('userId nahi mili aisi koi!! ' + str(user_id))
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)
            if request.method == 'PUT':
                tag_name = json.loads(request.body)['name']
                logging.error(tag_name + ' tag name')
                try:
                    tag_instance = Tag.objects.get(pk=tag_id)
                    if tag_instance.user_id == user_id:
                        tag_instance.tag_name = tag_name
                        tag_instance.save()
                        logging.error('success')
                        return HttpResponse(json.dumps({'result': 'success'}), status=status.HTTP_200_OK)
                except Exception as exp:
                    return HttpResponse(status=status.HTTP_404_NOT_FOUND)
            if request.method == 'DELETE':
                tag_instance = Tag.objects.get(pk=tag_id)
                if tag_instance.user_id == user_id:
                    tag_instance.delete()
                    logging.error("Delete kar diya")
                    return HttpResponse(status=status.HTTP_204_NO_CONTENT)
                logging.error('mila hi nahi data: ' + str(request.body))
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        logging.error("Not found")
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    except Exception as exp:
        logging.error(str(exp))
        return HttpResponse('nahi aayega result!!', status=status.HTTP_404_NOT_FOUND)


def validate_url(url):
    url_form_field = URLField()
    try:
        url_form_field.clean(url)
    except ValidationError:
        return False
    return True


def get_download_url(image_url: str, image_name: str) -> str:
    bucket_name = 'tu-cj-photos-assignment'
    if validate_url(image_url):
        file = requests.get(image_url)
        upload_file(file_name=file, bucket=bucket_name, object_name=image_name)
        return 'https:/s3.amazonaws.com/tu-cj-photos-assignment/image_name.jpg'
    return ""


@require_http_methods(['POST', 'GET'])
def create_image(request: Request) -> HttpResponse:
    try:
        try:
            token_id = request.META['HTTP_AUTHORIZATION']
            user_id = validate_token(token_id)
            logging.error(request)
            logging.error(token_id)
            logging.error(user_id)
        except Exception as exp:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if user_id is not None:
                image_data = json.loads(request.body)
                url = get_download_url(image_data['uri'])
                if url == "":
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
                image_content = {}
                if 'timestamp' in image_data:
                    image_content['timestamp'] = image_data['timestamp']
                image_content['name'] = image_data['name']
                image_content['place'] = image_data['place']
                image_content['uri'] = url
                image_content['user_id'] = user_id
                image_instance = ImageSerializer(data=image_content)
                logging.error(str(image_instance))
                if not image_instance.is_valid():
                    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
                image_instance.save()
                tag_ids = []
                for tag_id in image_data['tags']:
                    tag_ids.append(tag_id)
                    image_instance.tags.add(Tag.objects.get(id=int(tag_id)))
                image_instance.save()
                image_instance_json = json.dumps({'id': image_instance.id, 'name': image_data['name'],
                                                  'place': image_data['place'], 'uri': url,
                                                  'timestamp': image_data['timestamp'],
                                                  'user_id': user_id, 'tags': tag_ids})
                logging.error(image_instance_json)
                return HttpResponse(image_instance_json, status=status.HTTP_201_CREATED)
            else:
                return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'GET':
            if user_id is not None:
                logging.error(request)
                own_by_me = Image.objects.filter(user_id=user_id)
                shared_with_me = Image.objects.filter(shared_with__id=user_id)
                all_images = []
                for image in own_by_me:
                    all_images.append(image.id)
                for image in shared_with_me:
                    all_images.append(image.id)
                logging.error(all_images)
                return HttpResponse(json.dumps({"image_ids": all_images}), status=status.HTTP_200_OK)
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as ex:
        logging.error(str(ex))
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    logging.error('Not found')
    return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@require_http_methods(['GET', 'PUT', 'DELETE'])
def image_crud(request: Request, image_id: int):
    logging.error(request)
    token_id = request.META['HTTP_AUTHORIZATION']
    logging.error(token_id)
    user_id = validate_token(token_id)
    logging.error(user_id)
    if user_id is not None:
        if request.method == 'GET':
            image_instance = Image.objects.get(id=image_id)
            if image_instance.user_id == user_id:
                image_instance_json = json.dumps({
                    'id': image_instance.id,
                    'name': image_instance.name,
                    'place': image_instance.place,
                    'uri': image_instance.uri,
                    'timestamp': image_instance.timestamp,
                    'tags': [tag_instance.id for tag_instance in image_instance.tags.all()],
                    'shared_with': [user_instance.id for user_instance in image_instance.shared_with.all()]
                })
                logging.error(image_instance_json)
                return HttpResponse(image_instance_json, status=status.HTTP_200_OK)
            logging.error('Access nahi hai')
            return HttpResponse('get call kiya!!', status=status.HTTP_404_NOT_FOUND)
        if request.method == 'PUT':
            image_instance = Image.objects.get(id=image_id)
            if image_instance.user_id == user_id:
                query = json.loads(request.body)
                if 'name' in query:
                    image_instance.name = query['name']
                if 'place' in query:
                    image_instance.place = query['place']
                if 'uri' in query:
                    image_instance.uri = query['uri']
                if 'timestamp' in query:
                    image_instance.timestamp = query['timestamp']
                image_instance.save()
                tag_ids = []
                if 'tags' in query:
                    image_instance.tags.clear()
                    for tag_id in query['tags']:
                        tag_ids.append(tag_id)
                        image_instance.tags.add(Tag.objects.get(id=int(tag_id)))
                image_instance.save()
                image_instance_json = json.dumps({
                    'id': image_instance.id,
                    'name': image_instance.name,
                    'place': image_instance.place,
                    'uri': image_instance.uri,
                    'timestamp': image_instance.timestamp,
                    'tags': [tag_instance.id for tag_instance in image_instance.tags.all()]
                })
                logging.error(image_instance_json)
                return HttpResponse(image_instance_json, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            image_instance = Image.objects.get(id=image_id)
            if image_instance.user_id == user_id:
                image_instance.delete()
                logging.error('delete ho gaya successfully')
                return HttpResponse('kar diya delete jao aesh karo!!!', status=status.HTTP_204_NO_CONTENT)
    logging.error("Kisi method mein nahi jaa paya")
    return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@require_http_methods(['GET'])
def get_private_images(request: Request):
    try:
        logging.error(request)
        token_id = request.META['HTTP_AUTHORIZATION']
        user_id = validate_token(token_id)
        logging.error(token_id)
        logging.error(user_id)
        if user_id is not None:
            image_instances = Image.objects.all().filter(user_id=user_id)
            image_ids = []
            for image_instance in image_instances:
                image_ids.append(image_instance.id)
            logging.error(str(image_ids))
            return HttpResponse(json.dumps({'image_ids': image_ids}), status=status.HTTP_200_OK)
        logging.error("not found")
    except Exception as exp:
        logging.error(str(exp))
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


@require_http_methods(['GET'])
def get_shared_images(request):
    try:
        logging.error(request)
        token_id = request.META['HTTP_AUTHORIZATION']
        user_id = validate_token(token_id)
        logging.error(token_id)
        logging.error(user_id)
        if user_id is not None:
            image_instances = Image.objects.filter(shared_with__id=user_id)
            image_ids = []
            for image_instance in image_instances:
                image_ids.append(image_instance.id)
            logging.error(image_ids)
            return HttpResponse(json.dumps({"image_ids": image_ids}), status=status.HTTP_200_OK)
        logging.error('User is not authenticated!!')
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    except Exception as exp:
        logging.error("exception has occured: " + str(exp))
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


def image_share(request: Request, image_id: int):
    try:
        logging.error(request)
        logging.error(request.body)
        token_id = request.META['HTTP_AUTHORIZATION']
        user_id = validate_token(token_id)
        logging.error('UserId ' + str(user_id))
        user_ids = json.loads(request.body)['user_ids']
        if user_id is not None:
            image_instance = Image.objects.get(id=image_id)
            if image_instance.user_id == user_id:
                for user_id in user_ids:
                    image_instance.shared_with.add(User.objects.get(id=int(user_id)))
                image_instance.save()
                logging.error('Image shared successfully')
                return HttpResponse(status=status.HTTP_200_OK)
            return HttpResponse("image share nahi kar sakte tum!!", status=status.HTTP_404_NOT_FOUND)
    except Exception as ex:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse('kar dena share jaldi kya hai!!', status=status.HTTP_404_NOT_FOUND)


@require_http_methods(['POST', 'GET'])
def album(request: Request):
    if request.method == 'POST':
        try:
            logging.error(request)
            logging.error(request.body)
            token_id = request.META['HTTP_AUTHORIZATION']
            user_id = validate_token(token_id)
            logging.error('UserId ' + str(user_id))
            album_body = json.loads(request.body)
            album_instance = Album(name=album_body['name'], user_id=user_id)
            album_instance.save()
            image_ids = album_body['images']
            for image_id in image_ids:
                album_instance.images.add(Image.objects.get(id=int(image_id)))
            album_instance.save()
            return HttpResponse(json.dumps({"id": album_instance.id, "name": album_instance.name}),
                                status=status.HTTP_201_CREATED)
        except Exception as exp:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        try:
            logging.error(request)
            logging.error(request.body)
            token_id = request.META['HTTP_AUTHORIZATION']
            user_id = validate_token(token_id)
            logging.error('UserId ' + str(user_id))
            albums = Album.objects.filter(user_id=user_id)
            album_ids = [album_instance.id for album_instance in albums]
            return HttpResponse(json.dump({"album_ids": album_ids}), status=status.HTTP_200_OK)

        except Exception as exp:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)


def album_crud(request: Request, album_id: int):
    try:
        logging.error(request)
        logging.error(request.body)
        token_id = request.META['HTTP_AUTHORIZATION']
        user_id = validate_token(token_id)
    except Exception as exp:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)
    try:
        if user_id is not None:
            if request.method == 'GET':
                return HttpResponse('get wala is called!')
            if request.method == 'PUT':
                return HttpResponse('Put is called!!')
            if request.method == 'DELETE':
                return HttpResponse('Kar denge delete yaar!')
        else:
            return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    except Exception as exp:
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse('dekhte hai kya karna hai ' + str(album_id), status=status.HTTP_200_OK)
