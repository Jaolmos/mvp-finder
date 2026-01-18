# Comando Django para poblar la BD con datos de prueba
# Crea subreddits y posts de ejemplo para desarrollo y testing
# Ejecutar: docker compose exec backend uv run manage.py seed_data

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.subreddits.models import Subreddit
from apps.posts.models import Post


class Command(BaseCommand):
    help = "Poblar la base de datos con datos de prueba"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creando subreddits de prueba...")

        subreddits_data = [
            {"name": "SomebodyMakeThis", "active": True},
            {"name": "AppIdeas", "active": True},
            {"name": "Lightbulb", "active": True},
            {"name": "indiehackers", "active": False},
            {"name": "Entrepreneur", "active": True},
        ]

        subreddits = []
        for data in subreddits_data:
            subreddit, created = Subreddit.objects.get_or_create(
                name=data["name"],
                defaults={"active": data["active"]}
            )
            subreddits.append(subreddit)
            status = "✓ Creado" if created else "○ Ya existe"
            self.stdout.write(f"  {status}: r/{subreddit.name}")

        self.stdout.write("\nCreando posts de prueba...")

        # Posts ficticios con títulos/contenido en inglés (simulando Reddit real)
        # y análisis en español (simulando output de Ollama)
        posts_data = [
            {
                "reddit_id": "abc123",
                "subreddit": subreddits[0],
                "title": "App to track shared expenses with roommates",
                "content": "I live with 3 roommates and it's a nightmare tracking who owes what. We need an app that automatically splits bills and tracks payments.",
                "author": "user_roommate",
                "score": 245,
                "url": "https://reddit.com/r/SomebodyMakeThis/comments/abc123",
                "created_at_reddit": timezone.now() - timedelta(days=5),
                "analyzed": True,
                "summary": "App para dividir gastos entre roommates",
                "problem": "Dificultad para llevar cuentas compartidas entre compañeros de piso",
                "mvp_idea": "Tracker de gastos con división automática y notificaciones de deudas",
                "target_audience": "Estudiantes, young professionals con roommates",
                "potential_score": 7,
                "tags": "finanzas, compartir, gastos, roommates",
                "analyzed_at": timezone.now() - timedelta(days=4),
            },
            {
                "reddit_id": "def456",
                "subreddit": subreddits[1],
                "title": "Tool to organize weekly meal planning",
                "content": "I waste so much time deciding what to cook. Need an app that suggests recipes based on what I have in the fridge.",
                "author": "cooking_enthusiast",
                "score": 189,
                "url": "https://reddit.com/r/AppIdeas/comments/def456",
                "created_at_reddit": timezone.now() - timedelta(days=3),
                "analyzed": True,
                "summary": "Planificador de comidas semanal inteligente",
                "problem": "Pérdida de tiempo decidiendo qué cocinar cada día",
                "mvp_idea": "App que sugiere recetas según ingredientes disponibles",
                "target_audience": "Personas ocupadas que cocinan en casa",
                "potential_score": 8,
                "tags": "comida, recetas, planificación, cocina",
                "analyzed_at": timezone.now() - timedelta(days=2),
            },
            {
                "reddit_id": "ghi789",
                "subreddit": subreddits[2],
                "title": "Browser extension to block distracting websites during work",
                "content": "I keep getting distracted by social media when working. Need something smarter than just blocking sites.",
                "author": "productivity_seeker",
                "score": 512,
                "url": "https://reddit.com/r/Lightbulb/comments/ghi789",
                "created_at_reddit": timezone.now() - timedelta(days=7),
                "analyzed": True,
                "summary": "Bloqueador inteligente de sitios distractores",
                "problem": "Distracciones constantes por redes sociales durante trabajo",
                "mvp_idea": "Extensión de navegador con bloqueo contextual y recordatorios",
                "target_audience": "Trabajadores remotos, estudiantes",
                "potential_score": 9,
                "tags": "productividad, focus, trabajo, extensión",
                "analyzed_at": timezone.now() - timedelta(days=6),
            },
            {
                "reddit_id": "jkl012",
                "subreddit": subreddits[4],
                "title": "Platform to find co-founders for startup ideas",
                "content": "I have a great idea but no technical co-founder. There should be a LinkedIn for finding startup partners.",
                "author": "solo_founder",
                "score": 423,
                "url": "https://reddit.com/r/Entrepreneur/comments/jkl012",
                "created_at_reddit": timezone.now() - timedelta(days=2),
                "analyzed": True,
                "summary": "Plataforma para encontrar cofundadores de startups",
                "problem": "Dificultad para encontrar socios técnicos o de negocio",
                "mvp_idea": "Red social estilo LinkedIn específica para matching de cofundadores",
                "target_audience": "Emprendedores buscando socios",
                "potential_score": 6,
                "tags": "startups, cofundador, networking, emprendimiento",
                "analyzed_at": timezone.now() - timedelta(days=1),
            },
            {
                "reddit_id": "mno345",
                "subreddit": subreddits[0],
                "title": "App to remind me to drink water throughout the day",
                "content": "I always forget to stay hydrated. Simple notifications would help.",
                "author": "health_conscious",
                "score": 78,
                "url": "https://reddit.com/r/SomebodyMakeThis/comments/mno345",
                "created_at_reddit": timezone.now() - timedelta(days=1),
                "analyzed": False,
            },
            {
                "reddit_id": "pqr678",
                "subreddit": subreddits[1],
                "title": "Flashcard app with spaced repetition for language learning",
                "content": "Existing apps are too complex. Need something dead simple for vocabulary.",
                "author": "language_learner",
                "score": 234,
                "url": "https://reddit.com/r/AppIdeas/comments/pqr678",
                "created_at_reddit": timezone.now() - timedelta(hours=12),
                "analyzed": False,
            },
            {
                "reddit_id": "stu901",
                "subreddit": subreddits[2],
                "title": "Smart alarm that wakes you at optimal sleep cycle",
                "content": "Waking up at the wrong time makes me groggy. Need an alarm that tracks sleep cycles.",
                "author": "sleep_optimizer",
                "score": 891,
                "url": "https://reddit.com/r/Lightbulb/comments/stu901",
                "created_at_reddit": timezone.now() - timedelta(hours=6),
                "analyzed": True,
                "summary": "Alarma inteligente que despierta en ciclo óptimo",
                "problem": "Despertar en momento incorrecto del ciclo de sueño causa fatiga",
                "mvp_idea": "App con tracking de sueño que ajusta alarma al ciclo óptimo",
                "target_audience": "Personas con problemas de sueño, madrugadores",
                "potential_score": 7,
                "tags": "sueño, alarma, salud, tracking",
                "analyzed_at": timezone.now() - timedelta(hours=5),
            },
            {
                "reddit_id": "vwx234",
                "subreddit": subreddits[4],
                "title": "Tool to validate startup ideas with real users",
                "content": "Before building, I want to test if people actually want this. Need a platform to get quick feedback.",
                "author": "lean_startup_fan",
                "score": 156,
                "url": "https://reddit.com/r/Entrepreneur/comments/vwx234",
                "created_at_reddit": timezone.now() - timedelta(hours=18),
                "analyzed": False,
            },
        ]

        for data in posts_data:
            post, created = Post.objects.get_or_create(
                reddit_id=data["reddit_id"],
                defaults=data
            )
            status = "✓ Creado" if created else "○ Ya existe"
            analyzed_icon = "🤖" if post.analyzed else "⏳"
            self.stdout.write(f"  {status} {analyzed_icon}: {post.title[:60]}...")

        total_subreddits = Subreddit.objects.count()
        total_posts = Post.objects.count()
        analyzed_posts = Post.objects.filter(analyzed=True).count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Datos de prueba creados exitosamente:\n"
                f"  - {total_subreddits} subreddits\n"
                f"  - {total_posts} posts ({analyzed_posts} analizados, {total_posts - analyzed_posts} sin analizar)"
            )
        )
