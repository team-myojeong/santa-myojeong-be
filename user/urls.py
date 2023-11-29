from django.urls import path
from user import views

urlpatterns = [
    path('test/login/', views.login_test),
    path('login/', views.UserAuthView.as_view()),
    path('login/finish/', views.KakaoLoginView.as_view()),
]