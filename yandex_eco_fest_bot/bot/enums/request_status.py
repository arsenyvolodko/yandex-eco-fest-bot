from django.db.models import TextChoices


class RequestStatus(TextChoices):
    PENDING = "pending", "на проверке"
    DECLINED = "declined", "отклонено"
    ACCEPTED = "accepted", "засчитано"
