#! /usr/bin/env python3
'''
    File name: approaching_pose.py
    Author: Francisco Melo
    Mail: francisco.raposo.melo@tecnico.ulisboa.pt
    Date created: X/XX/XXXX
    Date last modified: X/XX/XXXX
    Python Version: 3.7
'''

import math

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from ellipse import plot_ellipse

import numpy as np

# Appeoachinf area radius increment in m
R_STEP = 0.01

# Thresold
THRESHOLD = 0
        # 127 -> cost -> definitely not in collision
        # http://wiki.ros.org/costmap_2d/hydro/inflation

def get_angle(pos1, pos2):
    "Angle between two points"
    return math.atan2(pos1[1] - pos2[1], pos1[0] - pos2[0])


def approaching_area_filtering(approaching_area, costmap):
    """ Filters the approaching area by checking the points inside personal or group space."""

    approaching_filter = []
    approaching_zones = []
    aux_list = []

    cnt = 0
    ox = costmap.info.origin.position.x
    oy = costmap.info.origin.position.y 
    resolution = costmap.info.resolution
    for x, y in zip(approaching_area[0], approaching_area[1]):
        
        ix = int((x - (resolution/2) - ox) / resolution)
        iy = int((y - (resolution/2) - oy) / resolution)
        index = iy * costmap.info.width + ix


        if costmap.data[index] <= THRESHOLD: 
            cnt += 1
        else:
            break

    if cnt != 0:
        px = approaching_area[0][0:cnt]
        py = approaching_area[1][0:cnt]

        x_area = []
        y_area = []

        c1 = approaching_area[0][cnt:]
        c2 = approaching_area[1][cnt:]

        x_area = np.concatenate([c1, px])
        y_area = np.concatenate([c2, py])
    else:
        x_area = approaching_area[0]
        y_area = approaching_area[1]

    for x, y in zip(x_area, y_area):
        ix = int((x - (resolution/2) - ox) / resolution)
        iy = int((y - (resolution/2) - oy) / resolution)
        index = iy * costmap.info.width + ix

        if costmap.data[index] <= THRESHOLD: #
            approaching_filter.append((x, y))
            aux_list.append((x, y))

        elif aux_list:
            approaching_zones.append(aux_list)
            aux_list = []

    if aux_list:
        approaching_zones.append(aux_list)

    return approaching_filter, approaching_zones


def approaching_heuristic(group_radius, pspace_radius, group_pos, approaching_filter, costmap, approaching_zones):
    """ """

    approaching_radius = group_radius
    approaching_radius += R_STEP
    if not approaching_filter:
        while not approaching_filter and approaching_radius <= pspace_radius:

            approaching_area = None
            approaching_filter = None
            approaching_zones = None

            approaching_area = plot_ellipse(
                semimaj=approaching_radius, semimin=approaching_radius, x_cent=group_pos[0], y_cent=group_pos[1], data_out=True)
            approaching_filter, approaching_zones = approaching_area_filtering(
                approaching_area, costmap)

            approaching_radius += R_STEP

    return approaching_filter, approaching_zones


def zones_center(approaching_zones, group_pos, group_radius):
    """ """
    # https://stackoverflow.com/questions/26951544/algorithm-find-the-midpoint-of-an-arc
    #https://stackoverflow.com/questions/11674239/find-arcs-mid-point-given-start-end-and-center-of-circle-points
    #https://stackoverflow.com/questions/26951544/algorithm-find-the-midpoint-of-an-arc
    center_x = []
    center_y = []
    orientation = []
    
    for zone in approaching_zones:
        if len(approaching_zones) != 1:
            # Sort points clockwise
            zone.sort(key=lambda c: math.atan2(c[0], c[1]))
     
        idx = int(len(zone) / 2)
        center_x.append(zone[idx][0])
        center_y.append(zone[idx][1])

        orientation.append(get_angle(group_pos, (zone[idx][0], zone[idx][1])))



    return center_x, center_y, orientation


