from django.urls import path#, include
from .views import *
# from rest_framework.routers import DefaultRouter


app_name = 'accounts'
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('mypage/', MypageView.as_view()),
    path('add-friend/', AddFriendView.as_view(), name='add-friend'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('delete/', DeleteView.as_view(), name='delete-account'),
    path('delete-friend/<int:friend_id>', DeleteFriendView.as_view(), name='delete-friend'),
    path('friends/', FriendsView.as_view()),
    path('save_timer/', TimerViewSet.as_view({'post': 'save_timer'}), name='timer-save'),
    path('timer_state/', TimerViewSet.as_view({'get': 'timer_state'}), name='timer-state'),

]