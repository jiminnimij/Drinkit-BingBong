from rest_framework import serializers
from .models import *

class RecordSerializer(serializers.ModelSerializer):
  class Meta:
    model = Record
    fields = ['user', 'year', 'month', 'day', 'dow', 'soju_record', 'beer_record', 'mak_record', 'wine_record']



class RecordPatchSerializer(serializers.ModelSerializer):
  class Meta:
    model = Record
    fields = ['soju_record', 'beer_record', 'mak_record', 'wine_record']