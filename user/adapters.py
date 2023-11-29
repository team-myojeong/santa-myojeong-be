from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.db import transaction


class KakaoAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        with transaction.atomic():
            user = super().save_user(request, sociallogin, form)

            oauth_data = sociallogin.account.extra_data
            user.nickname = oauth_data['kakao_account']['profile']['nickname']
            user.save()

        return user
