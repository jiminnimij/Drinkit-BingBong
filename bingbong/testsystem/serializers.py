from rest_framework import serializers
from .models import *

class TestResultSerializer(serializers.ModelSerializer):
  class Meta:
    model = TestResult
    fields = '__all__'

class TestAnswerSerializer(serializers.ModelSerializer):
  class Meta:
    model = TestResult
    fields = ['a1', 'a2', 'a3', 'a4', 'score',  'level']
  
class TestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ['date', 'score', 'level']