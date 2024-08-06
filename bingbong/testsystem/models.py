from django.db import models
from django.contrib.auth.models import User   #accounts 개발 전 user 모델 사용을 위한 import

class TestQuestion(models.Model):
  question = models.CharField(max_length=255)
  answer = models.IntegerField()

  def __str__(self):
    return str(self.pk)

class TestResult(models.Model):
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE
  ) #user
  date = models.DateField() #날짜
  stage = models.IntegerField(default=1) #테스트의 몇번째 문제를 푸는 중인지
  q1 = models.ForeignKey(TestQuestion, related_name="q1", null=True, on_delete=models.SET_NULL) #문제 1
  q2 = models.ForeignKey(TestQuestion, related_name="q2", null=True, on_delete=models.SET_NULL) #문제 2
  q3 = models.ForeignKey(TestQuestion, related_name="q3", null=True, on_delete=models.SET_NULL) #문제 3
  q4 = models.ForeignKey(TestQuestion, related_name="q4", null=True, on_delete=models.SET_NULL) #문제 4
  a1 = models.BooleanField(null=True) #문제 1 맞추면 True, 틀리면 False
  a2 = models.BooleanField(null=True) #문제 2 맞추면 True, 틀리면 False
  a3 = models.BooleanField(null=True) #문제 3 맞추면 True, 틀리면 False
  a4 = models.BooleanField(null=True) #문제 4 맞추면 True, 틀리면 False
  score = models.IntegerField(null=True) # 정답률
  level = models.IntegerField(null=True) # 취함 정도 1, 2, 3으로 입력되고 1은 멀쩡, 2는 알딸딸, 3은 취함을 의미

