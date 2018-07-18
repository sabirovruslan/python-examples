from functools import wraps


def cases(items):
    def decorator(f):
        @wraps(f)
        def wrapper(self, *args):
            for item in items:
                new_args = args + (item if isinstance(item, tuple) else (item,))
                with self.subTest(f'case: {new_args}'):
                    f(self, *new_args)

        return wrapper

    return decorator
