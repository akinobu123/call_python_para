import argparse
import task_broker_common as tb
import numpy as np
import cv2

parser = argparse.ArgumentParser()
parser.add_argument("--id", required=True, help="specify task instance id")
arg = parser.parse_args()


def exec_task(params):
	if len(params) < 2:
		return False

	img_in = cv2.imread(params[0])
	img_gray = cv2.cvtColor(img_in, cv2.COLOR_BGR2GRAY)
	ret, thresh = cv2.threshold(img_gray, 190, 255, cv2.THRESH_BINARY)
	contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
	img_out = cv2.drawContours(img_in, contours, -1, (0, 0, 255), 3)
	cv2.imwrite(params[1], img_out)

	return True


def main():
	tb.task_main_loop('draw_contour', arg.id, exec_task)

main()
