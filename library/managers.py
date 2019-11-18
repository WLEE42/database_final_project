from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, uemail, password=None, **extra_fields):
        if not uemail:
            raise ValueError('The given email must be set')
        uemail = self.normalize_email(uemail)
        user = self.model(uemail=uemail, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, uemail, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(uemail, password, **extra_fields)
