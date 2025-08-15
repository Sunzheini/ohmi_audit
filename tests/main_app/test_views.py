from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model


User = get_user_model()


class IndexViewTests(TestCase):
    def test_requires_login_redirects_anonymous(self):
        resp = self.client.get(reverse('index'))
        # LoginRequiredMixin redirects to /login/?next=/
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.url)

    def test_get_authenticated_ok(self):
        user = User.objects.create_user(username='u', email='u@example.com', password='p', first_name='U')
        self.client.login(username='u', password='p')
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)


class LoginViewRateLimitTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        # Create a valid user
        self.user = User.objects.create_user(
            username='john', email='john@example.com', password='secret123', first_name='John'
        )

    def tearDown(self):
        # Ensure cache state from one test doesn't affect others
        from django.core.cache import cache
        cache.clear()

    def test_rate_limiting_blocks_after_5_failures(self):
        # 5 failed attempts
        for _ in range(5):
            resp = self.client.post(self.login_url, {"username": "john", "password": "wrong"})
            self.assertEqual(resp.status_code, 200)
        # 6th attempt with wrong password remains blocked (status 200, not redirect)
        resp = self.client.post(self.login_url, {"username": "john", "password": "wrong"})
        self.assertEqual(resp.status_code, 200)
        # 7th attempt even with correct password should be blocked due to rate limit
        resp2 = self.client.post(self.login_url, {"username": "john", "password": "secret123"})
        self.assertEqual(resp2.status_code, 200)

    def test_successful_login_resets_attempts(self):
        # a couple of failed attempts
        for _ in range(2):
            self.client.post(self.login_url, {"username": "john", "password": "wrong"})
        # successful login should reset cache attempts
        resp = self.client.post(self.login_url, {"username": "john", "password": "secret123"})
        # redirect to index on success
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse('index'))
