from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from core.models import AuthUser


class LoginSerializer(serializers.Serializer):
    """Serializer para login compatible con frontend React"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class LoginResponseSerializer(serializers.Serializer):
    """Respuesta de login compatible con frontend React"""
    access_token = serializers.CharField()
    token_type = serializers.CharField(default='bearer')
    username = serializers.CharField()
    role = serializers.CharField()


class AuthUserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios con contraseña"""
    password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'password', 'role', 'employee', 'active']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data['password_hash'] = make_password(password)
        return super().create(validated_data)


class AuthUserListSerializer(serializers.ModelSerializer):
    """Serializer para listar usuarios (sin password)"""
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'role', 'employee', 'employee_name', 'active', 'created_at']


class PasswordUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar contraseña"""
    password = serializers.CharField(write_only=True, required=True)


@api_view(['POST'])
@permission_classes([AllowAny])
def auth_login(request):
    """
    Endpoint de login compatible con frontend React.
    POST /api/v1/auth/login
    Body: {"username": "admin", "password": "admin123"}
    Response: {"access_token": "...", "token_type": "bearer", "username": "admin", "role": "admin"}
    """
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {'detail': 'Datos de acceso inválidos'},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    
    try:
        user = AuthUser.objects.get(username=username, active=True)
    except AuthUser.DoesNotExist:
        return Response(
            {'detail': 'Usuario o contraseña incorrectos'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Verificar contraseña
    if not check_password(password, user.password_hash):
        return Response(
            {'detail': 'Usuario o contraseña incorrectos'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Generar token JWT
    refresh = RefreshToken()
    refresh['user_id'] = user.id
    refresh['username'] = user.username
    refresh['role'] = user.role
    
    # Respuesta compatible con frontend
    response_data = {
        'access_token': str(refresh.access_token),
        'token_type': 'bearer',
        'username': user.username,
        'role': user.role,
    }
    
    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def auth_users_list(request):
    """
    Endpoint para listar y crear usuarios compatible con frontend React.
    GET /api/v1/auth/users - Listar usuarios
    POST /api/v1/auth/users - Crear usuario
    """
    if request.method == 'GET':
        users = AuthUser.objects.all().order_by('-created_at')
        serializer = AuthUserListSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = AuthUserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_serializer = AuthUserListSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def auth_user_delete(request, user_id):
    """
    Endpoint para eliminar usuario compatible con frontend React.
    DELETE /api/v1/auth/users/{id}
    """
    try:
        user = AuthUser.objects.get(id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except AuthUser.DoesNotExist:
        return Response(
            {'detail': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def auth_user_password_update(request, user_id):
    """
    Endpoint para actualizar contraseña compatible con frontend React.
    PUT /api/v1/auth/users/{id}/password
    Body: {"password": "nueva_contraseña"}
    """
    try:
        user = AuthUser.objects.get(id=user_id)
    except AuthUser.DoesNotExist:
        return Response(
            {'detail': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = PasswordUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    password = serializer.validated_data['password']
    user.password_hash = make_password(password)
    user.save()
    
    return Response({'detail': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)
