"""
URL configuration for recipehub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import (
    home,
    UserSignupAPI,
    UserLoginAPI,
    ListCreateRecipeAPI,
    ReviewRecipeAPI,
    ReviewDetailAPI,
    ListUpdateDeleteRecipeAPI,
    
    
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('home', home, name='home'),
    path('signup', UserSignupAPI.as_view(), name='signup'),
    path('login', UserLoginAPI.as_view(), name='login'),
    path('recipe', ListCreateRecipeAPI.as_view(), name='create-recipe'),
    path('recipe/<int:pk>', ListUpdateDeleteRecipeAPI.as_view(), name='update-recipe'),
    path('reviews', ReviewRecipeAPI.as_view(), name='create-review'),
    path('reviews/<int:pk>', ReviewDetailAPI.as_view(), name='review-detail'),
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]
