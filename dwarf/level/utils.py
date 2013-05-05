from level.models import Level


def incr_points(user, points):
    """Increments the points of an user, If the user has passed to a new level
    it returns the level, if not then  returns None"""
    points = user.profile.points + points

    level = Level.objects.get(points_min__lte=points, points_max__gte=points)

    # Has our user increase the level?
    if user.profile.level.level_number < level.level_number:
        user.profile.level = level
    else:
        level = None

    user.profile.points = points
    user.profile.save()

    return level


def decr_points(user, points):
    points = user.profile.points - points
    if points < 0:
        points = 0

    level = Level.objects.get(points_min__lte=points, points_max__gte=points)

    # Has our user decrease the level?
    if user.profile.level.level_number > level.level_number:
        user.profile.level = level
    else:
        level = None

    user.profile.points = points
    user.profile.save()

    return level


def points_for_next_level(user):
    points = user.profile.points
    next_level = Level.objects.get(
        level_number=(user.profile.level.level_number + 1))
    return (next_level.points_min - points)


def percent_for_next_level(user):
    pass
