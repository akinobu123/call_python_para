import argparse
import time
import task_broker_common as tb
import cv2
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--task_name', required=True, help='specify task name')
parser.add_argument('--task_param', default='', help='specify task param')
parser.add_argument('--mode', default='exec', choices=['exec', 'exec_para', 'quit'])
arg = parser.parse_args()

def split_image(in_path):
	in_img = cv2.imread(in_path)
	h, w = in_img.shape[:2]
	half_h = int(h/2)
	split_h = half_h - (half_h % 256)
	if split_h == 0:
		split_h = half_h
	img1 = in_img[0:split_h, 0:w]
	img2 = in_img[split_h:h, 0:w]
	path1 = in_path.replace('.', '_1.')
	path2 = in_path.replace('.', '_2.')
	cv2.imwrite(path1, img1)
	cv2.imwrite(path2, img2)
	return path1, path2

def marge_image(path1, path2, out_path):
	img1 = cv2.imread(path1)
	img2 = cv2.imread(path2)
	out_img = np.vstack((img1, img2))
	cv2.imwrite(out_path, out_img)

def main():
	start_time = time.time()
	print(" task_broker start")
	SEND = 0
	RECV = 1

	if arg.mode == 'exec':
		q0 = tb.make_queues(arg.task_name, 0, True)  # (q_b2t, q_t2b)
		tb.make_taskworker_standby(arg.task_name, 0)
		tb.send(q0[SEND], 'execute:' + arg.task_param)
		msg0 = tb.recv(q0[RECV])
		if msg0[0] != 'completed':
			print(' task  execute ERROR')

	if arg.mode == 'exec_para':   # task_param = 'input-img-filepath,output-img-filepath'
		# split to 2 images
		task_params = arg.task_param.split(',')
		if len(task_params) < 2:
			print(' task execute ERROR')
		in1, in2 = split_image(task_params[0])
		out1 = in1.replace('.', '_out.')
		out2 = in2.replace('.', '_out.')
		print(out1, out2)

		# execute paralell
		q0 = tb.make_queues(arg.task_name, 0, True)  # (q_b2t, q_t2b)
		q1 = tb.make_queues(arg.task_name, 1, True)  # (q_b2t, q_t2b)
		tb.make_taskworker_standby(arg.task_name, 0)
		tb.make_taskworker_standby(arg.task_name, 1)
		tb.send(q0[SEND], 'execute:' + in1 + ',' + out1)
		tb.send(q1[SEND], 'execute:' + in2 + ',' + out2)
		msg0 = tb.recv(q0[RECV])
		msg1 = tb.recv(q1[RECV])
		if msg0[0] != 'completed' or msg1[0] != 'completed':
			print(' task  execute ERROR')

		# marge 2 images
		marge_image(out1, out2, task_params[1])
		
	elif arg.mode == 'quit':
		instance_id = 0
		while tb.is_running(tb.worker_file_name(arg.task_name), instance_id):
			q = tb.make_queues(arg.task_name, instance_id, False)
			tb.send(q[SEND], 'quit')
			msg = tb.recv(q[RECV])
			if msg[0] != 'completed':
				print(' task  execute ERROR')
			q[SEND].unlink()
			q[RECV].unlink()
			instance_id += 1

	print(" task_broker end")
	end_time = time.time()
	print(" elapsed time: ", str(end_time - start_time))

main()
