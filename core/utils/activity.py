from users.models import UserActivity
from django.utils import timezone

def track_activity(user, field):
    today = timezone.now().date()
    activity, created = UserActivity.objects.get_or_create(
        user=user,
        date=today
    )
    if field == "open":
        activity.opens_count += 1
    elif field == "login":
        activity.logins_count += 1
    activity.save()
