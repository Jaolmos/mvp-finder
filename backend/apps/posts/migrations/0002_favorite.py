# Migración para mover modelo Favorite de users a posts

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Añade el modelo Favorite a la app posts.

    El modelo se mueve desde apps.users para mantener posts autocontenido.
    Usamos SeparateDatabaseAndState porque la tabla users_favorite ya existe.
    """

    dependencies = [
        ("posts", "0001_initial"),
        ("users", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name="Favorite",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "created_at",
                            models.DateTimeField(
                                auto_now_add=True,
                                help_text="Cuándo se marcó como favorito",
                            ),
                        ),
                        (
                            "post",
                            models.ForeignKey(
                                help_text="Post marcado como favorito",
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="favorited_by",
                                to="posts.post",
                            ),
                        ),
                        (
                            "user",
                            models.ForeignKey(
                                help_text="Usuario que marcó el favorito",
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="favorites",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "verbose_name": "Favorito",
                        "verbose_name_plural": "Favoritos",
                        "ordering": ["-created_at"],
                        "db_table": "users_favorite",
                        "unique_together": {("user", "post")},
                    },
                ),
            ],
            database_operations=[],
        ),
    ]
