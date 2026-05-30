from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_product_colors_product_sizes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='image',
            field=models.URLField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.URLField(max_length=1000),
        ),
    ]
