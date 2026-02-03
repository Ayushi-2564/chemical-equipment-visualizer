from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.http import FileResponse
from .models import Dataset, Equipment
from .serializers import (
    DatasetSerializer, DatasetListSerializer, 
    EquipmentSerializer, RegisterSerializer, UserSerializer
)
from .utils import process_csv_file, generate_pdf_report
import pandas as pd
import os


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login user and return token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })
    return Response(
        {'error': 'Invalid credentials'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Logout user by deleting token"""
    request.user.auth_token.delete()
    return Response({'message': 'Successfully logged out'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    """Upload and process CSV file"""
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    csv_file = request.FILES['file']
    
    # Validate file extension
    if not csv_file.name.endswith('.csv'):
        return Response(
            {'error': 'File must be a CSV'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Process CSV file
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        if not all(col in df.columns for col in required_columns):
            return Response(
                {'error': f'CSV must contain columns: {", ".join(required_columns)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate statistics
        stats = {
            'total_count': len(df),
            'avg_flowrate': float(df['Flowrate'].mean()),
            'avg_pressure': float(df['Pressure'].mean()),
            'avg_temperature': float(df['Temperature'].mean()),
            'type_distribution': df['Type'].value_counts().to_dict()
        }
        
        # Create Dataset
        dataset = Dataset.objects.create(
            user=request.user,
            filename=csv_file.name,
            total_count=stats['total_count'],
            avg_flowrate=stats['avg_flowrate'],
            avg_pressure=stats['avg_pressure'],
            avg_temperature=stats['avg_temperature']
        )
        dataset.set_type_distribution(stats['type_distribution'])
        dataset.save()
        
        # Create Equipment records
        equipment_list = []
        for _, row in df.iterrows():
            equipment = Equipment(
                dataset=dataset,
                equipment_name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=float(row['Flowrate']),
                pressure=float(row['Pressure']),
                temperature=float(row['Temperature'])
            )
            equipment_list.append(equipment)
        
        Equipment.objects.bulk_create(equipment_list)
        
        # Keep only last 5 datasets per user
        user_datasets = Dataset.objects.filter(user=request.user)
        if user_datasets.count() > 5:
            datasets_to_delete = user_datasets[5:]
            for ds in datasets_to_delete:
                ds.delete()
        
        # Return dataset with equipment data
        serializer = DatasetSerializer(dataset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error processing CSV: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_list(request):
    """Get list of user's datasets (last 5)"""
    datasets = Dataset.objects.filter(user=request.user)[:5]
    serializer = DatasetListSerializer(datasets, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dataset_detail(request, pk):
    """Get detailed dataset with equipment data"""
    try:
        dataset = Dataset.objects.get(pk=pk, user=request.user)
        serializer = DatasetSerializer(dataset)
        return Response(serializer.data)
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def dataset_delete(request, pk):
    """Delete a dataset"""
    try:
        dataset = Dataset.objects.get(pk=pk, user=request.user)
        dataset.delete()
        return Response({'message': 'Dataset deleted successfully'})
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_report(request, pk):
    """Generate PDF report for a dataset"""
    try:
        dataset = Dataset.objects.get(pk=pk, user=request.user)
        
        # Generate PDF
        pdf_path = generate_pdf_report(dataset)
        
        # Return PDF file
        return FileResponse(
            open(pdf_path, 'rb'), 
            as_attachment=True, 
            filename=f'report_{dataset.filename}.pdf'
        )
        
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Error generating report: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current user info"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)