from django.urls import path, include
from .views import *

app_name = 'test'

urlpatterns = [
  path('', TestStartView.as_view(), name='test-view'),
  path('<int:pk>', TestAnswerView.as_view()),
  path('result/<int:pk>', TestResultView.as_view(), name='test-result'),
  path('history/', TestHistoryView.as_view(), name='test-history'),
]