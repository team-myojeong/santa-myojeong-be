from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    RABBITS = [
        (1, 'https://static.wixstatic.com/media/ea5e7b_9f2e827ced974561a73fcd5cfea6795c~mv2.png/v1/fill/w_184,h_286,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/1.png'),
    ]


    username = None
    first_name = None
    last_name = None
    email = models.EmailField(unique=True, max_length=255)

    nickname = models.CharField(null=True, max_length=10)
    gacha_ticket = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    rabbit = models.IntegerField(choices=RABBITS, default=1)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    

class UserLike(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    target_user = models.ForeignKey(User, related_name='target_user', on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
