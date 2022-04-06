from secrets import SystemRandom

random = SystemRandom()


def random_bool():
    return random.choice([True, False])


def random_choice(*args, **kwargs):
    return random.choice(*args, **kwargs)


def random_int(a, b):
    return random.randint(a, b)


def random_ratio():
    return random.random()


def random_uniform(*args):
    return random.uniform(*args)


def random_sample(*args):
    return random.sample(*args)


def random_seed(*args, **kwargs):
    return random.seed(*args, **kwargs)
