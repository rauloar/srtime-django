"""
Script para cargar datos mock de zk_prod en Django desde SQL exportado

Uso:
    python load_zk_prod.py

Carga automaticamente desde: ../migration_data/zk_prod_*.sql
"""
import sys
import os
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SRTimeWeb.settings')
django.setup()

from django.db import connection
from pathlib import Path


def load_zk_prod_data():
    """Carga datos desde SQL exportado de MariaDB a PostgreSQL + Django"""
    
    print("\n" + "="*70)
    print("  📦 Cargar datos mock zk_prod → Django PostgreSQL")
    print("="*70 + "\n")

    # Rutas de archivos
    base_dir = Path(__file__).resolve().parent.parent
    schema_file = base_dir / 'migration_data' / 'zk_prod_schema.sql'
    data_file = base_dir / 'migration_data' / 'zk_prod_data.sql'

    # Validar existencia
    print("[1/4] 📋 Validando archivos SQL...")
    if not schema_file.exists():
        print(f"  ✗ Schema no encontrado: {schema_file}")
        return False
    if not data_file.exists():
        print(f"  ✗ Data no encontrado: {data_file}")
        return False
    print("  ✓ Archivos encontrados")

    # Verificar conexión
    print("\n[2/4] 🔌 Verificando conexión PostgreSQL...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            row = cursor.fetchone()
            pg_version = str(row[0]) if row and row[0] is not None else "unknown"
            print(f"  ✓ Conectado: {pg_version[:50]}...")
    except Exception as e:
        print(f"  ✗ Error de conexión: {e}")
        return False

    # Cargar Schema
    print("\n[3/4] 📋 Cargando esquema...")
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        with connection.cursor() as cursor:
            # Ejecutar el SQL (PostgreSQL puede tener pequeñas diferencias)
            # Simplificar: ejecutar statement por statement
            statements = schema_sql.split(';')
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--') and not stmt.startswith('/*'):
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        # Algunos errores de compatibilidad MySQL→PG son esperados
                        if 'already exists' not in str(e) and 'does not exist' not in str(e):
                            print(f"    ⚠ {str(e)[:60]}")
        
        connection.commit()
        print("  ✓ Esquema cargado (o ya existe)")
    except Exception as e:
        print(f"  ✗ Error cargando esquema: {e}")
        connection.rollback()
        return False

    # Cargar Datos
    print("\n[4/4] 📦 Cargando datos...")
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data_sql = f.read()
        
        with connection.cursor() as cursor:
            statements = data_sql.split(';')
            inserted = 0
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--') and not stmt.startswith('/*'):
                    try:
                        cursor.execute(stmt)
                        if cursor.rowcount > 0:
                            inserted += cursor.rowcount
                    except Exception as e:
                        # Algunos inserts duplicados pueden fallar
                        if 'duplicate' not in str(e).lower():
                            print(f"    ⚠ {str(e)[:60]}")
        
        connection.commit()
        print(f"  ✓ Datos cargados (~{inserted} registros)")
    except Exception as e:
        print(f"  ✗ Error cargando datos: {e}")
        connection.rollback()
        return False

    # Verificación
    print("\n" + "="*70)
    print("  📊 Verificación de datos cargados:")
    print("="*70)
    
    try:
        from core.models import (
            Company, Employee, Department, Device, AttendanceLog
        )
        
        counts = {
            'Companies': Company.objects.count(),
            'Employees': Employee.objects.count(),
            'Departments': Department.objects.count(),
            'Devices': Device.objects.count(),
            'Attendance Logs': AttendanceLog.objects.count(),
        }
        
        for model_name, count in counts.items():
            status = '✓' if count > 0 else '✗'
            print(f"  {status} {model_name}: {count}")
        
        print("\n" + "="*70)
        print("  ✅ Carga completada exitosamente!")
        print("="*70)
        print("\n📝 Próximos pasos:")
        print("  1. Iniciar Django: python manage.py runserver 9000")
        print("  2. Ver datos: http://localhost:9000/api/v1/")
        print("  3. Admin: http://localhost:9000/admin/\n")
        
        return True
        
    except Exception as e:
        print(f"  ⚠ Error verificando datos: {e}")
        return False


if __name__ == "__main__":
    try:
        success = load_zk_prod_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
