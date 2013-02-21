from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from userprofile.models import Profile
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
