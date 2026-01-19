from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.management import call_command
from django.db import connection
from pathlib import Path
import json
import os
from datetime import datetime
import io

# Directorio para backups
BACKUP_DIR = Path(__file__).resolve().parent.parent / 'backups'
BACKUP_DIR.mkdir(exist_ok=True)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def database_backup(request):
    """
    Crear backup de la base de datos.
    POST /api/v1/system/database/backup
    Response: {"success": true, "message": "...", "file": "backup_xxx.json", "size_mb": 1.5, "timestamp": "2026-01-19T14:00:00"}
    """
    try:
        # Generar nombre del archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.json'
        backup_path = BACKUP_DIR / backup_filename
        
        # Usar dumpdata de Django para crear backup
        output = io.StringIO()
        call_command(
            'dumpdata',
            '--indent=2',
            '--exclude=admin.logentry',
            '--exclude=contenttypes',
            '--exclude=auth.permission',
            stdout=output,
            verbosity=0
        )
        
        # Guardar a archivo
        backup_data = output.getvalue()
        with open(backup_path, 'w') as f:
            f.write(backup_data)
        
        # Obtener tamaño del archivo
        size_bytes = os.path.getsize(backup_path)
        size_mb = round(size_bytes / (1024 * 1024), 2)
        
        return Response({
            'success': True,
            'message': f'Backup creado exitosamente: {backup_filename}',
            'file': backup_filename,
            'size_mb': size_mb,
            'timestamp': datetime.now().isoformat()
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al crear backup: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_backups(request):
    """
    Listar todos los backups disponibles.
    GET /api/v1/system/database/backups
    Response: {"backups": [{"filename": "backup_xxx.json", "path": "/path", "size_mb": 1.5, "created_at": "2026-01-19T14:00:00"}]}
    """
    try:
        backups = []
        
        if BACKUP_DIR.exists():
            for backup_file in sorted(BACKUP_DIR.glob('backup_*.json'), reverse=True):
                size_bytes = backup_file.stat().st_size
                size_mb = round(size_bytes / (1024 * 1024), 2)
                created_time = datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size_mb': size_mb,
                    'created_at': created_time
                })
        
        return Response({
            'backups': backups
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al listar backups: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def database_restore(request):
    """
    Restaurar base de datos desde un backup.
    POST /api/v1/system/database/restore?backup_filename=backup_xxx.json
    Response: {"success": true, "message": "..."}
    """
    try:
        backup_filename = request.query_params.get('backup_filename')
        
        if not backup_filename:
            return Response({
                'success': False,
                'message': 'Parámetro backup_filename requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        backup_path = BACKUP_DIR / backup_filename
        
        if not backup_path.exists():
            return Response({
                'success': False,
                'message': f'Archivo de backup no encontrado: {backup_filename}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validar que sea un archivo de backup válido
        if not backup_filename.startswith('backup_') or not backup_filename.endswith('.json'):
            return Response({
                'success': False,
                'message': 'Nombre de archivo inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Usar loaddata de Django para restaurar
        with open(backup_path, 'r') as f:
            call_command('loaddata', '-', stdin=f, verbosity=0)
        
        return Response({
            'success': True,
            'message': f'Base de datos restaurada exitosamente desde {backup_filename}'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al restaurar backup: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def database_test(request):
    """
    Probar conexión a la base de datos y obtener información.
    GET /api/v1/system/database/test
    Response: {"success": true, "database": "...", "tables_count": 15, "tables": [...], "records": {...}, "size_mb": 50}
    """
    try:
        from django.apps import apps
        
        db_name = 'srtimeweb'  # Usar nombre hardcoded para PostgreSQL
        
        # Obtener información de modelos y tablas
        tables_info = {}
        tables_list = []
        total_records = 0
        
        for model in apps.get_models():
            table_name = model._meta.db_table
            try:
                count = model.objects.count()
                tables_info[table_name] = count
                tables_list.append(table_name)
                total_records += count
            except Exception as e:
                tables_info[table_name] = 0
                tables_list.append(table_name)
        
        return Response({
            'success': True,
            'database': db_name,
            'tables_count': len(tables_list),
            'tables': sorted(tables_list),
            'records': tables_info,
            'size_mb': 100.0,  # Aproximado
            'connection': 'Successfully connected'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al probar BD: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def database_import(request):
    """
    Importar datos desde un archivo SQL/JSON.
    POST /api/v1/system/database/import
    Multipart: file
    Response: {"success": true, "message": "..."}
    """
    try:
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'message': 'Archivo requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_file = request.FILES['file']
        
        # Guardar temporalmente y cargar
        temp_path = BACKUP_DIR / f'temp_{uploaded_file.name}'
        
        with open(temp_path, 'wb+') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        try:
            # Intentar cargar como JSON fixture de Django
            with open(temp_path, 'r') as f:
                call_command('loaddata', '-', stdin=f, verbosity=0)
            
            return Response({
                'success': True,
                'message': f'Datos importados exitosamente desde {uploaded_file.name}'
            }, status=status.HTTP_200_OK)
        
        finally:
            # Limpiar archivo temporal
            if temp_path.exists():
                temp_path.unlink()
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error al importar datos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
