def get_string_from_file(path):
    with open(path, 'rb') as f:
        return f.read()
