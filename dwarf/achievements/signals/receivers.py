

def padawan_achievement(sender, **kwargs):
    print("Padawan achievement gained! {0}".format(sender.username))


def login_achievement(sender, **kwargs):
    print("Login achievement gained! {0}".format(sender.username))
