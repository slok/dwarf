import django.dispatch


############## User events #################

# Triggered when the user signs up
user_signup = django.dispatch.Signal()

# Triggered when the user logs in
user_login = django.dispatch.Signal()

############## Short link events #################
# Triggered when the link is shortened
link_shortened = django.dispatch.Signal()

# Triggered whe a link is clicked
link_clicked = django.dispatch.Signal()
