from django.db import migrations, models
import django.db.models.deletion


def assert_no_orphans(apps, schema_editor):
    AttendanceLog = apps.get_model('core', 'AttendanceLog')

    orphan_qs = AttendanceLog.objects.filter(employee__isnull=True)
    orphan_count = orphan_qs.count()
    if orphan_count == 0:
        return

    sample = list(orphan_qs.values_list('id', 'user_id', 'timestamp')[:10])
    raise RuntimeError(
        f"Cannot enforce NOT NULL on attendance_logs.employee: {orphan_count} orphan logs found. "
        f"Sample (id, user_id, timestamp): {sample}"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_attendancelog_employee_fk'),
    ]

    operations = [
        migrations.RunPython(assert_no_orphans, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='attendancelog',
            name='employee',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='logs',
                to='core.employee',
            ),
        ),
    ]
