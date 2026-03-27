# ohmi_audit

A program for managing audits by a certification company.

---

## Table of Contents

1. [Run Tests](#run-tests)
2. [Local Development (no Docker)](#local-development-no-docker)
3. [Local Development with Docker](#local-development-with-docker)
4. [Deploy to AWS EC2 (Full Guide)](#deploy-to-aws-ec2-full-guide)
5. [Useful Commands](#useful-commands)

---

## Run Tests

```powershell
# Local (PyCharm / terminal)
poetry run pytest -v

# Inside running Docker container
docker compose exec web pytest -v
```

---

## Local Development (no Docker) — PyCharm

Run Django directly in PyCharm while Postgres and Redis run in lightweight
Docker containers (no full docker-compose stack needed).

### Start backing services

```powershell
# Start only Postgres + Redis (first time or after docker-compose.services.yml changes)
docker compose -f docker-compose.services.yml up -d

# Stop (keeps DB data)
docker compose -f docker-compose.services.yml down

# Full reset (wipes DB)
docker compose -f docker-compose.services.yml down -v
```

> The `.env` has `DOCKER=False`, so Django connects to `localhost:5432` and
> `localhost:6379` — exactly what these containers expose.

### Run Django

```powershell
# First time only — installs all dependencies into .venv
poetry install

# Apply any new migrations
poetry run python manage.py migrate

# Start the dev server
poetry run python manage.py runserver
```


Access: http://127.0.0.1:8000
---

## Local Development with Docker

All services (Django, PostgreSQL, Redis) run in containers.
`entrypoint.sh` automatically runs `collectstatic` and `migrate` on every container start.

```powershell
# First time or after any code change вЂ” build + run
docker compose up --build

# Subsequent runs (no code changes)
docker compose up

# Stop (keeps DB data)
docker compose down

# Full reset (wipes DB volumes)
docker compose down -v
```

Access: http://localhost:8000

> **Note**: `docker-compose.yml` automatically overrides `DOCKER=False` from `.env`
> with `DOCKER=True` via the `environment:` section, so the DB host resolves to the
> `db` container instead of `localhost`.
>
> Use `docker-compose.services.yml` (see above) if you only need Postgres + Redis
> and want to run Django from PyCharm.

---

## Deploy to AWS EC2 (Full Guide)

### Architecture

```
Local machine            Docker Hub               AWS EC2
в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ   push в†’  в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ   pull в†’   в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
docker build             sunzheini1407/           web  (gunicorn)
docker push              ohmi_audit:latest        db   (postgres:13)
                                                  redis (redis:6)
```

On EC2 there is **no source code** and **no Dockerfile** вЂ” only:
- `docker-compose.yml` (copied once from `docker-compose.prod.yml`)
- `.env` (created manually on EC2)

---

### Step 0 вЂ” One-time: AWS Security Group

In **AWS Console в†’ EC2 в†’ Security Groups в†’ your instance's SG в†’ Inbound Rules**, add:

| Type       | Protocol | Port | Source    | Purpose             |
|------------|----------|------|-----------|---------------------|
| SSH        | TCP      | 22   | My IP     | Your SSH access     |
| Custom TCP | TCP      | 8000 | 0.0.0.0/0 | Public web access   |

> рџ’Ў Assign an **Elastic IP** (EC2 в†’ Elastic IPs в†’ Allocate в†’ Associate) so the IP
> never changes after a restart.

---

### Step 1 вЂ” One-time: Fix .pem Key Permissions (PowerShell)

```powershell
# !! Set this to your actual .pem file path before running any command below !!
$pem = "D:\BigBusiness\OhmiCert\19.03.2026\keypair1.pem"
icacls $pem /inheritance:r
icacls $pem /grant:r "${env:USERNAME}:R"
```

---

### Step 2 вЂ” One-time: SSH Into EC2

```powershell
# EC2 public IP is shown in AWS Console в†’ EC2 в†’ Instances
ssh -i "D:\BigBusiness\OhmiCert\19.03.2026\keypair1.pem" ec2-user@13.62.222.241
```

---

### Step 3 вЂ” One-time: Install Docker on EC2 (Amazon Linux 2)

```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
exit   # re-login for group change to take effect
```

Reconnect, then verify:
```bash
docker --version
```

---

### Step 4 вЂ” One-time: Install Docker Compose Plugin on EC2

```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
     -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version   # verify
```

---

### Step 5 вЂ” One-time: Transfer Files to EC2

Run from your **local PowerShell** (not EC2):

```powershell
$pem  = "D:\BigBusiness\OhmiCert\19.03.2026\keypair1.pem"
$ec2  = "ec2-user@13.62.222.241"
$proj = "D:\Study\Projects\PycharmProjects\ohmi_audit"

# Create app folder on EC2
ssh -i $pem $ec2 "mkdir -p ~/app"

# Transfer the production docker-compose as docker-compose.yml
scp -i $pem "$proj\docker-compose.prod.yml" "${ec2}:~/app/docker-compose.yml"

# Transfer .env (secrets вЂ” never commit to git)
scp -i $pem "$proj\.env" "${ec2}:~/app/.env"
```

---

### Step 6 вЂ” One-time: Harden .env on EC2

SSH into EC2 and edit the file:

```bash
nano ~/app/.env
```

Change these values for production:

```dotenv
DEBUG=False
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(50))">

ALLOWED_HOSTS=localhost,127.0.0.1,web,13.62.222.241
CSRF_TRUSTED_ORIGINS=http://13.62.222.241:8000

DB_PASSWORD=<use-a-strong-password>
```

> ⚠️ Never use the insecure dev `SECRET_KEY` in production.  
> `docker-compose.yml` reads `DB_PASSWORD` via `${DB_PASSWORD}` substitution,  
> so Postgres and Django always stay in sync — no other file to edit.

---

### Step 7 вЂ” Every Deployment: Build + Push + Deploy

**Local machine (PowerShell) вЂ” after every code change:**

```powershell
cd "D:\Study\Projects\PycharmProjects\ohmi_audit"

docker login   # once per session; Docker Hub user: sunzheini1407

docker build -t sunzheini1407/ohmi_audit:latest .
docker push sunzheini1407/ohmi_audit:latest
```

**EC2 (bash) вЂ” pull and restart:**

```bash
cd ~/app
docker pull sunzheini1407/ohmi_audit:latest
docker compose down
docker compose up -d
docker compose ps   # all should be Up
```

Access: `http://13.62.222.241:8000`

> `entrypoint.sh` (baked into the image) runs `collectstatic` and `migrate`
> automatically before gunicorn starts вЂ” no manual migration step needed.

---

### Step 8 вЂ” One-time: Create Superuser on EC2

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Useful Commands

### Local Docker

```powershell
# View logs
docker compose logs -f web

# Django shell
docker compose exec web python manage.py shell

# Run tests
docker compose exec web pytest -v

# Full rebuild from scratch
docker compose down -v
docker compose up --build
```

### EC2

```bash
# View live logs
docker compose logs -f web

# Free up disk (safe вЂ” does not touch running containers or DB volumes)
docker system prune -af

# Check disk usage
df -h

# Restart without re-pulling
docker compose restart

# Force re-pull and restart (after new push)
docker pull sunzheini1407/ohmi_audit:latest
docker compose down
docker compose up -d
```

### `no space left on device` on EC2

```bash
docker system prune -af   # removes stopped containers, unused images
df -h                     # check free space
```

If still full, expand the EBS volume in AWS Console в†’ EC2 в†’ Volumes в†’ Modify Volume.

---

## Notes

- `entrypoint.sh` runs `collectstatic` and `migrate` on every container start.
  Both are idempotent вЂ” safe to run repeatedly.
- `DOCKER=False` in `.env` is overridden to `DOCKER=True` by the `environment:`
  section in docker-compose files вЂ” no need to edit `.env` when using Docker.
- `.env` is in `.gitignore` and `.dockerignore` вЂ” never pushed to GitHub or baked
  into the image. Must be created manually on each machine.
- EC2 `t2.micro` (free tier) may struggle with Gunicorn. Use `t2.small` or larger.
- If EC2 IP changes after a restart (no Elastic IP), update `ALLOWED_HOSTS` and
  `CSRF_TRUSTED_ORIGINS` in `~/app/.env` and run `docker compose restart web`.


