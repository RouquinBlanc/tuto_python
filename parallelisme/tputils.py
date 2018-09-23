import time

def chronometre(func, *args, **kwargs):
    """
    Execute une fonction et retourne le temps d'execution
    """
    start = time.time()
    res = func(*args, **kwargs)
    end = time.time()
    return end - start
