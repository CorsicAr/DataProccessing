import glob
import cv2

import pandas as pd
import pathlib

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from pyzbar.pyzbar import decode

import numpy as np
import cv2


def order_points(pts):
	# initialzie a list of coordinates that will be ordered
	# such that the first entry in the list is the top-left,
	# the second entry is the top-right, the third is the
	# bottom-right, and the fourth is the bottom-left
	rect = np.zeros((4, 2), dtype = "float32")
	# the top-left point will have the smallest sum, whereas
	# the bottom-right point will have the largest sum
	s = pts.sum(axis = 1)
	rect[0] = pts[np.argmin(s)]
	rect[2] = pts[np.argmax(s)]
	# now, compute the difference between the points, the
	# top-right point will have the smallest difference,
	# whereas the bottom-left will have the largest difference
	diff = np.diff(pts, axis = 1)
	rect[1] = pts[np.argmin(diff)]
	rect[3] = pts[np.argmax(diff)]
	# return the ordered coordinates
	return rect

def four_point_transform(image, pts):
	# obtain a consistent order of the points and unpack them
	# individually
	rect = order_points(pts)
	(tl, tr, br, bl) = rect
	# compute the width of the new image, which will be the
	# maximum distance between bottom-right and bottom-left
	# x-coordiates or the top-right and top-left x-coordinates
	widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
	widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
	maxWidth = max(int(widthA), int(widthB))
	# compute the height of the new image, which will be the
	# maximum distance between the top-right and bottom-right
	# y-coordinates or the top-left and bottom-left y-coordinates
	heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
	heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
	maxHeight = max(int(heightA), int(heightB))
	# now that we have the dimensions of the new image, construct
	# the set of destination points to obtain a "birds eye view",
	# (i.e. top-down view) of the image, again specifying points
	# in the top-left, top-right, bottom-right, and bottom-left
	# order
	dst = np.array([
		[0, 0],
		[maxWidth - 1, 0],
		[maxWidth - 1, maxHeight - 1],
		[0, maxHeight - 1]], dtype = "float32")
	# compute the perspective transform matrix and then apply it
	M = cv2.getPerspectiveTransform(rect, dst)
	warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
	# return the warped image
	return warped

def read_qr_code(img):

	qrs = decode(img)

	if len(qrs) == 0:
		print("No qrs found")
		return

	cntr_pos = central_pos(qrs)
	points = []
	# define Matplotlib figure and axis
	fig, ax = plt.subplots()

	for qr in qrs:
		i = central_poly(qr.polygon, cntr_pos)
		points.append(qr.polygon[i])

	points = np.array(points)

	# from now on you can use img as an image, but make sure you know what you are doing!

	#img = four_point_transform(img, points)
	data = Sheet_Data(qrs[0].data.decode(), points)

	return  data

def central_pos(QRs):

	cntr_pos = np.array([0,0])

	for qr in QRs:
		cntr_pos = np.add(cntr_pos,qr.polygon[0])

	cntr_pos = np.divide(cntr_pos,4)

	return  cntr_pos

def central_poly(polys, centre_pos):

	dist = 1000000000000000000000

	centre_pos = np.array(centre_pos)

	index = -1

	for i, point in enumerate(polys):

		point = np.array(point)

		this_dist = np.linalg.norm(point - centre_pos)

		if dist > this_dist:
			dist = this_dist
			index = i

	return index

class Sheet_Data:

	def __init__(self, data, points):
		data = data.split("; ")
		self.num_indxs = int(data[2])
		self.Indxs_list = data[1].split(',')
		self.indxs_str = data[1]
		self.num_symbols = len(self.Indxs_list)
		self.raw_data = data
		self.points = points
		self.points_x = points[:, :1]
		self.points_y = points[:, 1:]

