from datetime import datetime, time

from django.db import migrations, models


def _parse_time_value(value, field_name, timetable_id):
    if value is None:
        return None

    if isinstance(value, time):
        return value.replace(second=0, microsecond=0)

    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                parsed = datetime.strptime(value, fmt).time()
                return parsed.replace(second=0, microsecond=0)
            except ValueError:
                continue

    raise ValueError(
        f"Invalid {field_name} for Timetable {timetable_id}: {value!r}. Expected HH:MM."
    )


def normalize_timetable_times(apps, schema_editor):
    Timetable = apps.get_model("core", "Timetable")

    for tt in Timetable.objects.all().iterator():
        on_duty = _parse_time_value(tt.on_duty_time, "on_duty_time", tt.id)
        off_duty = _parse_time_value(tt.off_duty_time, "off_duty_time", tt.id)

        if on_duty is None or off_duty is None:
            raise ValueError(
                f"Timetable {tt.id} missing on/off duty times (on={on_duty}, off={off_duty})."
            )

        tt.on_duty_time = on_duty.strftime("%H:%M:%S")
        tt.off_duty_time = off_duty.strftime("%H:%M:%S")

        update_fields = ["on_duty_time", "off_duty_time"]
        for field_name in [
            "check_in_start",
            "check_in_end",
            "check_out_start",
            "check_out_end",
        ]:
            value = _parse_time_value(getattr(tt, field_name), field_name, tt.id)
            setattr(tt, field_name, value.strftime("%H:%M:%S") if value else None)
            update_fields.append(field_name)

        tt.save(update_fields=update_fields)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0104_add_overtime_threshold_to_timetable"),
    ]

    operations = [
        migrations.RunPython(normalize_timetable_times, noop),
        migrations.AlterField(
            model_name="timetable",
            name="on_duty_time",
            field=models.TimeField(verbose_name="Hora Entrada"),
        ),
        migrations.AlterField(
            model_name="timetable",
            name="off_duty_time",
            field=models.TimeField(verbose_name="Hora Salida"),
        ),
        migrations.AlterField(
            model_name="timetable",
            name="check_in_start",
            field=models.TimeField(null=True, blank=True, verbose_name="Inicio Ventana Entrada"),
        ),
        migrations.AlterField(
            model_name="timetable",
            name="check_in_end",
            field=models.TimeField(null=True, blank=True, verbose_name="Fin Ventana Entrada"),
        ),
        migrations.AlterField(
            model_name="timetable",
            name="check_out_start",
            field=models.TimeField(null=True, blank=True, verbose_name="Inicio Ventana Salida"),
        ),
        migrations.AlterField(
            model_name="timetable",
            name="check_out_end",
            field=models.TimeField(null=True, blank=True, verbose_name="Fin Ventana Salida"),
        ),
    ]
