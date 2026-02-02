import os
import sys
from pathlib import Path
import django
from django.db import connection

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def fix_db():
    print("Checking for missing table 'forensic_integrity_hash'...")
    with connection.cursor() as cursor:
        # Check if table exists (PostgreSQL)
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'forensic_integrity_hash');")
        exists = cursor.fetchone()[0]
        
        if exists:
            print("Table 'forensic_integrity_hash' already exists.")
            return

        print("Creating table 'forensic_integrity_hash' manually...")
        # Schema based on models_forensic.py (Postgres Syntax)
        sql = """
        CREATE TABLE "forensic_integrity_hash" (
            "id" bigserial NOT NULL PRIMARY KEY,
            "entity_type" varchar(20) NOT NULL,
            "entity_id" bigint NOT NULL,
            "case_id" bigint NULL,
            "content_hash" varchar(64) NOT NULL,
            "previous_hash" varchar(64) NOT NULL,
            "chain_hash" varchar(64) NOT NULL UNIQUE,
            "canonical_json" text NOT NULL,
            "hash_algorithm" varchar(20) NOT NULL,
            "created_at" timestamp with time zone NOT NULL
        );
        """
        cursor.execute(sql)
        print("Table created successfully.")

        # Create indexes
        print("Creating indexes...")
        cursor.execute('CREATE INDEX "forensic_integrity_hash_entity_type_entity_id_idx" ON "forensic_integrity_hash" ("entity_type", "entity_id");')
        cursor.execute('CREATE INDEX "forensic_integrity_hash_case_id_created_at_idx" ON "forensic_integrity_hash" ("case_id", "created_at");')
        print("Indexes created.")

if __name__ == '__main__':
    fix_db()
