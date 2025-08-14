# Ohmi Audit Django Project — Architecture Overview

This document provides a high-level and code-level architecture analysis of the Ohmi Audit project, based on the current repository state.


## 1. Overview

- Framework: Django (with Django REST Framework for simple APIs).
- Apps:
  - ohmi_audit.main_app: Core domain (Audit, Auditor, Customer, AppUser, forms, views, tasks).
  - ohmi_audit.hr_management: Separate bounded context for HR features (currently a simple index view).
- Common utilities:
  - common: shared modules (serializers, decorators, middleware, common model data).
- Frontend: Django templates with a base layout and include fragments, static assets organized under static/ and static_files/.
- Internationalization (i18n): Enabled; languages configured (en, bg). URL i18n patterns used.
- Background processing: Celery configured; Redis suggested for broker (configurable for local/Docker).
- Caching: Redis (in Docker) or local memory cache, used directly in views for simple caching and rate limiting.
- Deployment: Render.com notes and Docker/Compose present. WhiteNoise for static in production.


## 2. Project Structure (selected)

- ohmi_audit/
  - ohmi_audit/
    - settings.py — Single settings module with environment-driven branching (Render, Docker, local) for DB, Cache, Celery, CORS, i18n, static/media.
    - urls.py — Root URL configuration with admin, main_app, hr_management, i18n.
    - main_app/
      - models.py — Core domain models: Audit, Auditor, Customer, AppUser (custom user).
      - forms.py — Django forms for UI flows (e.g., AuditForm, Login/Signup forms) and mixins for styling.
      - views.py — Class-based views for UI, DRF APIViews for data access, Celery demo view.
      - tasks.py — Celery tasks (referenced by views.TaskTestView).
      - urls.py — URL routes for web and API endpoints.
    - hr_management/
      - views.py — Simple index view rendering a template.
      - urls.py — Routes for HR management section.
  - common/
    - serializers.py — DRF serializers (AuditSerializer, CustomDataSerializer examples).
    - custom_middleware.py — referenced (measure_time_middleware) in settings.
    - common_models_data.py — constants and base behaviors used by models (e.g., CustomModelBase, validators, choices).
  - templates/ — base.html and include fragments compose the UI; main_app/index.html is the primary page.
  - static/ — CSS assets and components; static_files/ is the collectstatic target.
  - tests/
    - main_app/test_models.py — test coverage for core model contracts (validation, slugging, __str__).
  - Dockerfile, docker-compose.yml — containerization; Redis and Postgres are referenced/configurable.
  - render.yaml — Render deployment metadata.
  - pyproject.toml / poetry.lock — dependency management with Poetry; requirements.txt also present.


## 3. Configuration and Environments

- Settings highlights:
  - AUTH_USER_MODEL = 'main_app.AppUser'.
  - DEBUG read from env; SECRET_KEY from env (.env supported via python-dotenv).
  - INSTALLED_APPS include: main_app, hr_management, django.contrib.*, celery, django_celery_results, corsheaders, rest_framework.
  - Middleware includes corsheaders, WhiteNoise, custom timing middleware, and LocaleMiddleware.
  - Templates configured with DIRS=[BASE_DIR/'templates'] and i18n context processor.
  - Database: Docker branch uses discrete env vars; otherwise dj_database_url reads DATABASE_URL. (SQLite and direct Postgres examples are commented.)
  - Cache: Redis in Docker; LocMem fallback otherwise. Sessions use cached backend.
  - Celery: Redis broker (localhost or Docker hostname), result backend via django-db.
  - Static: WhiteNoise storage, STATIC_URL=/static/, STATICFILES_DIRS=(static,), STATIC_ROOT=static_files.
  - Media: MEDIA_URL=/media/, MEDIA_ROOT=media_files.
  - i18n: LANGUAGE_CODE=en-us, TIME_ZONE=Europe/Sofia, LANGUAGES=[('en','English'),('bg','Bulgarian')], LOCALE_PATHS=['localization/locale'].
  - CORS: Allowed origins via env; credentials allowed.

- Observations:
  - settings.py contains extensive operational notes and walkthroughs. Consider splitting into settings modules (base.py, dev.py, prod.py, docker.py) for clarity and safety.
  - Some commented configuration includes sensitive example credentials; best to remove or redact in public repos.


## 4. URLs and Routing

- Root urls.py:
  - Adds i18n route and admin.
  - Includes main_app and hr_management twice (plain and inside i18n_patterns). This doubles routes under both non-prefixed and language-prefixed paths.
- main_app/urls.py exposes:
  - UI routes: index, login, logout, signup, about-us, redirect-from-here, celery-example, task-status, health.
  - API routes: api-endpoint-example-model, api-endpoint-example-custom-data.
- hr_management/urls.py: HR index path under /hr-management/.

Recommendation: In production, prefer a single inclusion (usually only i18n_patterns with prefix_default_language as needed) to avoid duplicate routes and SEO issues.


## 5. Domain Model Layer

- CustomModelBase (from common.common_models_data) underpins domain entities and enforces:
  - A base __str__ delegating to get_display_name.
  - Slug generation on save (verified by tests).
  - validate_model hook invoked via clean to centralize domain validation.
- Entities:
  - Audit: name, description, date, is_active, category, image/file uploads; commented many-to-many to Auditor via an explicit through model with business rules for a single lead auditor.
  - Auditor: first_name, last_name, email(unique), phone(unique).
  - Customer: first_name, last_name, address, phone(unique), email(unique).
  - AppUser: custom user extending AbstractUser with adjusted fields and related_names for groups/permissions.

Observations:
  - Validation is thoughtfully centralized via validate_model, with tests asserting expected behavior.
  - File/image storage is local; production may need S3/GCS when scaling.


## 6. Views and API Layer

- Web UI Views (CBVs):
  - IndexView(LoginRequiredMixin) renders index.html; uses a form (AuditForm) and table of audits; caching per-user of queryset; supports create/edit/delete via POST button names and session editing_id.
  - Login/Logout/SignUp flows implemented with messages and cache-based rate limiting for login.
  - Celery TaskTestView triggers a long-running task and displays status via task_status endpoint and a template include.

- API Views (DRF):
  - ModelEndPointView lists audits (GET) and validates POST payload but does not save (serializer.save() commented) — likely a demo.
  - CustomDataEndPointView returns simple serialized data; validates POST and echoes back data.

Observations:
  - The API layer is minimal and example-oriented; consider DRF ViewSets + Routers for consistency and versioned API namespaces.
  - Rate limiting in LoginView uses cache; if Redis is enabled, this is fine; otherwise LocMem will be per-process.


## 7. Templates and Frontend Composition

- base.html establishes consistent blocks (page_title, additional_styles/js, nav, content areas, footer) and includes components.
- includes/left_menu_bar.html links to core sections and the async example.
- includes/content_container.html displays a generic form block and a table listing Audit fields with image/file rendering and pagination include.
- main_app/index.html nests card buttons bar and content container into right bar.

Observations:
  - The template structure is clean and modular; internationalization strings are present via {% trans %} and i18n context is enabled.


## 8. Static and Media

- Static is organized into components; WhiteNoise is configured for production.
- Media files live in media_files/ with audit_images/ and audit_files/ directories matched by model upload_to.

Recommendation: For production deployments behind multiple dynos/containers, move media storage to a shared object store (S3/GCS) and use django-storages.


## 9. Background Processing and Caching

- Celery is configured with Redis as broker; result backend uses django-db (django_celery_results installed).
- Example long_running_task is triggered from UI; progress is polled via task_status returning AsyncResult info.
- Cache is Redis in Docker or LocMem; sessions use cached backend; views use cache for queryset memoization and login rate limiting.

Recommendation: Centralize Celery app configuration (celery.py with autodiscover) and separate tasks into domain-focused modules. Consider result backend via Redis for performance if required.


## 10. Security, CORS, and Auth

- CORS configured via env; credentials allowed.
- Login rate limiting is in place.
- DEBUG is env-driven; SECRET_KEY from env.
- Custom user model is used and declared early in settings.

Recommendations:
  - Ensure CSRF_TRUSTED_ORIGINS and ALLOWED_HOSTS are set via env in production.
  - Remove sample credentials from comments; avoid committing secrets anywhere (even commented).
  - Consider DRF authentication/permission defaults if API is intended for production.


## 11. Testing Strategy

- tests/main_app/test_models.py provides good coverage for common model contracts, validation, slugging, and __str__.
- App-level tests.py placeholders exist but are empty.

Recommendations:
  - Add tests for forms, views (including login rate limiting), serializers, and API endpoints (pytest + pytest-django suggested).
  - Add Celery task tests using e.g. celery app test settings or EAGER mode.


## 12. Deployment and DevOps

- Docker/Compose present; settings support DOCKER and USE_REDIS env flags.
- Render deployment documented in settings comments and render.yaml.
- WhiteNoise serves static in production; collectstatic documented.

Recommendations:
  - Use separate settings modules: settings/base.py, settings/dev.py, settings/prod.py, settings/docker.py with a DJANGO_SETTINGS_MODULE switch.
  - Establish a .env.example documenting all required env variables.
  - Add pre-commit hooks (black, isort, flake8, django upgrade checker) and CI (GitHub Actions) for tests and linting.


## 13. Notable Strengths

- Clean domain model patterns with centralized validation and common base behavior.
- Clear template composition and componentization.
- i18n correctly wired (LocaleMiddleware, context processor, LOCALE_PATHS).
- Caching and Celery are integrated with sensible defaults for local and Docker.


## 14. Improvement Roadmap

1) Settings and Secrets
- Split settings into multiple files: base/dev/prod/docker.
- Remove sensitive example credentials and operational notes from settings; move runbooks to docs/.
- Add .env.example and ensure .env is gitignored.

2) API Layer
- Introduce DRF ViewSets and Routers for Audit/Auditor/Customer resources.
- Add API versioning (e.g., /api/v1/), default permissions, throttling.
- Use serializers in dedicated app module (e.g., main_app/api/serializers.py) or keep under common but avoid wildcard imports.

3) URL/i18n
- Avoid double inclusion of app URLs both outside and inside i18n_patterns; choose one strategy (likely only i18n_patterns in production) to prevent duplicates.

4) Services and Separation of Concerns
- Extract business logic from views into a services layer (e.g., main_app/services/audits.py) and forms for validation.
- Keep views thin: orchestrate forms/services; avoid direct cache logic scattered across views.

5) Storage
- Plan for object storage (S3) for media in production, using django-storages, configuring MEDIA_URL to cloud CDN.

6) Celery
- Create a celery.py initializer, autodiscover tasks, configure logging, and consider Redis result backend if needed.
- Separate task modules by domain for maintainability.

7) Caching and Rate Limiting
- If running multiple processes without Redis, switch to a shared cache (Redis) to make rate limiting effective across workers.
- Consider DRF throttling classes for API.

8) Testing and Quality
- Expand unit/functional tests for forms, views, and API; use pytest.
- Add type annotations and mypy for critical modules.
- Add black/isort/flake8 pre-commit configuration.

9) Observability
- Configure Django LOGGING settings (structured logging), error reporting (Sentry), and health checks (already a simple health endpoint exists).

10) Documentation
- Move operational how-tos out of settings.py into docs/ (Deployment guide, Runbook, Celery, Docker). Keep settings.py lean.


## 15. Potential Cleanups (Low Risk)

- Replace wildcard imports (from ohmi_audit.main_app.models import *) with explicit imports for clarity in serializers and tests.
- In IndexView POST logic, consider FormView or separate endpoints for edit/delete to avoid overloading a single handler; or keep pattern but extract to service functions.
- Use login throttling with a key that also considers username to prevent single IP collateral effects.
- Ensure main urls.py only registers i18n_patterns (or only non-i18n), not both.


## 16. Data Flow Summary

- Requests enter via urls.py to either web views (rendering index.html and includes) or DRF APIViews.
- Web: Forms submit to IndexView; creation or update saved via AuditForm; list of audits is cached per-user; media displayed in table; pagination decorator applied.
- API: ModelEndPointView fetches and serializes Audits; POST validates but does not persist (demo behavior).
- Background: TaskTestView triggers Celery task; UI polls task_status for progress.


## 17. Suggested Next Steps

- Decide the i18n URL strategy and adjust ohmi_audit/urls.py accordingly.
- Extract settings into a multi-module structure and remove secrets from comments.
- Introduce a minimal DRF ViewSet for Audit with a router under /api/v1/.
- Add .env.example and a docs/Deployment.md summarizing Render and Docker instructions.
- Add pre-commit and GitHub Actions for run checks and tests.
