import copy
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated

from recipes.models import Recipe, Review
from .serializers import (
    ReviewSerializer, UpdateReviewSerializer, UserSerializer, UserLoginSerializer
)
from .constant import RESPONSE_SUCSSS, RESPONSE_FAILED
from .utils import success_response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authentication import authenticate
# Create your views here.

def home(request):
    return HttpResponse("Hello Home")


class UserSignupAPI(CreateAPIView):
    serializer_class = UserSerializer

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Create a new user",
        request_body=UserSerializer,
        responses={201: UserSerializer}
    )
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response = copy.deepcopy(RESPONSE_SUCSSS)
            response["message"] = "User Created Sussfully"
            response["data"] = serializer.data
            return Response(response, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as ex:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["data"] = request.data
            response["message"] = str(ex)
            return Response({"error": str(ex), "request_data":request.data}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPI(CreateAPIView):
    serializer_class = UserLoginSerializer

    @swagger_auto_schema(
        tags=['Authentication'],
        operation_description="Login User",
        request_body=UserLoginSerializer,
        responses={200: UserLoginSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Custom logic to authenticate user (e.g., using Django's built-in authenticate method)
        user = authenticate(request, username=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            response = copy.deepcopy(RESPONSE_SUCSSS)
            response["message"] = "Login Sussfully"
            response["data"] = {
                "user_info": user.get_user_data_for_response(),
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "Invalid credentials"
            response["data"] = request.data
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)
        

class ReviewRecipeAPI(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Reviews'],
        operation_description="Create a new review",
        request_body=ReviewSerializer,
        responses={201: ReviewSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(serializer.data, status=status.HTTP_201_CREATED)

# Retrieve and Update API
class ReviewDetailAPI(RetrieveUpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = UpdateReviewSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Reviews'],
        operation_description="Retrieve a review",
        responses={200: ReviewSerializer}
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return success_response(data=response.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['Reviews'],
        operation_description="Update a review",
        request_body=ReviewSerializer,
        responses={200: ReviewSerializer}
    )
    def put(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, status=status.HTTP_200_OK)
