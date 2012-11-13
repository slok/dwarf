from django.test import TestCase

from linkshortener import utils
from linkshortener.exceptions import LinkShortenerLengthError


class UtilTest(TestCase):
    def test_first_shortened_url_token(self):
        next = utils.next_token()
        self.assertEquals("0000", next)

    def test_small_current_shortened_url_token(self):
        self.assertRaises(LinkShortenerLengthError, utils.next_token, "a")

    def test_next_shortened_url_token(self):
        test_data = (
                        ("0000", "0001"), ("0005", "0006"), ("0008", "0009"),
                        ("0009", "000a"), ("000b", "000c"), ("000o", "000p"),
                        ("000z", "000A"), ("000G", "000H"), ("000Y", "000Z"),
                        ("000Z", "0010"), ("34ZZ", "3500"), ("aabz", "aabA"),
                        ("a00z", "a00A"), ("Az3d", "Az3e"), ("YZZZ", "Z000"),
                    )

        for i in test_data:
            self.assertEquals(i[1], utils.next_token(i[0]))

    def test_next_shortened_url_token_limits(self):
        test_data = (
                        ("ZZZZZ", "000000"), ("ZZZZZZZZ", "000000000")
                    )

        for i in test_data:
            self.assertEquals(i[1], utils.next_token(i[0]))

    #Based on counter checks

    test_data = (
                        ("0000", 0), ("0005", 5), ("0006", 6), ("0009", 9),
                        ("000a", 10), ("000s", 28), ("000E", 40), ("000Z", 61),
                        ("0010", 62), ("001C", 100), ("0q0U", 100000),
                    )

    def test_start_counter_translation(self):
        counter = 0
        self.assertEquals("0000", utils.counter_to_token(counter))

    def test_counter_translation(self):
        for i in UtilTest.test_data:
            self.assertEquals(i[0], utils.counter_to_token(i[1]))

    def test_number_translation(self):

        for i in UtilTest.test_data:
            self.assertEquals(i[1], utils.token_to_counter(i[0]))
