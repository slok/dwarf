from fabric.api import local, lcd
#FOR NOW ONLY LOCAL, TODO: EXTERNAL SERVERS

#---------------------Settings-------------------------------------------------
RABITTMQ_HOME = "/usr/share/rabbitmq"


#---------------------Services-------------------------------------------------
def run_server():
    local("python manage.py runserver")


def run_redis():
    with lcd("/tmp"):
        local("redis-server")


def run_rabbitmq():
    with lcd(RABITTMQ_HOME + "/sbin"):
        local("rabbitmq-server")


def start_worker():
    local("python manage.py celery worker")
