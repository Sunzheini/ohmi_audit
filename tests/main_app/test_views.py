import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestIndexView:
    def test_requires_login_redirects_anonymous(self, client):
        resp = client.get(reverse('index'))
        # LoginRequiredMixin redirects to /login/?next=/
        assert resp.status_code == 302
        assert reverse('login') in resp.url

    def test_get_authenticated_ok(self, client):
        user = User.objects.create_user(username='u', email='u@example.com', password='p', first_name='U')
        client.login(username='u', password='p')
        resp = client.get(reverse('index'))
        assert resp.status_code == 200


@pytest.mark.django_db
class TestLoginViewRateLimit:
    @pytest.fixture(autouse=True)
    def setup(self, client, clear_cache):
        self.client = client
        self.login_url = reverse('login')
        # Create a valid user
        self.user = User.objects.create_user(
            username='john', email='john@example.com', password='secret123', first_name='John'
        )

    def test_rate_limiting_blocks_after_5_failures(self):
        # 5 failed attempts
        for _ in range(5):
            resp = self.client.post(self.login_url, {"username": "john", "password": "wrong"})
            assert resp.status_code == 200
        # 6th attempt with wrong password remains blocked (status 200, not redirect)
        resp = self.client.post(self.login_url, {"username": "john", "password": "wrong"})
        assert resp.status_code == 200
        # 7th attempt even with correct password should be blocked due to rate limit
        resp2 = self.client.post(self.login_url, {"username": "john", "password": "secret123"})
        assert resp2.status_code == 200

    def test_successful_login_resets_attempts(self):
        # a couple of failed attempts
        for _ in range(2):
            self.client.post(self.login_url, {"username": "john", "password": "wrong"})
        # successful login should reset cache attempts
        resp = self.client.post(self.login_url, {"username": "john", "password": "secret123"})
        # redirect to index on success
        assert resp.status_code == 302
        assert resp.url == reverse('index')
