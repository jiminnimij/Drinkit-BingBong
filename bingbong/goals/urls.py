from django.urls import path, include,re_path
from .views import *

app_name = 'goals'

urlpatterns = [
  path('', GoalView.as_view(), name='goal-view'),
  path('social/', SocialView.as_view(), name='social-view'),
  path('social/<int:friend_id>', FriendView.as_view(), name='friend-view'),
  path('social/cheer/<int:friend_id>', CheerView.as_view(), name='cheer-view'),
  # re_path(r'^webpush/', include('webpush.urls')),
]