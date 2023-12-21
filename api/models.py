from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User


class FriendRequest(models.Model):
    request_id = models.CharField(max_length=200, unique=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_requests"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_requests"
    )
    status = models.CharField(
        max_length=20,
        default="PENDING",
        choices=[
            ("PENDING", "Pending"),
            ("ACCEPTED", "Accepted"),
            ("REJECTED", "Rejected"),
        ],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.status}"

    class Meta:
        db_table = "friend_request"
