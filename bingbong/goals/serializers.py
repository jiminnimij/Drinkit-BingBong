from rest_framework import serializers
from .models import *

class GoalSerializer(serializers.ModelSerializer):
  class Meta:
    model = Goal
    fields = ['user', 'year','month','soju_goal', 'beer_goal', 'mak_goal', 'wine_goal', 'cheer']
  
class GoalPatchSerializer(serializers.ModelSerializer):
  class Meta:
    model = Goal
    fields = ["soju_goal", 'beer_goal', 'mak_goal', 'wine_goal']