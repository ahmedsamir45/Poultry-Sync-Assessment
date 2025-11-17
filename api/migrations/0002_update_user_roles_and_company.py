# Generated manually to handle role changes and company requirement

from django.db import migrations, models
import django.db.models.deletion


def assign_default_company_to_users(apps, schema_editor):
    """Assign a default company to any users without one and update old role values"""
    CustomUser = apps.get_model('api', 'CustomUser')
    Company = apps.get_model('api', 'Company')
    
    # Get or create a default company
    default_company, _ = Company.objects.get_or_create(
        name='Default Company',
        defaults={'name': 'Default Company'}
    )
    
    # Assign default company to users without one
    CustomUser.objects.filter(company__isnull=True).update(company=default_company)
    
    # Update old role values to new ones
    # system_admin and company_admin -> admin
    CustomUser.objects.filter(role__in=['system_admin', 'company_admin']).update(role='admin')
    # operator and viewer remain the same


def reverse_assign_default_company(apps, schema_editor):
    """Reverse migration - set company to null (not really needed but good practice)"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        # Step 1: Update role choices first
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[('admin', 'Admin'), ('operator', 'Operator'), ('viewer', 'Viewer')],
                default='viewer',
                max_length=20
            ),
        ),
        # Step 2: Assign default company to users without one
        migrations.RunPython(assign_default_company_to_users, reverse_assign_default_company),
        # Step 3: Make company field non-nullable
        migrations.AlterField(
            model_name='customuser',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='api.company'
            ),
        ),
        # Step 4: Make created_at fields immutable
        migrations.AlterField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, editable=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, editable=False),
        ),
    ]

