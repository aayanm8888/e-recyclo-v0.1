import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erecyclo.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Get all tables in database
    cursor.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    all_tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found {len(all_tables)} tables: {all_tables}\n")
    
    # Drop ALL tables (nuclear option)
    for table in all_tables:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
            print(f"✓ Dropped {table}")
        except Exception as e:
            print(f"✗ {table}: {e}")
    
    print("\n✓ Database cleared!")

print("Now run: python manage.py migrate")