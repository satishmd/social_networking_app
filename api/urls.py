from django.urls import path

from . import views

# import csrf_excempt
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path("signup/", views.SignupAPIView.as_view(), name="signup"),
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("fetch-users/", views.SearchUserAPIView.as_view(), name="get-users"),
    path(
        "send-friend-request/", views.SendFriendRequest.as_view(), name="friend_request"
    ),
    path(
        "send-friend-request/<str:request_id>/",
        views.SendFriendRequest.as_view(),
        name="Update_friend_request",
    ),
]
