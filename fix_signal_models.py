#!/usr/bin/env python
"""
Fix signal models by adding auto_now_add to created_at fields
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

from django.db import migrations, models

def fix_signal_models():
    """Create migration to fix signal model created_at fields"""
    
    migration_content = '''
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('signals', '0001_initial'),  # Adjust this to your latest migration
    ]

    operations = [
        migrations.AlterField(
            model_name='tradingsignal',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='spottradingsignal',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='marketregime',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='signalperformance',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='signalalert',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='spotportfolio',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
'''
    
    # Write migration file
    migration_file = 'apps/signals/migrations/0002_fix_created_at_fields.py'
    
    try:
        with open(migration_file, 'w') as f:
            f.write(migration_content)
        print(f"✅ Migration file created: {migration_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating migration file: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Creating migration to fix signal model created_at fields...")
    success = fix_signal_models()
    
    if success:
        print("\n📋 Next steps:")
        print("1. Run: python manage.py makemigrations signals")
        print("2. Run: python manage.py migrate")
        print("3. Test signal generation again")
    else:
        print("\n❌ Failed to create migration file")




















