#!/usr/bin/python
# -*- coding: utf-8 -*-

""" A simple simulation that plots a single figure"""

import mreorg
import pylab
import numpy as np

x = np.linspace(0,100,num=500)
y = np.sin(x) * np.exp(-x* 0.05)

pylab.plot(x,y)

pylab.show()
