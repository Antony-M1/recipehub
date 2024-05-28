# myapp/serializers.py
from rest_framework import serializers
from recipes.models import User

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
    
