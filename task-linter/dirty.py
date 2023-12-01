'Import module'
import random
import numpy as np

DEFAULT_ACCURACY = 3


def sum_two_values(first, second):
    """function print sum of two"""
    return first + second


def div(x, y, accuracy):
    """function print del x/y"""
    return round(x/y,  accuracy)



def get_rand():
    """function return of random"""
    return random.randint(1, 10)

def rand_array():
    """function random massive"""
    a = [get_rand(), get_rand(), get_rand()]
    return np.array(a)

def main():
    """main?"""
    print(rand_array())


main()
