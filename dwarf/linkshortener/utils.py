from settings import START_URL_TOKEN_LENGTH, ALPHABET
from linkshortener.exceptions import LinkShortenerLengthError


def next_token(current=None):
    """Generates the next token based on a current token (start in
    START_URL_TOKEN_LENGHT chars).
    The token starts with digit(0-9), then small letters(a-z) and then cap
    letters (A-Z) so for example from low to high:
        - 0000
        - 0001
        - 000a
        - 000A
        - 001a
        - 001A
        - ZZZZ
        - 00000

    : param current: the previous token to the one that needs to be generated
    """
    if not current:
        return ALPHABET[0] * START_URL_TOKEN_LENGTH
    else:

        # Check the length
        if len(current) < START_URL_TOKEN_LENGTH:
            raise LinkShortenerLengthError()

        result = list(current)
        #Check every char
        for index in range(len(current) - 1, -1, -1):

            char = current[index]

            # Reset this token to
            if char == ALPHABET[len(ALPHABET) - 1]:
                result[index] = ALPHABET[0]
            # Take the next character
            else:
                result[index] = ALPHABET[ALPHABET.index(char) + 1]
                break

        # Join all the chars to get the final result
        result = "".join(result)

        # Maximun of combinations reached? add one more!
        # We know because the number is reseted to the start number
        if result == len(current) * ALPHABET[0]:
            result += ALPHABET[0]

        return result
