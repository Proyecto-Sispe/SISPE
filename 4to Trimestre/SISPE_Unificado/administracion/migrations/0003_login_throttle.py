from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("administracion", "0002_factura_impuesto_factura_metodo_pago_factura_propina_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoginThrottle",
            fields=[
                ("key", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("attempts", models.PositiveSmallIntegerField(default=0)),
                ("window_started", models.DateTimeField()),
                ("blocked_until", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "sispe_login_throttle",
            },
        ),
        migrations.AddIndex(
            model_name="loginthrottle",
            index=models.Index(fields=["window_started"], name="login_window_idx"),
        ),
    ]
