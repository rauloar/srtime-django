from django.db import migrations, models
import django.db.models.deletion


def backfill_employee_fk(apps, schema_editor):
    AttendanceLog = apps.get_model('core', 'AttendanceLog')
    Employee = apps.get_model('core', 'Employee')

    employee_map = {
        row['user_id']: row['id']
        for row in Employee.objects.exclude(user_id__isnull=True).exclude(user_id='').values('id', 'user_id')
    }

    to_update = []
    queryset = AttendanceLog.objects.filter(employee__isnull=True).exclude(user_id__isnull=True).exclude(user_id='')

    for log in queryset.iterator(chunk_size=2000):
        employee_id = employee_map.get(log.user_id)
        if employee_id:
            log.employee_id = employee_id
            to_update.append(log)

        if len(to_update) >= 2000:
            AttendanceLog.objects.bulk_update(to_update, ['employee'])
            to_update = []

    if to_update:
        AttendanceLog.objects.bulk_update(to_update, ['employee'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_remove_shadowcalculation_att_shadow__employe_69f4d5_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendancelog',
            name='employee',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='logs',
                to='core.employee',
            ),
        ),
        migrations.RunPython(backfill_employee_fk, noop_reverse),
    ]
