# Migración para remover modelo Favorite de users

from django.db import migrations


class Migration(migrations.Migration):
    """
    Elimina el modelo Favorite de la app users.

    El modelo se movió a apps.posts para mantener posts autocontenido.
    Solo eliminamos del estado de Django, la tabla se mantiene.
    """

    dependencies = [
        ("users", "0001_initial"),
        ("posts", "0002_favorite"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name="Favorite",
                ),
            ],
            database_operations=[],
        ),
    ]
