from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from .serializers import (
    UserSerializer,
    LoginSerializer,
    RegisterSerializer,
    FriendRequestSerializer,
)
from django.db import IntegrityError
from django.contrib.auth.models import User
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from uuid import uuid4
from .models import FriendRequest
from ratelimit.mixins import RatelimitMixin
from ratelimit.exceptions import Ratelimited


class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle HTTP POST requests.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: The HTTP response object.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data["email"].lower())
        if user and user.check_password(serializer.validated_data["password"]):
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "user": UserSerializer(user).data})
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class SignupAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Registers a new user with the provided email, password, and username.

        Parameters:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing the user data if registration is successful, or an error message if registration fails.
        """
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = serializer.validated_data["email"].lower()
        password = serializer.validated_data["password"]
        username = serializer.validated_data["username"]

        email_check = User.objects.filter(email=email)
        username_check = User.objects.filter(username=username)

        if email_check:
            return Response(
                {"error": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if username_check:
            return Response(
                {"error": "User with this username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            email=email, password=password, username=username
        )
        return Response({"user": UserSerializer(user).data})


# create a class view to search the user by email or name
class SearchUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle HTTP POST requests.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object containing a list of user information.
        """
        name = request.data.get("name")

        # check weather name is email type or username using regex

        if re.match(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", name):
            users = User.objects.filter(email__iexact=name)
        else:
            users = User.objects.filter(username__icontains=name)

        users_list = [
            {"id": user.id, "username": user.username, "email": user.email}
            for user in users
        ]

        return Response(users_list)


class SendFriendRequest(RatelimitMixin, APIView):
    ratelimit_key = "user"  # You can use 'ip' or any other key
    ratelimit_rate = "3/m"  # 5 requests per minute
    ratelimit_method = "POST"  # Apply rate limit only for POST requests
    ratelimit_block = True  # Block requests that exceed the limit

    def get(self, request):
        """
        Retrieves a list of friends or pending friend requests for a given user.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            Response: A response object containing a list of friends or pending friend requests.
        """
        get_params = request.GET
        user_req = User.objects.get(username=get_params.get("user"))
        if get_params.get("details") == "friends":
            friends = FriendRequest.objects.filter(
                sender=user_req.id, status="ACCEPTED"
            )
            friends_list = [
                {"name": friend.receiver.username, "email": friend.receiver.email}
                for friend in friends
            ]
            return Response(friends_list)
        friend_req_pend = FriendRequest.objects.filter(
            receiver=user_req.id, status="PENDING"
        )
        friend_req_pend_list = [
            {"name": req.sender.username, "email": req.sender.email}
            for req in friend_req_pend
        ]
        return Response(friend_req_pend_list)

    def post(self, request):
        """
        Sends a friend request from the sender to the receiver.

        Parameters:
            request (Request): The HTTP request object.

        Returns:
            Response: The HTTP response object with the result of the friend request.
        """

        try:
            data = request.data
            sender_details = User.objects.get(username=data.get("sender"))
            receiver_details = User.objects.get(username=data.get("receiver"))

            # Check if a friend request already exists
            existing_request = FriendRequest.objects.filter(
                sender=sender_details.id, receiver=receiver_details.id
            )
            if existing_request.exists():
                return Response({"message": "Friend request already sent."}, status=400)

            request_id = str(uuid4())
            serializer = FriendRequestSerializer(
                data={
                    "sender": sender_details.id,
                    "receiver": receiver_details.id,
                    "request_id": request_id,
                }
            )

            if not serializer.is_valid():
                return Response(
                    {"status": "error", "data": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            return Response(
                {
                    "status": "success",
                    "message": "Friend request sent",
                    "friend_req_id": request_id,
                }
            )
        except:
            Response(
                {
                    "status": "error",
                    "message": "you can only send 3 requests for minute.",
                }
            )

    def patch(self, request, request_id=None):
        """
        Update the status of a friend request.

        Parameters:
            request (Request): The HTTP request object.
            request_id (int, optional): The ID of the friend request to update. Defaults to None.

        Returns:
            Response: The HTTP response object containing the updated friend request status.
        """

        data = request.data
        frequest_details = FriendRequest.objects.get(request_id=request_id)

        if frequest_details.status == "ACCEPTED" or "REJECTED":
            return Response({"message": f"Friend request already {frequest_details.status}."}, status=400)
        serializer = FriendRequestSerializer(frequest_details, data=data, partial=True)

        if not serializer.is_valid():
            return Response(
                {"status": "error", "data": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        return Response(
            {
                "status": "success",
                "message": f"Friend request status updated as {data.get('status')}",
            }
        )
