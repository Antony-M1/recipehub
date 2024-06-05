import copy
from django.shortcuts import render
from django.http import HttpResponse
from django.db.utils import IntegrityError
from django.db import connection
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView, 
    GenericAPIView
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authentication import authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserSerializer, UserLoginSerializer, CreateRecipeSerializer, 
    ListRequestRecipeSerializer, RecipeSerializer, UpdateRecipeSerializer,
    ReviewSerializer, UpdateReviewSerializer
)
from .models import Recipe, Review, User
from .utils import success_response
from .constant import RESPONSE_SUCCESS, RESPONSE_FAILED, CustomPagination

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
            if User.objects.filter(email=request.data.get("email")).exists():
                response = copy.deepcopy(RESPONSE_FAILED)
                response["message"] = "User already exists"
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(phone_number=request.data.get("phone_number")).exists():
                response = copy.deepcopy(RESPONSE_FAILED)
                response["message"] = "Phone number already used"
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            response = copy.deepcopy(RESPONSE_SUCCESS)
            response["message"] = "User Created Successfully"
            response["data"] = serializer.data
            return Response(response, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as ex:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["data"] = request.data
            response["message"] = str(ex)
            return Response({"error": str(ex), "request_data": request.data}, status=status.HTTP_400_BAD_REQUEST)

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

        user = authenticate(request, username=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            response = copy.deepcopy(RESPONSE_SUCCESS)
            response["message"] = "Login Successfully"
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

class ListCreateRecipeAPI(CreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Create Recipe",
        request_body=CreateRecipeSerializer,
        responses={201: CreateRecipeSerializer}
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data, status=status.HTTP_201_CREATED, message="Recipe Created Successfully")

class ListGetRecipeAPI(GenericAPIView):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'avg_rating', 'title', 'description', 'ingredients', 
        'preparation_steps', 'cooking_time', 'serving_size',
        'category_id'
    ]

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="List Recipes",
        request_body=ListRequestRecipeSerializer,
        responses={200: RecipeSerializer(many=True)}
    )
    def post(self, request):
        filters = request.data.get('filters', [])
        query = """
            SELECT trc.*, AVG(tr.rating) AS avg_rating
            FROM tabRecipe AS trc
            LEFT JOIN tabReview AS tr ON trc.id = tr.recipe_id
        """
        where_conditions = []
        having_conditions = []

        for f in filters:
            field = f.get('field')
            operator = f.get('operator')
            value = f.get('value')
            if field and operator and value:
                value = f"'{value}'" if isinstance(value, str) else value
                if field == 'avg_rating':
                    having_conditions.append(f"{field} {operator} {value}")
                else:
                    where_conditions.append(f"{field} {operator} {value}")

        if where_conditions or having_conditions:
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            query += " GROUP BY trc.id"
            if having_conditions:
                query += " HAVING " + " AND ".join(having_conditions)
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            recipes_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(recipes_data, request)

        if page is not None:
            serializer = RecipeSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = RecipeSerializer(recipes_data, many=True)
        return success_response(serializer.data, status=status.HTTP_200_OK, message='Recipes details')

class ListUpdateDeleteRecipeAPI(RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = UpdateRecipeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Update Recipe",
        request_body=UpdateRecipeSerializer,
        responses={200: UpdateRecipeSerializer}
    )
    def put(self, request, *args, **kwargs):
        recipe_user_id = Recipe.objects.get(id=kwargs['pk']).user_id
        if request.user.id != recipe_user_id:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "You are not authorized to update this recipe"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Delete Recipe"
    )
    def delete(self, request, *args, **kwargs):
        recipe_user_id = Recipe.objects.get(id=kwargs['pk']).user_id
        if request.user.id != recipe_user_id:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "You are not authorized to delete this recipe"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Recipe'],
        operation_description="Retrieve Recipe",
        responses={200: UpdateRecipeSerializer}
    )
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                tr.*,
                tu.first_name, 
                tu.last_name
                FROM
                tabReview AS tr
                LEFT JOIN
                tabUser AS tu ON tr.user_id = tu.id          
                LEFT JOIN
                tabRecipe AS rc ON tr.recipe_id = rc.id
                WHERE 
                tr.recipe_id = {kwargs['pk']};  
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            reviews = [dict(zip(columns, row)) for row in rows]
        recipe = super().get(request, *args, **kwargs)

        if recipe:
            response = copy.deepcopy(RESPONSE_SUCCESS)
            response['data']['recipe'] = recipe.data
            response['data']['reviews'] = reviews
            response['message'] = "Recipe Retrieved Successfully"
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = copy.deepcopy(RESPONSE_FAILED)
            response['message'] = "Recipe Not Found"
            return Response(response, status=status.HTTP_404_NOT_FOUND)

class ReviewRecipeAPI(CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Review'],
        operation_description="Create Review",
        request_body=ReviewSerializer,
        responses={201: ReviewSerializer}
    )
    def post(self, request):
        if Review.objects.filter(user_id=request.user.id, recipe_id=request.data.get('recipe_id')).exists():
            response = copy.deepcopy(RESPONSE_FAILED)
            response['message'] = "You have already reviewed this recipe"
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data, status=status.HTTP_201_CREATED, message="Review Created Successfully")

class ListUpdateDeleteReviewAPI(RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = UpdateReviewSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Review'],
        operation_description="Update Review",
        request_body=UpdateReviewSerializer,
        responses={200: UpdateReviewSerializer}
    )
    def put(self, request, *args, **kwargs):
        review_user_id = Review.objects.get(id=kwargs['pk']).user_id
        if request.user.id != review_user_id:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "You are not authorized to update this review"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Review'],
        operation_description="Delete Review"
    )
    def delete(self, request, *args, **kwargs):
        review_user_id = Review.objects.get(id=kwargs['pk']).user_id
        if request.user.id != review_user_id:
            response = copy.deepcopy(RESPONSE_FAILED)
            response["message"] = "You are not authorized to delete this review"
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=['Review'],
        operation_description="Retrieve Review",
        responses={200: UpdateReviewSerializer}
    )
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT
                tr.*,
                tu.first_name, 
                tu.last_name
                FROM
                tabReview AS tr
                LEFT JOIN
                tabUser AS tu ON tr.user_id = tu.id          
                LEFT JOIN
                tabRecipe AS rc ON tr.recipe_id = rc.id
                WHERE 
                tr.recipe_id = {kwargs['pk']};  
            """)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            reviews = [dict(zip(columns, row)) for row in rows]
        review = super().get(request, *args, **kwargs)

        if review:
            response = copy.deepcopy(RESPONSE_SUCCESS)
            response['data']['review'] = review.data
            response['data']['reviews'] = reviews
            response['message'] = "Review Retrieved Successfully"
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = copy.deepcopy(RESPONSE_FAILED)
            response['message'] = "Review Not Found"
            return Response(response, status=status.HTTP_404_NOT_FOUND)
