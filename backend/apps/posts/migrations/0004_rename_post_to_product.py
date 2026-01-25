# Generated manually for Post → Product refactor
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_change_target_audience_to_textfield'),
    ]

    operations = [
        # Renombrar modelo Post → Product
        migrations.RenameModel(
            old_name='Post',
            new_name='Product',
        ),
        # Renombrar campo post → product en Favorite (post_id → product_id)
        migrations.RenameField(
            model_name='favorite',
            old_name='post',
            new_name='product',
        ),
        # Actualizar related_name en Topic (posts → products)
        migrations.AlterField(
            model_name='product',
            name='topic',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to='topics.topic',
                help_text='Topic de origen',
            ),
        ),
        # Actualizar unique_together en Favorite
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together={('user', 'product')},
        ),
    ]
