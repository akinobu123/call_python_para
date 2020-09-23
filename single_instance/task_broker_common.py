import posix_ipc
import subprocess
import psutil

# send message to queue
def send(queue, cmd, params):
	params_str = ','.join(params)
	queue.send(cmd + ':' + params_str)

# receive message from queue (message .... 'cmd:param1,param2,param3...')
def recv(queue):
	msg = queue.receive()
	msg_str = msg[0].decode('utf-8')
	splitted_str = msg_str.split(':')
	cmd_str = splitted_str[0]
	params_str = []
	if len(splitted_str) > 1:
		params_str = splitted_str[1].split(',')
	return (cmd_str, params_str)

# clear messages on queue
def clear(queue):
	while queue.current_messages > 0:
		str = recv(queue)

# create queues between the task and the broker
def make_queues(task_name, is_clear=False):
	q_name_b2t = '/broker_to_' + task_name
	q_name_t2b = '/' + task_name + '_to_broker'
	q_b2t = posix_ipc.MessageQueue(q_name_b2t, posix_ipc.O_CREAT)
	q_t2b = posix_ipc.MessageQueue(q_name_t2b, posix_ipc.O_CREAT)
	if is_clear:
		clear(q_b2t)
		clear(q_t2b)
	return (q_b2t, q_t2b)

# task-name ... ex) "remove-stamp" "cleansing-fax"
def worker_file_name(task_name):
	return task_name + '_worker.py'

def worker_name(task_name):
	return task_name + '_worker'

# check if python program is running
def is_running(python_program_name):
	ls = []
	for p in psutil.process_iter(['cmdline']):
		tmp = p.info['cmdline']
		if len(tmp) >= 2 and tmp[0] == 'python' and tmp[1] == (python_program_name):
			return True
	return False

# execute the task if dont running task
def make_taskworker_standby(task_name):
	if not is_running(worker_file_name(task_name)):
		subprocess.Popen(['python', worker_file_name(task_name)])

# task_main_loop
def task_main_loop(task_name, exec_task_func):
	q = make_queues(task_name)      # (q_b2t, q_t2b)
	SEND = 1
	RECV = 0

	while(True):
		msg = recv(q[RECV])
		CMD = 0
		PARAMS = 1
		if msg[CMD] == 'execute':
			print('    ' + worker_name(task_name) + ' ' + msg[1])
			ret = exec_task_func(msg[PARAMS])
			if not ret:
				print('     ' + worker_name(task_name) + ' ERROR')
			send(q[SEND], 'completed', [])
		elif msg[CMD] == 'quit':
			break

	print('    ' + worker_name(task_name) + ' quited.')
	send(q[SEND], 'completed', [])

