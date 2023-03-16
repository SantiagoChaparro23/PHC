from django.test import SimpleTestCase
from django.urls import reverse, resolve

from users.views import login_view, logout_view

class TestUrls(SimpleTestCase):
    def test_login_url_is_resolved(self):
        url = reverse('users:login')    
        self.assertEqual( resolve(url).func, login_view )
      
