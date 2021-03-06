#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: main.py

import time
from nbgl import GLDrawer
import numpy as np
import threading
import sys
from time import sleep, time

def rand(min = 0.2, max = 1):
    from random import random
    return (max - min) * random() + min

class Sphere(object):
    def __init__(self, r, pos):
        self.radius = float(r)
        self.pos = [float(k) for k in pos]
        assert len(self.pos) == 3
        #self.color = [rand() for i in range(3)]
        self.color = [1,1,0]

class Cylinder(object):
    def __init__(self, p1, p2, r, col):
        self.p1 = np.asarray(p2, dtype='float32')
        self.p2 = np.asarray(p1, dtype='float32')
        self.r = float(r)
        self.color = col

class Frame(object):
    def __init__(self, sphlist, cyllist):
        self.sphlist = sphlist
        self.cyllist = cyllist

def build_cylinder_from_3dpts(pts):
    ret = []

    def f(id1, id2, thick, col=[0,0.5,0]):
        return Cylinder(pts[id1,:],pts[id2,:], thick, col)

    ret.append(f(0,1,3, [0.5,0.5,0]))
    ret.append(f(2,3,1, [0, 1, 1]))
    ret.append(f(3,4,1, [0,1,1]))
    ret.append(f(5,6,1, [1,0,1]))
    ret.append(f(6,7,1, [1,0,1]))
    ret.append(f(8,9,1))
    ret.append(f(9,10,1))
    ret.append(f(11,12,1))
    ret.append(f(12,13,1))
    return ret

def run_app(draw_cb, get_frame_func):
    """
    :param draw_cb: call back drawing function, taking a :class:`Frame`
    object and the time as float, return the whether the drawing loop should
    continue"""
    stop_flag = [False]
    time_delta = 0.04

    def draw_thread():
        prev = time()
        frcnt = 0
        tot_time = 0
        while True:
            cur = time()
            tot_time += time_delta
            if cur - prev > 1:
                print 'network fps=' + str(frcnt / (cur - prev))
                prev = cur
                frcnt = 0
            frcnt += 1
            if not draw_cb(get_frame_func(), tot_time):
                stop_flag[0] = True
                return
            sleep(time_delta)

    threading.Thread(target = draw_thread).start()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: {} <npy file with all 3d points>"
        sys.exit(1)
    B = 600.0
    drawer = GLDrawer('winname', [(-B,B)]*3)
    drawer.start()

    alldata = np.load(sys.argv[1])
    print "Shape:", alldata.shape
    cnt = 0
    def get_frame():
        global cnt
        cnt += 1
        step = cnt / 3
        print step % alldata.shape[0]
        data = alldata[step%alldata.shape[0]] * 100
        spheres = [Sphere(3, pos) for pos in data]
        spheres[0].radius = 10
        cyls = build_cylinder_from_3dpts(data)
        f = Frame(spheres, cyls)
        return f

    run_app(drawer.draw_callback, get_frame)
    sleep(100)
