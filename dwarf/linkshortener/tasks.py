from celery import task


from models import ShortLink


@task()
def create_token(url):
    # Get the next counter to create the token
    counter = ShortLink.incr_counter()

    # Create the instance with the data
    sl = ShortLink()
    sl.counter = counter
    sl.url = url

    # Save
    sl.save()

    # Return the new token
    return sl.token


@task()
def add(x, y):
    return x + y
