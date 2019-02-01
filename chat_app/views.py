import json
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.core import serializers
from chat_app.models import Chat, User, Message
from django.contrib import auth
from django.db.models import Q
import hashlib
import uuid


def login(request):
    body_unicode = request.body.decode('utf-8')

    try:
        body = json.loads(body_unicode)
    except:
        error_json = {"message": "Conversion error"}
        return JsonResponse(error_json, safe=False, status=400)

    username = body.get('username')
    password = body.get('password')

    error_json = {"message": "username or password error"}

    if not username or not password:
        return JsonResponse(error_json, safe=False, status=400)

    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        ok_json = {"message": "successfully login"}
        return JsonResponse(ok_json, safe=False)
    else:
        return JsonResponse(error_json, safe=False, status=400)


@login_required
@require_http_methods(['GET'])
def logout(request):
    auth.logout(request)

    ok_json = {"message": "successfully logout"}
    return JsonResponse(ok_json, safe=False)


# @login_required
@require_http_methods(['GET'])
def user_search(request):
    temporary_auth(request)

    limit = 10
    user = request.user
    username_prefix = request.GET.get('username')

    error_json = {"message": "Prefix error"}

    if not username_prefix:
        return JsonResponse(error_json, safe=False, status=400)

    users = User.objects.extra(where=["username LIKE %s %s"], params=[username_prefix, '%'])
    users_in_my_city = users.filter(city=user.city).values('id', 'username', 'city').order_by('-date_joined')[:limit]

    limit = limit - len(users_in_my_city)

    if limit > 0:
        users_other = users.filter(~Q(city=user.city)).values('id', 'username', 'city').order_by('-date_joined')[:limit]
    else:
        users_other = []

    res = list(chain(users_in_my_city, users_other))

    return JsonResponse(res, safe=False)


def temporary_auth(request):
    user = auth.authenticate(username='taifsalebame', password='vpLfieaESe0G')
    # user = auth.authenticate(username='Grisha', password='222')
    if user is not None and user.is_active:
        auth.login(request, user)
    return

# @login_required
@require_http_methods(['GET'])
def my_chats(request):
    temporary_auth(request)

    user = request.user
    chats = Chat.objects.filter(users=user).select_related()

    res = []

    for chat in chats:
        chat_json = {'id': chat.id, 'name': chat.name, 'users': list(chat.users.all().values('id', 'username'))}
        last_msg = Message.objects.filter(chat_id=chat.id).values('text', 'date', 'id').order_by('-date')[:1]

        if len(last_msg) == 0:
            chat_json['last_msg'] = "Empty"
        else:
            chat_json['last_msg'] = {'id': last_msg[0].get('id'),
                                     'date': last_msg[0].get('date'),
                                     'text': last_msg[0].get('text')}

        res.append(chat_json)

    return JsonResponse(res, safe=False)


# @login_required
@require_http_methods(['POST'])
def chat_send(request, **kwargs):
    temporary_auth(request)

    user = request.user
    chat_id = kwargs["id"]
    # print(kwargs["id"])
    body_unicode = request.body.decode('utf-8')

    error_json = {"message": "Conversion error"}

    try:
        messages = json.loads(body_unicode)
    except:
        return JsonResponse(error_json, safe=False, status=400)

    for message in messages:
        if not message:
            continue
        try:
            curr_message = Message.objects.create(text=message["message"], user=user, chat_id=chat_id)
        except:
            return JsonResponse(error_json, safe=False, status=400)
        else:
            curr_message.save()
            Chat.objects.get(id=chat_id).users.add(user)

    ok_json = {"message": "Successfully created"}

    return JsonResponse(ok_json, safe=False)


# @login_required
@require_http_methods(['GET'])
def chat_messages(request, **kwargs):
    temporary_auth(request)

    user = request.user
    chat_id = kwargs["id"]

    if not chat_id:
        return JsonResponse({"message": "Chat_id error"}, safe=False, status=400)

    access_to_chat = Chat.objects.filter(users=user, id=chat_id)

    if not access_to_chat:
        return JsonResponse({"message": "No access error"}, safe=False, status=400)

    page = request.GET.get('page')  # size * page = offset
    size = request.GET.get('size')  # size

    try:
        page = int(page)
    except (TypeError, ValueError):
        page = 0

    try:
        size = int(size)
    except (TypeError, ValueError):
        size = 5

    res = []

    messages = Message.objects.filter(chat_id=chat_id).order_by('-date').select_related()[
               size * page:][:size]

    for message in messages:
        elem = {"id": message.id, "text": message.text, "user": {"id": message.id, "username": message.user.username},
                "date": message.date}
        res.append(elem)

    return JsonResponse(res, safe=False)
