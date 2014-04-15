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

import network

#net = network.Network(distribution='normal', M=1, resampling_steps=5)
#net.step_until(20)

#net = network.Network(distribution='normal', M=50, resampling_steps=5)
#net.step_until(20)

#net = network.Network(graph_basetype='grid2d:5x5', distribution='normal', consensus_step='single', M=2, resampling_steps=2000)
#net.step_until(20)

#net = network.Network(distribution='uniform', M=1, resampling_steps=5)
#net.step_until(20)

#net = network.Network(graph_basetype='grid2d:5x5', distribution='uniform', consensus_step='single', M=100, resampling_steps=10)
#net.step_until(100)

#net = network.Network(distribution='exponential', M=1, resampling_steps=5)
#net.step_until(20)

#net = network.Network(distribution='exponential', M=50, resampling_steps=5)
#net.step_until(20)

#net = network.Network(distribution='bernoulli', M=1, resampling_steps=5)
#net.step_until(20)

#net = network.Network(distribution='bernoulli', M=50, resampling_steps=5)
#net.step_until(20)

net = network.Network(graph_basetype='grid2d:19', distribution='bernoulli', consensus_step='single', M=5, resampling_steps=0)
net.step_until(2000)


