import shutil
import tempfile
from io import BytesIO

from PIL import Image as PilImage
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Asteroid, Composition, Order, Profile, SpectralClass

TEST_MEDIA_ROOT = tempfile.mkdtemp()


def make_image(name='test.png'):
    buffer = BytesIO()
    PilImage.new('RGB', (12, 12), (48, 43, 192)).save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


class BaseAppTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.spectral = SpectralClass.objects.create(name='M-Type')
        cls.composition = Composition.objects.create(name='руда')
        cls.staff = User.objects.create_user(
            username='admin-test',
            email='admin@test.ru',
            password='pass12345',
            is_staff=True,
            is_superuser=True,
        )
        cls.user = User.objects.create_user(
            username='user@test.ru',
            email='user@test.ru',
            password='pass12345',
        )
        Profile.objects.get_or_create(user=cls.user)
        cls.asteroid = Asteroid.objects.create(
            title='Тестовый лот',
            description='Описание тестового лота',
            price=1000,
            distance=500,
            spectral_class=cls.spectral,
            status='in_sale',
        )
        cls.asteroid.compositions.set([cls.composition])
        cls.asteroid.image.save('base.png', make_image('base.png'), save=True)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class PublicPagesTests(BaseAppTestCase):
    def test_public_pages(self):
        for name in ('index', 'catalog', 'login', 'register'):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

        response = self.client.get(reverse('asteroid_detail', args=[self.asteroid.pk]))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('profile')}",
        )


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class AuthTests(BaseAppTestCase):
    def test_login_by_username_and_email(self):
        response = self.client.post(
            reverse('login'),
            {'email': 'admin-test', 'password': 'pass12345'},
        )
        self.assertRedirects(response, reverse('index'))

        self.client.logout()
        response = self.client.post(
            reverse('login'),
            {'email': 'admin@test.ru', 'password': 'pass12345'},
        )
        self.assertRedirects(response, reverse('index'))

    def test_login_error(self):
        response = self.client.post(
            reverse('login'),
            {'email': 'admin-test', 'password': 'wrong'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Неверный логин')

    def test_register(self):
        email = 'new-user@test.ru'
        response = self.client.post(
            reverse('register'),
            {
                'email': email,
                'password': 'pass12345',
                'password2': 'pass12345',
            },
        )
        self.assertRedirects(response, reverse('index'))
        user = User.objects.get(username=email)
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_profile_update(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('profile'),
            {'name': 'Новое имя', 'email': 'updated@test.ru'},
        )
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Новое имя')
        self.assertEqual(self.user.email, 'updated@test.ru')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class AdminPanelTests(BaseAppTestCase):
    def setUp(self):
        self.client.force_login(self.staff)

    def test_access(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('admin_panel')).status_code, 302)

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('admin_panel')).status_code, 302)

        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('admin_panel')).status_code, 200)

    def test_add_requires_image(self):
        data = {
            'title': 'Новый лот',
            'description': 'Описание нового лота',
            'price': '2000',
            'distance': '1000',
            'spectral_class': self.spectral.pk,
            'compositions': [self.composition.pk],
            'status': 'in_sale',
        }
        response = self.client.post(reverse('admin_lot_add'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Asteroid.objects.filter(title='Новый лот').exists())

        data['image'] = make_image('new-lot.png')
        response = self.client.post(reverse('admin_lot_add'), data)
        self.assertRedirects(response, reverse('admin_panel'))
        self.assertTrue(Asteroid.objects.filter(title='Новый лот').exists())

    def test_edit_and_delete_keeps_and_replaces_image(self):
        old_name = self.asteroid.image.name
        data = {
            'title': 'Тестовый лот',
            'description': 'Новое описание',
            'price': '1500',
            'distance': '600',
            'spectral_class': self.spectral.pk,
            'compositions': [self.composition.pk],
            'status': 'in_sale',
        }

        response = self.client.post(reverse('admin_lot_edit', args=[self.asteroid.pk]), data)
        self.assertRedirects(response, reverse('admin_panel'))
        self.asteroid.refresh_from_db()
        self.assertEqual(self.asteroid.image.name, old_name)

        data['image'] = make_image('replacement.png')
        response = self.client.post(reverse('admin_lot_edit', args=[self.asteroid.pk]), data)
        self.assertRedirects(response, reverse('admin_panel'))
        self.asteroid.refresh_from_db()
        new_name = self.asteroid.image.name
        self.assertNotEqual(new_name, old_name)
        self.assertFalse(default_storage.exists(old_name))
        self.assertTrue(default_storage.exists(new_name))

        response = self.client.post(reverse('admin_lot_delete', args=[self.asteroid.pk]))
        self.assertRedirects(response, reverse('admin_panel'))
        self.assertFalse(Asteroid.objects.filter(pk=self.asteroid.pk).exists())
        self.assertFalse(default_storage.exists(new_name))

    def test_orders_and_users_pages(self):
        order = Order.objects.create(
            user=self.user,
            asteroid=self.asteroid,
            code='#SO-TEST',
            status='in_transit',
        )

        self.assertEqual(self.client.get(reverse('admin_orders')).status_code, 200)
        self.assertEqual(self.client.get(reverse('admin_users')).status_code, 200)

        response = self.client.post(reverse('admin_order_toggle', args=[order.pk]))
        self.assertRedirects(response, reverse('admin_orders'))
        order.refresh_from_db()
        self.assertEqual(order.status, 'completed')


def tearDownModule():
    shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)
