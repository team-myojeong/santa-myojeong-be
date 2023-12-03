import random

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.db import transaction

from user.models import DefaultQuestion


class KakaoAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        with transaction.atomic():
            QUESTION_COUNT = 3

            user = super().save_user(request, sociallogin, form)

            oauth_data = sociallogin.account.extra_data
            user.nickname = oauth_data['kakao_account']['profile']['nickname']

            question_list = list(DefaultQuestion.objects.filter(is_delete=False))
            for i, q in enumerate(random.sample(question_list, QUESTION_COUNT)):
                setattr(user, f'question{i + 1}', q.question)

            user.save()

        return user
