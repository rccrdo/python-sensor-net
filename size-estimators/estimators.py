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
import fractions

def size_estimator_max_uniform(local_maxs, nr_samples):
    #print 'estim max uniform'
    assert isinstance(nr_samples, int) and nr_samples > 0

    return -float(nr_samples)/numpy.sum(numpy.log(local_maxs))


def size_estimator_min_exponential(local_maxs, nr_samples):
    #print 'estim max exponential'
    assert isinstance(nr_samples, int) and nr_samples > 0

    return float(nr_samples -1)/numpy.sum(local_maxs)
    
    
def size_estimator_avg_normal(local_avgs, nr_samples):
    #print 'estim avg normal'
    assert isinstance(nr_samples, int) and nr_samples > 0

    return float(nr_samples)/numpy.sum(local_avgs**2)


def size_estimator_avg_bernoulli(local_avg):
    #print 'estim avg bernoulli'
    def lcm(values):
        assert len(values) > 0

        if len(values) == 1:
            return values[0]
   
        lcm = (values[0]*values[1])/fractions.gcd(values[0],values[1])
        for v in values[2:]:
            lcm = (lcm*v)/fractions.gcd(lcm,v)
        return lcm

    den = []
    for frac in local_avg:
        den.append(int(frac.denominator))
    return lcm(den)
    

def size_estimator_avg_bernoulli2(local_avg):
    #print 'estim avg bernoulli'
    def lcm(values):
        assert len(values) > 0

        if len(values) == 1:
            return values[0]
   
        lcm = (values[0]*values[1])/fractions.gcd(values[0],values[1])
        for v in values[2:]:
            lcm = (lcm*v)/fractions.gcd(lcm,v)
        return lcm

    den = []
    for frac in local_avg:
        frac = frac.limit_denominator(5000)
        den.append(int(frac.denominator))
    return lcm(den)
    
def size_estimator_avg_bernoulli3(local_avg):
    #print 'estim avg bernoulli'
    def lcm(values):
        assert len(values) > 0

        if len(values) == 1:
            return values[0]
   
        lcm = (values[0]*values[1])/fractions.gcd(values[0],values[1])
        for v in values[2:]:
            lcm = (lcm*v)/fractions.gcd(lcm,v)
        return lcm

    den = []
 #   print local_avg
    for x in local_avg:
        assert isinstance(num, float)
        frac = fractions.Fraction(x).limit_denominator(5000)
        
        if abs(x -frac) >=( 1./(500.*499.)):
            return 0.

        den.append(int(frac.denominator))
    return lcm(den)



