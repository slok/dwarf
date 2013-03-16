from django.test import LiveServerTestCase, TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from userprofile.models import Profile
from userprofile.forms import SignupForm
from dwarfutils.hashutils import get_random_hash


class AccountActionvationTests(LiveServerTestCase):

    def test_user_activation(self):
        """
        Tests if the user activation works
        """

        user = User()
        user.username = "test"
        user.save()

        profile = Profile.objects.get(user=user)
        self.assertFalse(profile.activated)

        user_id = user.id
        user_token = profile.activation_token

        url = reverse("userprofile-activate", args=(user_id, user_token))

        self.client.get(url)

        profile = Profile.objects.get(user=user)
        self.assertTrue(profile.activated)

    def test_user_whrong_activation(self):
        """
        Tests if the user activation works worng
        """

        user = User()
        user.username = "test"
        user.save()

        profile = Profile.objects.get(user=user)
        self.assertFalse(profile.activated)

        user_id = user.id
        user_token = get_random_hash()

        url = reverse("userprofile-activate", args=(user_id, user_token))

        self.client.get(url)

        profile = Profile.objects.get(user=user)
        self.assertFalse(profile.activated)


class SignupFormTests(TestCase):

    def test_missing_field_username(self):
        form_data = {
            'username': '',
            'password1': 'p455w0rd',
            'password2': 'p455w0rd',
            'email': 'slok@slok.org',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("username" in form.errors)
        #self.assertTrue(unicode(_(u"This field is required.")) in form.errors)

    def test_missing_field_password(self):
        form_data = {
            'username': 'slok',
            'password1': '',
            'password2': 'p455w0rd',
            'email': 'slok@slok.org',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("password1" in form.errors)
        #self.assertTrue(unicode(_(u"This field is required.")) in form.errors)

    def test_missing_field_password2(self):
        form_data = {
            'username': 'slok',
            'password1': 'p455w0rd',
            'password2': '',
            'email': 'slok@slok.org',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("password2" in form.errors)
        #self.assertTrue(unicode(_(u"This field is required.")) in form.errors)

    def test_missing_field_email(self):
        form_data = {
            'username': 'slok',
            'password1': 'p455w0rd',
            'password2': 'p455w0rd',
            'email': '',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("email" in form.errors)
        #self.assertTrue(unicode(_(u"This field is required.")) in form.errors)

    def test_different_passwords(self):
        form_data = {
            'username': 'slok',
            'password1': 'p455w0rd',
            'password2': 'p455w0rd2',
            'email': 'slok@slok.org',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("password2" in form.errors)
        #self.assertTrue(unicode(_(u"Your passwords do not match")) in form.errors)

    def test_password_length(self):
        form_data = {
            'username': 'slok',
            'password1': 'p',
            'password2': 'p',
            'email': 'slok@slok.org',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("password2" in form.errors)

        form_data['password1'] = "123456"
        form_data['password2'] = form_data['password1']
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("password2" in form.errors)
        #self.assertTrue(unicode(_(u"Password length needs to be 7 or more")) in form.errors)

        form_data['password1'] = "1234567"
        form_data['password2'] = form_data['password1']
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_correct(self):
        form_data = {
            'username': '-test',
            'password1': 'p455w0rd',
            'password2': 'p455w0rd',
            'email': 'slok@slok.org',
        }
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())

        form_data['username'] = "test_"
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("username" in form.errors)

        form_data['username'] = "-test"
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("username" in form.errors)

        form_data['username'] = "te@st"
        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("username" in form.errors)
        #self.assertTrue(unicode(_(u""Username may only contain alphanumeric characters or dashes and cannot begin with a dash"")) in form.errors)

        form_data['username'] = "te-st"
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data['username'] = "t3st"
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

        form_data['username'] = "3te-st"
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_username_exists(self):
        form_data = {
            'username': 'test',
            'password1': 'p455w0rd',
            'password2': 'p455w0rd',
            'email': 'slok@slok.org',
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Now check with a user
        user = User()
        user.username = "test"
        user.save()

        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("username" in form.errors)

        #self.assertTrue(unicode(_(u"This username is already taken")) in form.errors)

    def test_email_exists(self):
        form_data = {
            'username': 'test',
            'password1': 'p455w0rd',
            'password2': 'p455w0rd',
            'email': 'slok@slok.org',
        }
        form = SignupForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Now check with a user
        user = User()
        user.username = "test2"
        user.email = "slok@slok.org"
        user.save()

        form = SignupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertTrue("email" in form.errors)

        #self.assertTrue(unicode(_(u"This email is already taken")) in form.errors)

    def test_user_signup(self):
        form_data = {
            'username': 'test',
            'password1': 'p455w0rd',
            'password2': 'p455w0rd',
            'email': 'slok@slok.org',
        }

        self.assertRaises(ObjectDoesNotExist, User.objects.get, username="test")

        url = reverse("userprofile-signup")
        resp = self.client.post(url, form_data)
        self.assertEqual(resp.status_code, 200)

        user = User.objects.get(username="test")
        self.assertEqual(form_data['username'], user.username)
        self.assertTrue(user.check_password(form_data['password1']))
        self.assertEqual(form_data['email'], user.email)

    def test_username_login(self):
        form_data = {
            'username': 'test',
            'password': 'p455w0rd',
        }

        user = User()
        user.username = form_data['username']
        user.set_password(form_data['password'])
        user.save()
        
        # Without login
        response = self.client.get(reverse("userprofile-dashboard"))
        self.assertTrue(reverse("userprofile-login") in response.get("location"))

        # With login
        response = self.client.post(reverse("userprofile-login"), form_data)
        self.assertTrue(reverse("userprofile-dashboard") in response.get("location"))