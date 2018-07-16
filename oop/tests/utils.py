from functools import wraps


def cases(items):
    def decorator(f):
        @wraps(f)
        def wrapper(*args):
            for item in items:
                new_args = args + (item if isinstance(item, tuple) else (item,))
                try:
                    f(*new_args)
                except AssertionError as e:
                    raise AssertionError(e.args + (f'case: {new_args}',))
        return wrapper
    return decorator