# Copyright (c) 2011 Riccardo Lucchese, riccardo.lucchese at gmail.com
#
# This software is provided 'as-is', without any express or implied
# warranty. In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
#    1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
#
#    2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
#
#    3. This notice may not be removed or altered from any source
#    distribution.

import numpy
from fractions import Fraction

def random_vector_bernoulli_use_fractions(n, p):
    rv = numpy.random.binomial(1, p, n)

    fraction_array = []
    for num in rv:
        fraction_array.append(Fraction(num,1))
    
    return numpy.array(fraction_array)

def random_vector_bernoulli(n, p):
    return numpy.random.binomial(1, p, n)


