from functools import wraps

def force_debug_output(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        func(*args, **kwargs)
    return wrapped
