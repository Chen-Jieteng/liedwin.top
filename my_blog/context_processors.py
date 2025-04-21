import time

def timestamp_processor(request):
    """
    Adds timestamp to the request context to prevent caching issues
    Especially useful for logout links to ensure they are never cached
    """
    return {
        'timestamp': int(time.time())
    } 