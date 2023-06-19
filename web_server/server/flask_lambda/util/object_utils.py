def get_nested(o, default, *args):
    if o is None:
        return default
    current = o
    for arg in args:
        if current is None or arg is None or current.get(arg, None) is None:
            return default
        current = current.get(arg, default)
    return current
