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
## Local Development (no Docker) � PyCharm

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
> `localhost:6379` � exactly what these containers expose.

### Run Django

```powershell
# First time only � installs all dependencies into .venv
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
# First time or after any code change — build + run
docker compose up --build

# Subsequent runs (no code changes)
docker compose up

# Stop (keeps DB data)
docker compose down

# Full reset (wipes DB volumes)
docker compose down -v
```

```
# run in a separate terminal:
docker compose exec web python manage.py createsuperuser
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
─────────────   push →  ────────────   pull →   ──────────────────────────
docker build             sunzheini1407/           web  (gunicorn)
docker push              ohmi_audit:latest        db   (postgres:13)
                                                  redis (redis:6)
```

On EC2 there is **no source code** and **no Dockerfile** — only:
- `docker-compose.yml` (copied once from `docker-compose.prod.yml`)
- `.env` (created manually on EC2)

---

### Step 0 — One-time: AWS Security Group


1. In the EC2 console, click "Security Groups" in the left navigation pane.
2. Find and select the security group associated with your instance.
3. Click the "Inbound rules" tab, then the "Edit inbound rules" button.

In **AWS Console → EC2 → Security Groups → your instance's SG → Inbound Rules**, add:

| Type       | Protocol | Port | Source    | Purpose             |
|------------|----------|------|-----------|---------------------|
| SSH        | TCP      | 22   | My IP          | Your SSH access     |
| Custom TCP | TCP      | 8000 | Anywhere IPv4  | Public web access   |

> 💡 Assign an **Elastic IP** (EC2 → Elastic IPs → Allocate → Associate) so the IP
> never changes after a restart.

---

### Step 1 — One-time: Fix .pem Key Permissions (PowerShell)

```powershell
# !! Set this to your actual .pem file path before running any command below !!
$pem = "D:\BigBusiness\OhmiCert\19.03.2026\keypair1.pem"
icacls $pem /inheritance:r                              # remove all inherited ACEs
icacls $pem /remove "NT AUTHORITY\Authenticated Users"  # remove explicit broad ACE
icacls $pem /remove "BUILTIN\Users"                     # remove Users group ACE
icacls $pem /grant:r "${env:USERNAME}:R"                # grant read to current user only
icacls $pem                                             # verify: only your user + Administrators + SYSTEM
```

---

### Step 2 — One-time: SSH Into EC2

```powershell
# EC2 public IP is shown in AWS Console → EC2 → Instances
ssh -i "D:\BigBusiness\OhmiCert\19.03.2026\keypair1.pem" ec2-user@13.50.70.50
```

---

### Step 3 — One-time: Install Docker on EC2 (Amazon Linux 2)

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

### Step 4 — One-time: Install Docker Compose Plugin on EC2

```bash
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
docker compose version   # verify
```

---

### Step 5 — One-time: Transfer Files to EC2

Run from your **local PowerShell** (not EC2):

```powershell
$pem  = "D:\BigBusiness\OhmiCert\19.03.2026\keypair1.pem"
$ec2  = "ec2-user@13.50.70.50"
$proj = "D:\Study\Projects\PycharmProjects\ohmi_audit"

# Create app folder on EC2
ssh -i $pem $ec2 "mkdir -p ~/app"

# Transfer the production docker-compose as docker-compose.yml
scp -i $pem "$proj\docker-compose.prod.yml" "${ec2}:~/app/docker-compose.yml"

# Transfer .env.prod as .env — already fully production-ready, no editing on EC2 needed
scp -i $pem "$proj\.env.prod" "${ec2}:~/app/.env"
```

> `.env.prod` has a real `SECRET_KEY` already baked in, `DEBUG=False`, and
> the correct `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` for `13.50.70.50`.
> Nothing to touch on EC2 after this step.

---

### Step 6 — Every Deployment: Build + Push + Deploy

**Local machine (PowerShell) — after every code change:**

```powershell
cd "D:\Study\Projects\PycharmProjects\ohmi_audit"

docker login   # once per session; Docker Hub user: sunzheini1407

docker build -t sunzheini1407/ohmi_audit:latest .
docker push sunzheini1407/ohmi_audit:latest
```

**EC2 (bash) — pull and restart:**

```bash
cd ~/app
docker pull sunzheini1407/ohmi_audit:latest
docker compose down
docker compose up -d
docker compose ps   # all should be Up
```

Access: `http://13.50.70.50:8000`

> `entrypoint.sh` (baked into the image) runs `collectstatic` and `migrate`
> automatically before gunicorn starts — no manual migration step needed.

---

### Step 7 — One-time: Create Superuser on EC2

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

# Free up disk (safe — does not touch running containers or DB volumes)
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

If still full, expand the EBS volume in AWS Console → EC2 → Volumes → Modify Volume.

---

## Notes

- `entrypoint.sh` runs `collectstatic` and `migrate` on every container start.
  Both are idempotent — safe to run repeatedly.
- `DOCKER=False` in `.env` is overridden to `DOCKER=True` by the `environment:`
  section in docker-compose files — no need to edit `.env` when using Docker.
- `.env` is in `.gitignore` and `.dockerignore` — never pushed to GitHub or baked
  into the image. Must be created manually on each machine.
- EC2 `t2.micro` (free tier) may struggle with Gunicorn. Use `t2.small` or larger.
- If EC2 IP changes after a restart (no Elastic IP), update `ALLOWED_HOSTS` and
  `CSRF_TRUSTED_ORIGINS` in `~/app/.env` and run `docker compose restart web`.
