from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from .models import *
from .serializers import *
from datetime import datetime, date
import random
from .serializers import TestHistorySerializer


# Create your views here.
class TestStartView(APIView):
  def get(self, request):
    if not request.user.is_authenticated:
      return Response({"message": "로그인이 필요합니다."},status=status.HTTP_400_BAD_REQUEST)

    q_list = TestQuestion.objects.all()
    q_list = list(q_list)
    random_q = random.sample(q_list, 4)

    q1 = random_q[0]
    q2 = random_q[2]
    q3 = random_q[3]
    q4 = random_q[3]
    
    user = request.user
    user_id = user.id

    date = datetime.now().date()

    data = {
      "user": user_id,
      "date": date,
      "q1": q1.id,
      "q2": q2.id,
      "q3": q3.id,
      "q4": q4.id
    }
    

    serializer = TestResultSerializer(data=data)
    if serializer.is_valid():
      instance = serializer.save()
      pk = instance.pk
      question = get_object_or_404(TestQuestion, pk=q1.id)
      data = {
        "pk": pk,
        "stage": instance.stage,
        "q1": question.question
      }
      return Response(data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
class TestAnswerView(APIView):
  def get(self, request, pk):
    test_result = get_object_or_404(TestResult, pk=pk)

    if request.user != test_result.user:
      return Response({"message": "권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

    if test_result.stage == 2:
      question = get_object_or_404(TestQuestion, pk=test_result.q2.id)
      data = {
      "pk": pk,
      "stage": test_result.stage,
      "q2": question.question
      }
      return Response(data, status=status.HTTP_200_OK)

    elif test_result.stage == 3:
      question = get_object_or_404(TestQuestion, pk=test_result.q3.id)
      data = {
      "pk": pk,
      "stage": test_result.stage,
      "q3": question.question
      }
      return Response(data, status=status.HTTP_200_OK)

    elif test_result.stage == 4:
      question = get_object_or_404(TestQuestion, pk=test_result.q4.id)
      data = {
      "pk": pk,
      "stage": test_result.stage,
      "q4": question.question
      }
      return Response(data, status=status.HTTP_200_OK)
    else:
      return Response({'error': 'Invalid stage'}, status=status.HTTP_400_BAD_REQUEST)


  def patch(self, request, pk):
    test_result = get_object_or_404(TestResult, pk=pk)

    if request.user != test_result.user:
      return Response({"message": "권한이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
    
    answer = int(request.data.get('answer'))

    if test_result.stage == 1:
      test_result.stage += 1
      if test_result.q1.answer == answer:
        test_result.a1 = True
      else:
        test_result.a1 = False
      update = {
        "a1": test_result.a1
      }

      serializer = TestAnswerSerializer(test_result, data=update)
      if serializer.is_valid():
        instance = serializer.save()
        pk = instance.pk
        data = {
          "pk": pk,
          "stage": instance.stage - 1,
          "result": "정답입니다!" if test_result.a1 else "오답입니다 :("
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif test_result.stage == 2:
      test_result.stage += 1
      if test_result.q2.answer == answer:
        test_result.a2 = True
      else:
        test_result.a2 = False
      update = {
        "a2": test_result.a2
      }

      serializer = TestAnswerSerializer(test_result, data=update)
      if serializer.is_valid():
        instance = serializer.save()
        pk = instance.pk
        data = {
          "pk": pk,
          "stage": instance.stage - 1,
          "result": "정답입니다!" if test_result.a2 else "오답입니다 :("
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif test_result.stage == 3:
      test_result.stage += 1
      if test_result.q3.answer == answer:
        test_result.a3 = True
      else:
        test_result.a3 = False
      update = {
        "a3": test_result.a3
      }

      serializer = TestAnswerSerializer(test_result, data=update)
      if serializer.is_valid():
        instance = serializer.save()
        pk = instance.pk
        data = {
          "pk": pk,
          "stage": instance.stage -1,
          "result": "정답입니다!" if test_result.a3 else "오답입니다 :("
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif test_result.stage == 4:
      if test_result.q4.answer == answer:
        test_result.a4 = True
      else:
        test_result.a4 = False
      score = test_result.a1 + test_result.a2 + test_result.a3 + test_result.a4
      score = score * 25
      if score <= 25:
        level = 3 # 취함
      elif score <= 75:
        level = 2 # 알딸딸 
      else:
        level = 1 # 멀쩡

      update = {
        "a4": test_result.a4,
        "score": score,
        "level": level
      }

      serializer = TestAnswerSerializer(test_result, data=update)
      if serializer.is_valid():
        instance = serializer.save()
        pk = instance.pk

        data = {
          "pk": pk,
          "stage": instance.stage,
          "result": "정답입니다!" if test_result.a4 else "오답입니다 :("
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    else:
      return Response({'error': 'Invalid stage'}, status=status.HTTP_400_BAD_REQUEST)
    
class TestResultView(generics.RetrieveAPIView):
    serializer_class = TestResultSerializer

    def get(self, request, pk):
        test_result = get_object_or_404(TestResult, pk=pk)

        # 각 질문에 대한 결과와 정답률, 레벨 설명 계산
        level_description = self.get_level_description(test_result.level)
        
        result_data = {
            "q1_result": "정답" if test_result.a1 is True else "오답",
            "q2_result": "정답" if test_result.a2 is True else "오답",
            "q3_result": "정답" if test_result.a3 is True else "오답",
            "q4_result": "정답" if test_result.a4 is True else "오답",
            "level": test_result.level,
            "level_description": level_description,
            "score": test_result.score
        }

        return Response(result_data, status=status.HTTP_200_OK)

    def get_level_description(self, level):
        if level == 1:
            return "멀쩡"
        elif level == 2:
            return "알딸딸"
        elif level == 3:
            return "취함"

class TestHistoryView(generics.ListAPIView):
    serializer_class = TestHistorySerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return TestResult.objects.none()  # 빈 쿼리셋 반환
        return TestResult.objects.filter(user=user).order_by('-date')  # 사용자가 수행한 테스트 결과를 날짜순으로 정렬