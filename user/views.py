from json.decoder import JSONDecodeError

import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount

from user.models import User
from user.serializers import QuestionSerializer
from santa_myojeong_be.settings import KAKAO_REST_API_KEY, KAKAO_CALLBACK_URI


BASE_URL = 'http://127.0.0.1:8000/'


def login_test(request):
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code"
    )


class UserAuthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')
        token = self._get_token(code)
        email = self._get_email(token)

        response = self._sign_in(email, token, code)

        return response

    def _get_token(self, code: str):
        token_req = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={KAKAO_REST_API_KEY}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}")
        token_req_json = token_req.json()
        error = token_req_json.get("error")
        if error is not None:
            raise JSONDecodeError(error)
        
        access_token = token_req_json.get("access_token")

        return access_token
    
    def _get_email(self, access_token: str):
        profile_request = requests.get("https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
        profile_json = profile_request.json()
        error = profile_json.get("error")
        if error is not None:
            raise JSONDecodeError(error)
        
        kakao_account = profile_json.get('kakao_account')
        email = kakao_account.get('email')

        return email
    
    def _sign_in(self, email: str, access_token: str, code: str):
        try:
            user = User.objects.get(email=email)
            # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러, 맞으면 로그인
            # 다른 SNS로 가입된 유저
            social_user = SocialAccount.objects.get(user=user)
            if social_user is None:
                return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
            if social_user.provider != 'kakao':
                return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 기존에 Kakao 가입된 유저
            response = self._get_sign_in_response(access_token, code, False)

            return response
            
        except User.DoesNotExist:
            # 가입
            response = self._get_sign_in_response(access_token, code, True)

            return response
        
    def _get_sign_in_response(self, access_token: str, code: str, is_signup: bool):
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}user/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status != 200:
            return JsonResponse({'err_msg': f"failed to {'signup' if is_signup else 'signin'}"}, status=accept_status)
        accept_json = accept.json()

        refresh_token = accept.headers['Set-Cookie'].split('refresh_token=')[-1].split(';')[0]

        COOKIE_MAX_AGE = 3600 * 24 * 14 # 14 days

        response = {
            'access_token': accept_json['access'],
            'is_signup': is_signup
        }
        response_with_cookie = JsonResponse(response)
        response_with_cookie.set_cookie('refresh_token', refresh_token, max_age=COOKIE_MAX_AGE, httponly=True, samesite='Lax')

        return response_with_cookie


class KakaoLoginView(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI


class QuestionView(APIView):
    def get(self, request):
        id_ = request.GET.get('id')

        try:
            requested_user = User.objects.get(id=id_)
        except User.DoesNotExist:
            return Response({'message': '존재하지 않는 유저입니다.'}, status=status.HTTP_404_NOT_FOUND)
        
        serialized_data = QuestionSerializer(requested_user).data

        return Response(serialized_data, status=status.HTTP_200_OK)
