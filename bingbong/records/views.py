from decimal import Decimal
import json
from django.http import Http404
from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from .models import *
from accounts.models import Mypage
from .serializers import *
from goals.models import *
from datetime import datetime, date, timezone, timedelta

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

class RecordsView(APIView):
  def post(self, request):
    if not request.user.is_authenticated:
      return Response({"message": "권한이 없습니다."},status=status.HTTP_400_BAD_REQUEST)

    request_data = request.data
    parsed_data = json.dumps(request_data)
    parsed_data = json.loads(parsed_data)
    date_str = parsed_data['date']
    date_time = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    nine_hours = timedelta(hours=9)
    new_date = date_time + nine_hours
    
    #new_date = date.isoformat()

    # date_obj = datetime.strptime(new_date, '%Y-%m-%dT%H:%M:%S.%fZ')
    # date_obj = date_obj.replace(tzinfo=timezone.utc)
    parsed_data = request_data['records']

    
    year  = new_date.year
    month = new_date.month
    day   = new_date.day

    year  = int(year)
    month = int(month)
    day   = int (day)

    try:
      record = get_object_or_404(Record, user=request.user, year=year, month=month, day=day)
      return Response({"message": "이미 존재하는 기록입니다. 기록을 수정해주세요.", "record_id": record.pk}, status=status.HTTP_400_BAD_REQUEST)
    except Http404:

      soju_record = Decimal(0.0)
      beer_record = Decimal(0.0)
      mak_record  = Decimal(0.0)
      wine_record = Decimal(0.0)

      for selection in parsed_data:
        amount = selection['amount']
        if selection['drink'] == '소주':
          soju_record += Decimal(soju[amount])

        elif selection['drink'] == '맥주':
          beer_record += Decimal(beer[amount])

        elif selection['drink'] == '막걸리':
          mak_record += Decimal(mak[amount])

        else:
          wine_record += Decimal(wine[amount])
      
      request_date = date(year, month, day)
      days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
      weekday = request_date.weekday()

      user = request.user
      user_id = user.id
      data = {
        "user": user_id,
        "year": year,
        "month": month,
        "day": day,
        "dow": days[weekday],
        #"total_record": soju_record+beer_record+mak_record+wine_record,
        "soju_record": soju_record,
        "beer_record": beer_record,
        "mak_record": mak_record,
        "wine_record": wine_record
      }
      
      records = Record.objects.filter(user=request.user, year=year, month=month)
      record_count = records.count()
      serializer = RecordSerializer(data=data)
      if serializer.is_valid():
        serializer.save()

        # return Response(data, status=status.HTTP_201_CREATED)
        record = get_object_or_404(Record, user=request.user, year=year, month=month, day=day)
        user_page = get_object_or_404(Mypage, user=request.user)
        total_record = Decimal(0.0)
        total_record = Decimal(record.soju_record)+Decimal(record.beer_record)+Decimal(record.mak_record)+Decimal(record.wine_record)
        data = {
          "user": user_page.nickname,
          "year": record.year,
          "month": record.month,
          "day": record.day,
          "dow": record.dow,
          "record_id"   : record.pk,
          "record_count": record_count + 1,
          "total_record": total_record
          }

        return Response(data, status=status.HTTP_201_CREATED)
      else:
        return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)
      
  def get(self, request):
    year = int(request.GET['year'])
    month = int(request.GET['month'])
    day = int(request.GET['day'])
    record = get_object_or_404(Record, user=request.user, year=year, month=month, day=day)
    serializer = RecordSerializer(record, many=False)
    user_page = get_object_or_404(Mypage, user=request.user)
    total_record = Decimal(0.0)
    total_record = Decimal(record.soju_record)+Decimal(record.beer_record)+Decimal(record.mak_record)+Decimal(record.wine_record)
    data = {
        "user": user_page.nickname,
        "year": record.year,
        "month": record.month,
        "day": record.day,
        "dow": record.dow,
        "record_id"   : record.pk,
        "total_record": total_record,
        "soju_record": record.soju_record,
        "beer_record": record.beer_record,
        "mak_record": record.mak_record,
        "wine_record": record.wine_record
    }

    return Response(data, status=status.HTTP_201_CREATED)

  def delete(self, request):
    if not request.user.is_authenticated:
      return Response({"message": "권한이 없습니다."})

    year = int(request.GET['year'])
    month = int(request.GET['month'])
    day = int(request.GET['day'])

    record = get_object_or_404(Record, user=request.user, year=year, month=month, day=day)
    if request.user == record.user:
      record.delete()
      return Response({"message": "삭제되었습니다."}, status=status.HTTP_200_OK)
    else:
      return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)


class RecordView(APIView):
  
  
  def patch(self, request, record_id):
    if not request.user.is_authenticated:
      return Response({"message": "수정 권한이 없습니다."})

    record = get_object_or_404(Record, pk=record_id)
    
    if record.user != request.user:
      return Response({"message": "권한이 없습니다."})
    
    request_data = request.data
    parsed_data = json.dumps(request_data)
    parsed_data = json.loads(parsed_data)
    parsed_data = request_data['records']

    soju_record = Decimal(0.0)
    beer_record = Decimal(0.0)
    mak_record  = Decimal(0.0)
    wine_record = Decimal(0.0)

    for selection in parsed_data:
      amount = selection['amount']
      if selection['drink'] == '소주':
        soju_record += Decimal(soju[amount])

      elif selection['drink'] == '맥주':
        beer_record += Decimal(beer[amount])

      elif selection['drink'] == '막걸리':
        mak_record += Decimal(mak[amount])

      else:
        wine_record += Decimal(wine[amount])
    
    data = {
        "soju_record": soju_record,
        "beer_record": beer_record,
        "mak_record": mak_record,
        "wine_record": wine_record
      }

    serializer = RecordPatchSerializer(record, data=data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    serializer.save()

    record = get_object_or_404(Record, user=request.user, pk=record_id)
    user_page = get_object_or_404(Mypage, user=request.user)
    records = Record.objects.filter(user=request.user, year=record.year, month=record.month)
    record_count = records.count()
    total_record = Decimal(0.0)

    total_record = Decimal(record.soju_record) + Decimal(record.beer_record) + Decimal(record.mak_record) + Decimal(record.wine_record)

    data = {
      "user": user_page.nickname,
      "year": record.year,
      "month": record.month,
      "day": record.day,
      "dow": record.dow,
      "record_id": record.id,
      "record_count": record_count,
      "total_record": total_record
    }

    return Response(data, status=status.HTTP_200_OK)

  
  