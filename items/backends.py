from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom authentication backend to allow case-insensitive login via email.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            # Case-insensitive search by email
            user = UserModel.objects.get(email__iexact=username)
        except UserModel.DoesNotExist:
            try:
                # Fallback to case-insensitive search by username
                user = UserModel.objects.get(username__iexact=username)
            except UserModel.DoesNotExist:
                return None
            except UserModel.MultipleObjectsReturned:
                user = UserModel.objects.filter(username__iexact=username).order_by('id').first()
        except UserModel.MultipleObjectsReturned:
            # In case multiple users exist with the same email (should be unique though)
            user = UserModel.objects.filter(email__iexact=username).order_by('id').first()
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
