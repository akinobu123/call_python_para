import posix_ipc
import subprocess
import psutil

# send message to queue
def send(queue, msg_str):
	queue.send(msg_str)

# receive message from queue (message .... 'cmd:param1,param2,param3...')
def recv(queue):
	msg = queue.receive()
	msg_str = msg[0].decode('utf-8')
	splitted_str = msg_str.split(':')
	cmd_str = splitted_str[0]
	param_str = ''
	if len(splitted_str) > 1:
		param_str = splitted_str[1]
	return (cmd_str, param_str)

# clear messages on queue
def clear(queue):
	while queue.current_messages > 0:
		str = recv(queue)

# create queues between the task and the broker
def make_queues(task_name, instance_id, is_clear=False):
	q_name_b2t = '/broker_to_' + task_name + ':' + str(instance_id)
	q_name_t2b = '/' + task_name + ':' + str(instance_id) + '_to_broker'
	q_b2t = posix_ipc.MessageQueue(q_name_b2t, posix_ipc.O_CREAT)
	q_t2b = posix_ipc.MessageQueue(q_name_t2b, posix_ipc.O_CREAT)
	if is_clear:
		clear(q_b2t)
		clear(q_t2b)
	return (q_b2t, q_t2b)

# task-name ... ex) "remove_stamp" "cleansing_fax"
def worker_file_name(task_name):
	return task_name + '_worker.py'

def worker_name(task_name, instance_id):
	return task_name + '_worker[' + str(instance_id) + ']'

# check if python program is running
def is_running(python_program_name, instance_id):
	ls = []
	for p in psutil.process_iter(['cmdline']):
		tmp = p.info['cmdline']
		if len(tmp) >= 4 and tmp[0] == 'python' and \
			tmp[1] == (python_program_name) and \
			tmp[2] == '--id' and \
			tmp[3] == str(instance_id):
			return True
	return False

# execute the task if dont running task
def make_taskworker_standby(task_name, instance_id):
	if not is_running(worker_file_name(task_name), instance_id):
		subprocess.Popen(['python', worker_file_name(task_name), \
			'--id', str(instance_id)])
# task_main_loop
def task_main_loop(task_name, instance_id, exec_task_func):
	q = make_queues(task_name, instance_id)      # (q_b2t, q_t2b)
	SEND = 1
	RECV = 0

	while(True):
		msg = recv(q[RECV])
		if msg[0] == 'execute':
			print('    ' + worker_name(task_name, instance_id) + ' ' + msg[1])
			params = msg[1].split(',')
			ret = exec_task_func(params)
			if not ret:
				print('     ' + worker_name(task_name, instance_id) + ' ERROR')
			send(q[SEND], 'completed')
		elif msg[0] == 'quit':
			break

	print('    ' + worker_name(task_name, instance_id) + ' quited.')
	send(q[SEND], 'completed')

