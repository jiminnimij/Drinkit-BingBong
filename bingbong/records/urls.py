from django.urls import path, include
from .views import *

app_name = 'records'

urlpatterns = [
  path('', RecordsView.as_view(), name='records-view'),
  path('<int:record_id>', RecordView.as_view(), name='record-view'),
]