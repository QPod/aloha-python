from secrets import SystemRandom


def random_bool():
    return SystemRandom().choice([True, False])


def random_choice(*args):
    return SystemRandom().choice(*args)


def random_int(a, b):
    return SystemRandom().randint(a, b)


def random_ratio():
    return SystemRandom().random()


def random_uniform(*args):
    return SystemRandom().uniform(*args)


def random_sample(*args):
    return SystemRandom().sample(*args)
