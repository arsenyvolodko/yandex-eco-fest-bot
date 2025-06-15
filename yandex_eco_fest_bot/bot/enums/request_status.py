from django.db.models import TextChoices


class RequestStatus(TextChoices):
    PENDING = "pending", "На проверке ⏳"
    DECLINED = "declined", "Отклонено ❌"
    ACCEPTED = "accepted", "Принято ✅"
