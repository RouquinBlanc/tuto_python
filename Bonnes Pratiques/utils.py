"""
Module annexe de TP
"""

def premier(x):
    """
    Prédicat indiquant si un nombre est premier
    :param x: Nombre entier positif
    :returns: True si l'entier `x` est premier, False sinon
    """
    if x < 2:
        return False
    
    for y in range(2, x):
        if (x % y) == 0:
            return False
        
    return True
