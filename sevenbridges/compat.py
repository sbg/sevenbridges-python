try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError
