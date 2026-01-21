# Comando Django para poblar la BD con datos de prueba
# Crea topics y posts de ejemplo para desarrollo y testing
# Ejecutar: docker compose exec backend uv run manage.py seed_data

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.topics.models import Topic
from apps.posts.models import Post


class Command(BaseCommand):
    help = "Poblar la base de datos con datos de prueba"

    def handle(self, *args, **kwargs):
        self.stdout.write("Creando topics de prueba...")

        topics_data = [
            {"name": "artificial-intelligence", "is_active": True},
            {"name": "productivity", "is_active": True},
            {"name": "developer-tools", "is_active": True},
            {"name": "marketing", "is_active": False},
            {"name": "tech", "is_active": True},
        ]

        topics = []
        for data in topics_data:
            topic, created = Topic.objects.get_or_create(
                name=data["name"],
                defaults={"is_active": data["is_active"]}
            )
            topics.append(topic)
            status = "✓ Creado" if created else "○ Ya existe"
            self.stdout.write(f"  {status}: {topic.name}")

        self.stdout.write("\nCreando posts de prueba...")

        # Posts ficticios simulando productos de Product Hunt
        posts_data = [
            {
                "external_id": "ph_001",
                "topic": topics[0],
                "title": "AI Code Assistant",
                "tagline": "Your intelligent pair programmer powered by GPT-4",
                "content": "AI Code Assistant helps developers write better code faster. It understands context, suggests completions, and can even explain complex code snippets.",
                "author": "techfounder",
                "score": 1245,
                "votes_count": 1245,
                "comments_count": 89,
                "url": "https://producthunt.com/posts/ai-code-assistant",
                "website": "https://aicodeassistant.com",
                "created_at_source": timezone.now() - timedelta(days=5),
                "analyzed": True,
                "summary": "Asistente de código con IA para desarrolladores",
                "problem": "Los desarrolladores pierden tiempo escribiendo código repetitivo y buscando documentación",
                "mvp_idea": "Extension de IDE con sugerencias de código inteligentes basadas en contexto",
                "target_audience": "Desarrolladores de software, equipos de engineering",
                "potential_score": 8,
                "tags": "IA, código, desarrollo, productividad",
                "analyzed_at": timezone.now() - timedelta(days=4),
            },
            {
                "external_id": "ph_002",
                "topic": topics[1],
                "title": "FocusFlow",
                "tagline": "Pomodoro timer with AI-powered distraction blocking",
                "content": "FocusFlow combines the pomodoro technique with smart website blocking. It learns your habits and automatically blocks distracting sites during work sessions.",
                "author": "productivityguru",
                "score": 892,
                "votes_count": 892,
                "comments_count": 67,
                "url": "https://producthunt.com/posts/focusflow",
                "website": "https://focusflow.app",
                "created_at_source": timezone.now() - timedelta(days=3),
                "analyzed": True,
                "summary": "Timer pomodoro con bloqueo inteligente de distracciones",
                "problem": "Las distracciones digitales reducen la productividad durante el trabajo",
                "mvp_idea": "App de pomodoro que bloquea sitios automáticamente basándose en patrones de uso",
                "target_audience": "Trabajadores remotos, freelancers, estudiantes",
                "potential_score": 9,
                "tags": "productividad, focus, pomodoro, trabajo",
                "analyzed_at": timezone.now() - timedelta(days=2),
            },
            {
                "external_id": "ph_003",
                "topic": topics[2],
                "title": "APIDoc Generator",
                "tagline": "Auto-generate beautiful API documentation from your code",
                "content": "Stop writing documentation manually. APIDoc Generator analyzes your code and creates interactive API docs that stay up-to-date automatically.",
                "author": "devtoolmaker",
                "score": 756,
                "votes_count": 756,
                "comments_count": 45,
                "url": "https://producthunt.com/posts/apidoc-generator",
                "website": "https://apidocgen.io",
                "created_at_source": timezone.now() - timedelta(days=7),
                "analyzed": True,
                "summary": "Generador automático de documentación de APIs",
                "problem": "La documentación de APIs se desactualiza rápidamente y es tedioso mantenerla",
                "mvp_idea": "Herramienta CLI que genera docs interactivos desde anotaciones de código",
                "target_audience": "Desarrolladores backend, equipos de API",
                "potential_score": 7,
                "tags": "developer-tools, documentación, API, automatización",
                "analyzed_at": timezone.now() - timedelta(days=6),
            },
            {
                "external_id": "ph_004",
                "topic": topics[4],
                "title": "StartupMatch",
                "tagline": "Find your perfect co-founder based on skills and vision",
                "content": "StartupMatch uses AI to match entrepreneurs with complementary skills. Answer a few questions about your startup idea and find technical or business co-founders.",
                "author": "startupbuilder",
                "score": 623,
                "votes_count": 623,
                "comments_count": 112,
                "url": "https://producthunt.com/posts/startupmatch",
                "website": "https://startupmatch.co",
                "created_at_source": timezone.now() - timedelta(days=2),
                "analyzed": True,
                "summary": "Plataforma de matching para encontrar cofundadores",
                "problem": "Dificultad para encontrar cofundadores con habilidades complementarias",
                "mvp_idea": "Matching tipo Tinder para emprendedores basado en skills y visión",
                "target_audience": "Emprendedores buscando socios, founders solo",
                "potential_score": 6,
                "tags": "startups, cofundadores, networking, matching",
                "analyzed_at": timezone.now() - timedelta(days=1),
            },
            {
                "external_id": "ph_005",
                "topic": topics[0],
                "title": "VoiceNote AI",
                "tagline": "Turn voice memos into structured notes with AI",
                "content": "Record your thoughts and let AI organize them into bullet points, action items, and summaries. Perfect for meetings and brainstorming sessions.",
                "author": "aienthusiast",
                "score": 478,
                "votes_count": 478,
                "comments_count": 34,
                "url": "https://producthunt.com/posts/voicenote-ai",
                "website": "https://voicenote.ai",
                "created_at_source": timezone.now() - timedelta(days=1),
                "analyzed": False,
            },
            {
                "external_id": "ph_006",
                "topic": topics[1],
                "title": "HabitStack",
                "tagline": "Build habits by stacking them with existing routines",
                "content": "HabitStack helps you build new habits by linking them to things you already do. Uses the proven habit stacking technique with smart reminders.",
                "author": "habithacker",
                "score": 534,
                "votes_count": 534,
                "comments_count": 56,
                "url": "https://producthunt.com/posts/habitstack",
                "website": "https://habitstack.app",
                "created_at_source": timezone.now() - timedelta(hours=12),
                "analyzed": False,
            },
            {
                "external_id": "ph_007",
                "topic": topics[2],
                "title": "GitMetrics",
                "tagline": "Beautiful dashboards for your GitHub repositories",
                "content": "Track commits, PRs, and code reviews with GitMetrics. Perfect for team leads who want to understand their team's productivity patterns.",
                "author": "metricsmaster",
                "score": 891,
                "votes_count": 891,
                "comments_count": 78,
                "url": "https://producthunt.com/posts/gitmetrics",
                "website": "https://gitmetrics.dev",
                "created_at_source": timezone.now() - timedelta(hours=6),
                "analyzed": True,
                "summary": "Dashboards de métricas para repositorios GitHub",
                "problem": "Difícil visualizar la productividad y patrones del equipo de desarrollo",
                "mvp_idea": "Dashboard conectado a GitHub con métricas de commits, PRs y reviews",
                "target_audience": "Tech leads, engineering managers, equipos de desarrollo",
                "potential_score": 7,
                "tags": "GitHub, métricas, desarrollo, equipos",
                "analyzed_at": timezone.now() - timedelta(hours=5),
            },
            {
                "external_id": "ph_008",
                "topic": topics[4],
                "title": "LaunchPad Analytics",
                "tagline": "Track your Product Hunt launch in real-time",
                "content": "Monitor your Product Hunt launch with live analytics. See upvotes, comments, and traffic sources as they happen. Get alerts for important milestones.",
                "author": "launchexpert",
                "score": 356,
                "votes_count": 356,
                "comments_count": 23,
                "url": "https://producthunt.com/posts/launchpad-analytics",
                "website": "https://launchpad-analytics.com",
                "created_at_source": timezone.now() - timedelta(hours=18),
                "analyzed": False,
            },
        ]

        for data in posts_data:
            post, created = Post.objects.get_or_create(
                external_id=data["external_id"],
                defaults=data
            )
            status = "✓ Creado" if created else "○ Ya existe"
            analyzed_icon = "🤖" if post.analyzed else "⏳"
            self.stdout.write(f"  {status} {analyzed_icon}: {post.title[:60]}...")

        total_topics = Topic.objects.count()
        total_posts = Post.objects.count()
        analyzed_posts = Post.objects.filter(analyzed=True).count()

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ Datos de prueba creados exitosamente:\n"
                f"  - {total_topics} topics\n"
                f"  - {total_posts} posts ({analyzed_posts} analizados, {total_posts - analyzed_posts} sin analizar)"
            )
        )
