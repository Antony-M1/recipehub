import copy
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.generics import CreateAPIView, GenericAPIView, RetrieveUpdateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView, DestroyAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.db.utils import IntegrityError
from .serializers import (
    UserSerializer, UserLoginSerializer, CreateRecipieSerializer, CreateRecipeSerializer2,
    ReviewSerializer, UpdateReviewSerializer, UpdateRecipeSerializer, AllReviewSerializer
)
from .models import (
    Recipe, Review
)
from .utils import success_response
from .constant import RESPONSE_SUCSSS, RESPONSE_FAILED, CustomPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authentication import authenticate
from rest_framework.permissions import IsAuthenticated
from django.db import connection

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
        responses={200: UserLoginSerializer},
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
        

class ListCreateRecipeAPI(ListCreateAPIView):
    
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipieSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Create Recipe",
        request_body=CreateRecipieSerializer,
        responses={201: CreateRecipieSerializer}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(serializer.data, status=status.HTTP_201_CREATED, message="Recipe Created Sussfully")

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="List Recipes"
    )
    def get(self, request):

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT trc.*, AVG(tr.rating) AS avg_rating
                FROM tabRecipe AS trc
                LEFT JOIN tabReview AS tr ON trc.id = tr.recipe_id
                GROUP BY trc.id;
            """)
            columns = [col[0] for col in cursor.description]
            recipes = [dict(zip(columns, row)) for row in cursor.fetchall()]

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(recipes, request)

        serializer = CreateRecipieSerializer(page, many=True)

        if page is not None:
            res = paginator.get_paginated_response(serializer.data)
            return success_response(data = res.data, status=status.HTTP_200_OK)
        return success_response(serializer.data, status=status.HTTP_200_OK)

    def get_page_size(self, request):
        page_size = self.pagination_class.page_size
        if 'page_size' in request.query_params:
            try:
                page_size = int(request.query_params['page_size'])
            except ValueError:
                pass
        return page_size


class ListUpdateDeleteRecipeAPI(RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = UpdateRecipeSerializer
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Update Recipe",
        request_body=UpdateRecipeSerializer,
        responses={201: UpdateRecipeSerializer}
    )
    def put(self, request, *args, **kwargs):
        recipe_user_id = Recipe.objects.get(id=kwargs['pk']).user_id
        if not request.user.id == recipe_user_id:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "You are not authorized to update this recipe"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, status=status.HTTP_200_OK, message="Recipe Updated Sussfully")


    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Delete Recipe",
        # request_body=UpdateRecipeSerializer,
        # responses={201: UpdateRecipeSerializer}
    )
    def delete(self, request, *args, **kwargs):
        recipe_user_id = Recipe.objects.get(id=kwargs['pk']).user_id
        if not request.user.id == recipe_user_id:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "You are not authorized to delete this recipe"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        response = super().delete(request, *args, **kwargs)
        return success_response(data=response.data, status=status.HTTP_204_NO_CONTENT, message="Recipe Deleted Sussfully")

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Retrieve Recipe",
        responses={200: UpdateRecipeSerializer}
    )
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    tr.*,
                    tu.first_name, tu.last_name
                FROM
                    tabReview AS tr
                LEFT JOIN tabUser AS tu
            """)
            rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        reviews = [dict(zip(columns, row)) for row in rows]
        recipe = super().get(request, *args, **kwargs)

        if recipe:
            response = copy.deepcopy(RESPONSE_SUCSSS)
            response['data']['recipe'] = recipe.data
            response['data']['reviews'] = reviews
            response['message'] = "Recipe Retrieved Sussfully"
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = copy.deepcopy(RESPONSE_FAILED)
            response['message'] = "Recipe Not Found"
            return Response(response, status=status.HTTP_404_NOT_FOUND)

class ReviewRecipeAPI(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Reviews'],
        operation_description="Create a new review",
        request_body=ReviewSerializer,
        responses={201: ReviewSerializer},
        security=[{'Bearer': []}]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success_response(serializer.data, status=status.HTTP_201_CREATED,message="Review Created Sussfully")

# Retrieve and Update API
class ReviewDetailAPI(RetrieveUpdateDestroyAPIView):
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
        return success_response(data=response.data, status=status.HTTP_200_OK, message='Review Retrieved Sussfully')

    @swagger_auto_schema(
        tags=['Reviews'],
        operation_description="Update a review",
        request_body=ReviewSerializer,
        responses={200: ReviewSerializer}
    )
    def put(self, request, *args, **kwargs):
        review_user_id = Review.objects.get(id=kwargs['pk']).user_id
        if not request.user.id == review_user_id:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "You are not authorized to update this review"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        response = super().update(request, *args, **kwargs)
        return success_response(data=response.data, status=status.HTTP_200_OK, message="Review Updated Sussfully")
    
    
    @swagger_auto_schema(
        tags=['Reviews'],
        operation_description="delete a review",
        # request_body=ReviewSerializer,
        # responses={200: ReviewSerializer}
    )
    def delete(self, request, *args, **kwargs):
        review_user_id = Review.objects.get(id=kwargs['pk']).user_id
        if not request.user.id == review_user_id:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "You are not authorized to delete this review"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        response = super().delete(request, *args, **kwargs)
        return success_response(data=response.data, status=status.HTTP_200_OK, message="Review Deleted Sussfully")