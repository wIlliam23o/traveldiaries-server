from django.shortcuts import render

# Create your views here.

import json

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

from .models import Diary

from . import models




@csrf_exempt
def post_sign_up(request):
    with transaction.atomic():
        user = User.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password'),
            email=request.POST.get('email')
        )
        user.save()
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        userinfo = models.UserInfo(user=user)
        userinfo.save()

    return HttpResponse(
        json.dumps(
            {
                'token': Token.objects.get(user=user).key
            }
        )
    )

@csrf_exempt
def get_user_detail(request):
    token = request.GET.get('token', None)
    if not token:
        return HttpResponse("Unauthorized", status=401)

    token = Token.objects.filter(key=token)

    if len(token) == 0:
        return HttpResponse("Unauthorized", status=401)

    user = token[0].user

    info = models.UserInfo.objects.filter(user=user)

    if len(info) == 0:
        info = models.UserInfo()
        info.user = user
        info.save()
    else:
        info = info[0]

    age = models.UserInfo.objects.filter(user=info.user)
    if len(age) == 0:
        weight = None
    else:
        weight = age[0].weight

    return HttpResponse(
        json.dumps(
            {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'age': age,
                'doj': str(info.join_date),
            }
        )
    )


@csrf_exempt
def post_post(request):
    print(request.body)
    request_dict = json.loads(request.body.decode('utf-8'))

    try:
        token = request_dict['token']
    except Exception:
        token = None

    if not token:
        print("No Token found in POST")
        return HttpResponse("Unauthorized", status=401)

    token = Token.objects.filter(key=token)

    if len(token) == 0:
        return HttpResponse("Unauthorized", status=401)

    user = token[0].user
    diaries = Diary.objects.all()

    if Diary.objects.get(diary_name=request_dict['diary_name']).DoesNotExist:
        return HttpResponse(
            json.dumps(
                {
                    'error': 'Diary does not exist'
                }
            ),
            status=500
        )

    with transaction.atomic():
        posty = models.Post()
        posty.number_of_items = request_dict['post_title']
        posty.user = user
        posty.post_title = request_dict['post_title']
        posty.diary = Diary.objects.get(diary_name=request_dict['diary_name'])
        posty.save()

    return HttpResponse(
        json.dumps(
            {
                'status': 'success'
            }
        )
    )

#evry line added has its worth


def get_wall_posts(request):
    token = request.GET.get('token', None)
    if not token:
        return HttpResponse("Unauthorized", status=401)

    token = Token.objects.filter(key=token)

    if len(token) == 0:
        return HttpResponse("Unauthorized", status=401)

    user = token[0].user

    followers = models.Follows.objects.values('user_two_id').filter(user_one=user)







    posty = models.Post.objects.filter(user=user)

    ret_list = []

    for follower in followers:

        curr_dict = {
            'follower_name': follower.user_two.name,

        }

        sub_posts = models.Post.objects.filter(user=follower.user_two)

        post_list = []
        for post_item in sub_posts:
            post_list.append(
                {
                    'post_name': post_item.post_title,
                    'post_title':post_item.post_text,
                    'post_votes':post_item.post_votes,
                    'post_diary':post_item.diary.diary_name,


                }
            )

        curr_dict['items'] = item_list

        ret_list.append(curr_dict)

    return HttpResponse(
        json.dumps(
            {
                'subscriptions': ret_list
            }
        )
    )
