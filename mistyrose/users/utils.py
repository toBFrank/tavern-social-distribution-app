from urllib.parse import urlparse


def is_fqid(value):
    """
    Check if the value is an FQID (a URL) or a SERIAL (integer).
    """
    try:
        value_str = str(value)
        print (f"checking if {value} is a url")
        # Parse the value as a URL
        result = urlparse(value_str)
        print (f"result: {result}")
        print(f"result.scheme: {result.scheme}")
        print(f"result.netloc: {result.netloc}")
        return all([result.scheme, result.netloc])  # Valid URL requires scheme and netloc
    except ValueError as e:
        print(f"error: {e}")
        return False