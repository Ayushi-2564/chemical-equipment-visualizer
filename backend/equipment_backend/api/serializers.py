from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, Equipment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class EquipmentSerializer(serializers.ModelSerializer):
    """Serializer for Equipment model"""
    class Meta:
        model = Equipment
        fields = ['id', 'equipment_name', 'equipment_type', 'flowrate', 
                  'pressure', 'temperature']


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for Dataset model"""
    equipment = EquipmentSerializer(many=True, read_only=True)
    type_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'upload_date', 'total_count', 
                  'avg_flowrate', 'avg_pressure', 'avg_temperature',
                  'type_distribution', 'equipment']
    
    def get_type_distribution(self, obj):
        """Return type distribution as dict"""
        return obj.get_type_distribution()


class DatasetListSerializer(serializers.ModelSerializer):
    """Simplified serializer for dataset list (without equipment details)"""
    type_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'upload_date', 'total_count', 
                  'avg_flowrate', 'avg_pressure', 'avg_temperature',
                  'type_distribution']
    
    def get_type_distribution(self, obj):
        return obj.get_type_distribution()