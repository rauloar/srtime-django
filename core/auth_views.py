from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
import time

# Tiempo de inicio del servidor (se establece al cargar el módulo)
SERVER_START_TIME = str(int(time.time()))


class LoginSerializer(serializers.Serializer):
    """Serializer para login compatible con frontend React"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)



# Serializer for login response
class LoginResponseSerializer(serializers.Serializer):
    """Respuesta de login compatible con frontend React"""
    access_token = serializers.CharField()
    token_type = serializers.CharField(default='bearer')
    username = serializers.CharField()
    role = serializers.CharField()

# Serializer for creating users
class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'is_active', 'is_staff', 'is_superuser', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

# Serializer for listing users
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_active', 'is_staff', 'is_superuser', 'email', 'first_name', 'last_name', 'date_joined']


class PasswordUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar contraseña"""
    password = serializers.CharField(write_only=True, required=True)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def auth_login(request):
    """
    Endpoint de login compatible con frontend React usando User estándar de Django.
    POST /api/v1/auth/login
    Body: {"username": "admin", "password": "admin123"}
    Response: {"access_token": "...", "token_type": "bearer", "username": "admin", "is_staff": true, ...}
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'detail': 'Datos de acceso inválidos'},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    assert serializer.is_valid()
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)
    if user is None or not user.is_active:
        return Response(
            {'detail': 'Usuario o contraseña incorrectos'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    # Generar token JWT
    refresh = RefreshToken.for_user(user)
    # Respuesta compatible con frontend
    # Determinar el rol para el frontend
    if user.is_superuser:
        role = 'admin'
    elif user.is_staff:
        role = 'staff'
    else:
        role = 'user'
    response_data = {
        'access_token': str(refresh.access_token),
        'token_type': 'bearer',
        'username': user.username,
        'role': role,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def server_info(request):
    """
    Endpoint para obtener información del servidor.
    GET /api/v1/auth/server-info
    Response: {"start_time": "1234567890", "version": "1.0.0"}
    """
    return Response({
        'start_time': SERVER_START_TIME,
        'version': '1.0.0',
        'framework': 'Django 6.0.1'
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def auth_users_list(request):
    """
    Endpoint para listar y crear usuarios usando el modelo estándar de Django.
    GET /api/v1/auth/users - Listar usuarios
    POST /api/v1/auth/users - Crear usuario
    """
    from django.contrib.auth.models import User
    if request.method == 'GET':
        users = User.objects.all().order_by('-date_joined')
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = UserListSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def auth_user_delete(request, user_id):
    """
    Endpoint para eliminar usuario usando el modelo estándar de Django.
    DELETE /api/v1/auth/users/{id}
    """
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def auth_user_password_update(request, user_id):
    """
    Endpoint para actualizar contraseña usando el modelo estándar de Django.
    PUT /api/v1/auth/users/{id}/password
    Body: {"password": "nueva_contraseña"}
    """
    from django.contrib.auth.models import User
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = PasswordUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    assert serializer.is_valid()
    password = serializer.validated_data['password']
    user.set_password(password)
    user.save()
    return Response({'detail': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)
