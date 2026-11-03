from django.contrib.contenttypes.models import ContentType

from activity.models import ActivityLog


def get_client_ip(request):

    if not request:
        return None

    # Do not blindly trust X-Forwarded-For.
    # Configure trusted proxy handling if needed.
    return request.META.get('REMOTE_ADDR')


def log_activity(request, action, description, instance=None, changes=None):

    user = None

    if request and request.user.is_authenticated:
        user = request.user

    content_type = None
    object_id = None
    object_repr = ''

    if instance is not None:
        content_type = ContentType.objects.get_for_model(
            instance,
            for_concrete_model=False
        )

        object_id = str(instance.pk)
        object_repr = str(instance)[:255]

    return ActivityLog.objects.create(

        user=user,

        action=action,

        description=description,

        content_type=content_type,

        object_id=object_id,

        object_repr=object_repr,

        changes=changes or {},

        ip_address=get_client_ip(request),

        user_agent=(
            request.META.get('HTTP_USER_AGENT', '')
            if request else ''
        ),

        path=request.path if request else '',

        method=request.method if request else '',
    )