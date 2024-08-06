from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from .models import Goal
from .serializers import *
from records.models import *
from records.serializers import *
from accounts.models import *
from datetime import datetime
from decimal import Decimal
from webpush import send_user_notification
import json
# from permissions import CustomReadOnly # modelviewset으로 바꿀지 고민 중...
# https://newbiecs.tistory.com/316 참고해서 공부하고 코드 변경해보기

soju = {
  "1잔 (50ml)": 1.0,
  "2잔": 2.0,
  "3잔": 3.0,
  "4잔": 4.0,
  "5잔": 5.0,
  "6잔": 6.0,
  "7잔": 7.0,
  "1병": 7.5,
  "1병 반": 11.25,
  "2병": 15,
  "2병 반": 18.75,
  "3병": 22.5,
  "3병 반": 26.25
}

beer = {
  "1잔 (200ml)": 1.0,
  "2잔": 2.0,
  "1병": 2.5,
  "1병 반": 3.75,
  "2병": 5,
  "2병 반": 6.25,
  "3병": 7.5,
  "3병 반": 8.75,
  "4병": 10,
  "4병 반": 11.25,  
}

mak = {
  "1사발 (250ml)": 1.0,
  "2사발": 2.0,
  "1병": 3.0,
  "1병 반": 4.5,
  "2병": 6.0,
  "2병 반": 7.5,
  "3병": 9.0,
  "3병 반":10.5,
  "4병":12.0,
  "4병 반":13.5,
}

wine = {
  "1잔 (150ml)": 1.0,
  "2잔": 2.0,
  "3잔": 3.0,
  "4잔": 4.0,
  "1병": 5.0,
  "1병 반": 7.5,
  "2병": 10.,
  "2병 반": 12.5,
  "3병": 15.0,
  "3병 반": 17.5,
  "4병": 20.0,
  "4병 반": 22.5,
}

class GoalView(APIView):
  def get(self, request):
    now = datetime.now()
    year = now.year
    month = now.month

    year = request.query_params.get('year', now.year)
    month = request.query_params.get('month', now.month)

    try:
      year = int(year)
      month = int(month)
    except ValueError:
      return Response({"message": "연도와 달은 정수여야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    user_id = user.id
    user_page = get_object_or_404(Mypage, user=user)
    # 없으면 목표가 전부 0이게 새로 생성
    if not Goal.objects.filter(user=user, year=year, month=month).exists():
      data = {
          "user":       user_id,
          "year":       year,
          "month":      month
          # 'soju_goal':  0,
          # 'beer_goal':  0,
          # 'mak_goal':   0,
          # 'wine_goal':  0
        }
      serializer = GoalSerializer(data=data)
      if serializer.is_valid():
        serializer.save()
      else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
    # 사용자의 목표 정보
    # 사용자 id, 목표 연도, 목표 월, 목표 소주량, 목표 맥주량, 목표 막걸리량, 목표 와인량, 목표 총 합
      
    goal = get_object_or_404(Goal, user=request.user, year=year, month=month)
    serializer = GoalSerializer(goal)
    goal = serializer.data
    user = goal['user']
    soju_goal = Decimal(goal['soju_goal'])
    beer_goal = Decimal(goal['beer_goal'])
    mak_goal = Decimal(goal['mak_goal'])
    wine_goal = Decimal(goal['wine_goal'])
    total_goal = soju_goal + beer_goal + mak_goal + wine_goal
    goal = {
      "total_goal": total_goal,
      "soju_goal": soju_goal,
      "beer_goal": beer_goal,
      "mak_goal": mak_goal,
      "wine_goal": wine_goal

    }
    

    # 현재까지 마신 잔수의 합
    date = []
    total_soju = Decimal('0.0')
    total_beer = Decimal('0.0')
    total_mak = Decimal('0.0')
    total_wine = Decimal('0.0')
    total_record = Decimal('0.0')

    records = Record.objects.filter(user=request.user, year=year, month=month)
    for a in records:
      date.append({'day': a.day, 'id': a.id})
      total_soju += a.soju_record
      total_beer += a.beer_record
      total_mak += a.mak_record
      total_wine += a.wine_record
    total_record = total_soju + total_beer + total_mak + total_wine
    
    record = {
      "total_record":total_record,
      "total_soju":total_soju,
      "total_beer":total_beer,
      "total_mak":total_mak,
      "total_wine":total_wine
    }

    # 남은 잔수의 합
    remainder = Decimal(total_goal) - total_record
    if total_goal == 0:
      percentage = 0
    else:
      percentage = total_record/total_goal * 100

    data ={
      "year": year,
      "month": month,
      "before":{
          "year": year-1 if month == 1 else year,
          "month": 12 if month == 1 else month-1
        },
      "user": user_page.nickname,
      "user_id":user_id,
      "goal": goal,
      "record": {
        "date": date,
        "record_alcohol": record
      },
      "percentage":percentage
      ,
      "remainder": remainder
    }

    return Response(data, status=status.HTTP_200_OK)
  

    

  def patch(self, request):
    if not request.user.is_authenticated:
      return Response({"message": "수정 권한이 없습니다."})
    now = datetime.now()
    year = now.year
    month = now.month
    user = request.user
    user_page = get_object_or_404(Mypage, user=user)

    request_data = request.data
    parsed_data = json.dumps(request_data)
    parsed_data = json.loads(parsed_data)
    parsed_data = request_data['selections']

    soju_goal = Decimal(0.0)
    beer_goal = Decimal(0.0)
    mak_goal  = Decimal(0.0)
    wine_goal = Decimal(0.0)

    for selection in parsed_data:
      amount = selection['amount']
      drink_type = selection['drink']

      if drink_type == '소주':
        soju_goal += Decimal(soju.get(amount, 0.0))
      elif drink_type == '맥주':
        beer_goal += Decimal(beer.get(amount, 0.0))
      elif drink_type == '막걸리':
        mak_goal += Decimal(mak.get(amount, 0.0))
      elif drink_type == '와인':
        wine_goal += Decimal(wine.get(amount, 0.0))
      else:
        continue
    
    data = {
      "soju_goal": soju_goal,
      "beer_goal": beer_goal,
      "mak_goal": mak_goal,
      "wine_goal": wine_goal
    }

    goal = get_object_or_404(Goal, user=request.user, year=year, month=month)
    
    if goal.user == request.user:
      serializer = GoalPatchSerializer(goal, data=data)#request.data)
      if serializer.is_valid():
        serializer.save()
      else: return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      goal = get_object_or_404(Goal, user=request.user, year=year, month=month)
      serializer = GoalSerializer(goal)
      goal = serializer.data
      user = goal['user']
      soju_goal = Decimal(goal['soju_goal'])
      beer_goal = Decimal(goal['beer_goal'])
      mak_goal = Decimal(goal['mak_goal'])
      wine_goal = Decimal(goal['wine_goal'])
      total_goal = soju_goal + beer_goal + mak_goal + wine_goal
      goal = {
        "total_goal": total_goal,
        "soju_goal": soju_goal,
        "beer_goal": beer_goal,
        "mak_goal": mak_goal,
        "wine_goal": wine_goal
      }
    

      # 현재까지 마신 잔수의 합
      date = []
      total_soju = Decimal('0.0')
      total_beer = Decimal('0.0')
      total_mak = Decimal('0.0')
      total_wine = Decimal('0.0')
      total_record = Decimal('0.0')

      records = Record.objects.filter(user=request.user, year=year, month=month)
      for a in records:
        date.append({'day': a.day, 'id': a.id})
        total_soju += a.soju_record
        total_beer += a.beer_record
        total_mak += a.mak_record
        total_wine += a.wine_record
      total_record = total_soju + total_beer + total_mak + total_wine
    
      record = {
        "total_record":total_record,
        "total_soju":total_soju,
        "total_beer":total_beer,
        "total_mak":total_mak,
        "total_wine":total_wine
      }

      # 남은 잔수의 합
      remainder = Decimal(total_goal) - total_record
      if total_goal == 0:
        percentage = 0
      else:
        percentage = total_record/total_goal * 100
      data ={
        "year":year,
        "month":month,
        "user": user_page.nickname,
        "goal": goal
      }
      return Response(data, status=status.HTTP_200_OK)
    else:
      return Response({"message": "수정 권한이 없습니다."})
    
  def delete(self, request):
    now = datetime.now()
    year = now.year
    month = now.month
    user = request.user

    goal = get_object_or_404(Goal, user=request.user, year=year, month=month)
    if request.user == goal.user:
      goal.delete()
      return Response({"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT)
    else:
      return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

class SocialView(APIView):
  def get(self, request):
    now   = datetime.now()
    year  = now.year
    month = now.month
    day   = now.day

    #목표
    goal, created = Goal.objects.get_or_create(user=request.user, year=year, month=month)
    goal_serializer = GoalSerializer(goal)
    goal_data = goal_serializer.data
    
    #사용자 id, 응원
    user = request.user
    user_id = user.id
    cheer = goal_data['cheer']
    user_page = get_object_or_404(Mypage, user=user)
    period = 0
    while True:
      month  = month-1 if month != 1 else 12
      year   = year if month != 1 else year -1

      total_goal = Decimal(0.0)
      total_record = Decimal(0.0)

      try:
        goal = Goal.objects.get(user=user, year=year, month=month)
      except Goal.DoesNotExist:
        break

      else:
        total_goal = goal.soju_goal+goal.beer_goal+goal.mak_goal+goal.wine_goal
        records = Record.objects.filter(user=request.user, year=year, month=month)
        for record in records:
          total_record += record.soju_record+record.beer_record+record.mak_record+record.wine_record

        if total_goal>=total_record:
          period += 1
        else:
          break

    #사용자 설정 목표
    soju_goal = Decimal(goal_data['soju_goal'])
    beer_goal = Decimal(goal_data['beer_goal'])
    mak_goal  = Decimal(goal_data['mak_goal'])
    wine_goal = Decimal(goal_data['wine_goal'])

    #기록
    year  = now.year
    month = now.month
    records = Record.objects.filter(user=request.user, year=year, month=month)
    soju_record = Decimal(0.0)
    beer_record = Decimal(0.0)
    mak_record  = Decimal(0.0)
    wine_record = Decimal(0.0)

    for record in records:
      record_serializer = RecordSerializer(record)
      record_data = record_serializer.data
      soju_record += Decimal(record_data['soju_record'])
      beer_record += Decimal(record_data['beer_record'])
      mak_record  += Decimal(record_data['mak_record'])
      wine_record += Decimal(record_data['wine_record'])
    
    #목표 달성율
    soju = {
      "goal"        : soju_goal,
      "record"      : soju_record,
      "percentage"  : soju_record/soju_goal if soju_goal != 0 else 0
    }

    beer = {
      "goal"        : beer_goal,
      "record"      : beer_record,
      "percentage"  : beer_record/beer_goal if beer_goal != 0 else 0
    }

    mak = {
      "goal"        : mak_goal,
      "record"      : mak_record,
      "percentage"  : mak_record/mak_goal if mak_goal != 0 else 0
    }

    wine = {
      "goal"        : wine_goal,
      "record"      : wine_record,
      "percentage"  : wine_record/wine_goal if wine_goal != 0 else 0
    }

    # 친구의 달성률
    # user의 친구 리스트 불러오기
    # user의 친구 정보 리스트로 받기
    friends_list = []
    user = get_object_or_404(Mypage, user=request.user)
    for friend in user.friends.all():
      # user의 친구 정보로 친구의 목표 정보 가져오기
      user_friend = get_object_or_404(User, pk=friend.pk)
      friend_page = get_object_or_404(Mypage, user=user_friend)
      friend_total_goal = Decimal(0.0)

      goal, created = Goal.objects.get_or_create(user=user_friend, year=year, month=month)

      goal_serializer = GoalSerializer(goal)
      goal_data = goal_serializer.data
      friend_total_goal = Decimal(goal_data['soju_goal']) + Decimal(goal_data['beer_goal']) + Decimal(goal_data['mak_goal']) + Decimal(goal_data['wine_goal'])

      records = Record.objects.filter(user=user_friend, year=year, month=month)
      friend_total_record = Decimal(0.0)
      for record in records:
        record_serializer = RecordSerializer(record)
        record_data = record_serializer.data
        friend_total_record += Decimal(record_data['soju_record']) + Decimal(record_data['beer_record']) + Decimal(record_data['mak_record']) + Decimal(record_data['wine_record'])
      
      percentage = friend_total_record/friend_total_goal if friend_total_goal!=0 else 0
      
      friends_list.append({"friend_id":user_friend.id, "friend":friend_page.nickname, "goal": friend_total_goal, "record": friend_total_record, "percentage": percentage})
      # 각 친구의 목표 정보 밑 친구의 정보 {}에 저장하기
      # {"username": "유저 이름", "achievement":~~}
    # 반복문 돌면서 친구의 달성률 계산



    data = {
      "user"    : user_page.nickname,
      "period"  : period,
      "cheer"   : cheer,
      "soju"    : soju,
      "beer"    : beer,
      "mak"     : mak,
      "wine"    : wine,
      "friends" : friends_list
    }
    return Response(data, status=status.HTTP_200_OK)
  

class FriendView(APIView):
  def get(self, request, friend_id):
    now   = datetime.now()
    year  = now.year
    month = now.month
    day   = now.day

    friend         = get_object_or_404(User, pk=friend_id)
    friend_page    = get_object_or_404(Mypage, user=friend)
    friend_goal    = get_object_or_404(Goal, user=friend, year=year, month=month)
    friend_records = Record.objects.filter(user=friend, year=year, month=month)
    
    soju_record = Decimal(0.0)
    beer_record = Decimal(0.0)
    mak_record  = Decimal(0.0)
    wine_record = Decimal(0.0)

    for record in friend_records:
      soju_record += record.soju_record
      beer_record += record.beer_record
      mak_record  += record.mak_record
      wine_record += record.wine_record

    data = {
      "friend_id"   : friend.id,
      "friend_name" : friend_page.nickname,
      "soju_goal"   : friend_goal.soju_goal,
      "beer_goal"   : friend_goal.beer_goal,
      "mak_goal"    : friend_goal.mak_goal,
      "wine_goal"   : friend_goal.wine_goal,
      "soju_record" : soju_record,
      "beer_record" : beer_record,
      "mak_record"  : mak_record,
      "wine_record" : wine_record
      
    }
    return Response(data, status=status.HTTP_200_OK)

class CheerView(APIView):
  def post(self, request, friend_id):
    # request에서 입력받은 친구 정보로 해당 목표 모델 가져오기
    user = request.user
    user_page = get_object_or_404(Mypage, user = user)
    friend = get_object_or_404(User, pk=friend_id)
    friend_page = get_object_or_404(Mypage, user=friend)

    if friend_page not in user_page.friends.all():
      return Response({"message":"내 친구가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)

    now = datetime.now()
    year = now.year
    month = now.month

    # 목표 정보 중 cheer만 +1 하기
    goal = get_object_or_404(Goal, user=friend, year=year, month=month)
    goal.cheer += 1
    goal.save()

    # 친구에게 웹 푸시 알림가게 하기
    body_messeage = "{}({})님이 {}님께 음주 목표를 달성하면 좋겠다는 응원을 보냈어요. 건강한 음주 습관을 위해 이번 달도 화이팅!".format(user_page.nickname, user.email, friend_page.nickname)
    payload = {"head": "친구에게 응원을 받았어요!🎉",
              "body": body_messeage,
              "icon": "https://i.imgur.com/dRDxiCQ.png",
              "url": "http://127.0.0.1:8000/goals/" #배포하는 사이트의 url에 맞춰 변경 예정
              }
    payload = json.dumps(payload)

    send_user_notification(user=friend, payload=payload)

    return Response({"message": "응원을 보냈습니다.", "friend": friend_page.nickname}, status=status.HTTP_200_OK)
  