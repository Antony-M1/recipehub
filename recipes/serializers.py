# myapp/serializers.py
from rest_framework import serializers
from recipes.models import User, Category, Recipe, Review
from django.db import models
from .validators import validate_rating, validate_field_and_value

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    phone_number = serializers.CharField(max_length=15)
    
    class Meta:
        model = User
        fields = ('password', 'email', "first_name", "last_name", "phone_number")

    def create(self, validated_data):
        
        user = User.objects.create_user(
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data['phone_number']
        )
        
            
        return user

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('email', 'password')

class RecipeSerializer(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField()
    ingredients = serializers.CharField()
    preparation_steps = serializers.CharField()
    cooking_time = serializers.IntegerField()
    serving_size = serializers.IntegerField()
    category_id = serializers.CharField()
    
    class Meta:
        model = Recipe
        fields = ('id', 'category_id', 'avg_rating', 'user', 'title', 'description', 'ingredients', 'preparation_steps', 'cooking_time', 'serving_size')


class CreateRecipeSerializer(serializers.ModelSerializer):
    # user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField()
    ingredients = serializers.CharField()
    preparation_steps = serializers.CharField()
    cooking_time = serializers.IntegerField()
    serving_size = serializers.IntegerField()
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')
    
    class Meta:
        model = Recipe
        fields = ('id', 'category_id', 'avg_rating', 'user', 'title', 'description', 'ingredients', 'preparation_steps', 'cooking_time', 'serving_size')


class FilterValueField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, list):
            return data
        try:
            return int(data)
        except ValueError:
            try:
                return float(data)
            except ValueError:
                return data

class FilterSerializer(serializers.Serializer):
    field = serializers.CharField(max_length=100,  required=True)
    operator = serializers.CharField(max_length=10,  required=True)
    value = FilterValueField(required=True)
        
    def validate(self, data):
        field = data.get('field')
        value = data.get('value')
        operator = data.get('operator')
        validate_field_and_value(field, operator, value)
        return data

class ListRequestRecipeSerializer(serializers.Serializer):
    filters = FilterSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = '__all__'



class UpdateRecipeSerializer(serializers.ModelSerializer):
    user_id = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField(required=False)
    ingredients = serializers.CharField(required=False)
    preparation_steps = serializers.CharField(required=False)
    cooking_time = serializers.IntegerField(required=False)
    serving_size = serializers.IntegerField(required=False)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'user_id', 'title', 'description', 'ingredients', 'preparation_steps', 'cooking_time', 'serving_size', 'category_id')

class CreateRecipeSerializer2(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'
        read_only_fields = ['user_id', 'created_at', 'updated_at']
        
        
class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    id = serializers.IntegerField(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    rating = serializers.IntegerField(validators=[validate_rating])
    comment = serializers.CharField()

    class Meta:
        model = Review
        fields = ('id', 'user', 'recipe', 'rating', 'comment')

class UpdateReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all(), required=False)
    rating = serializers.IntegerField(required=False, validators=[validate_rating])
    comment = serializers.CharField(required=False)

    class Meta:
        model = Review
        fields = ('user', 'recipe', 'rating', 'comment')
        read_only_fields = ('user',)
        

class DeleteReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())


class AllReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        


class SearchSerializer(serializers.Serializer):
    
    search = serializers.CharField()
    class Meta:
        fields = '__all__'