import argparse
import task_broker_common as tb

parser = argparse.ArgumentParser()
parser.add_argument("--id", required=True, help="specify task instance id")
arg = parser.parse_args()


def exec_task(params):
	# dummy task
	tmp = 1
	for a in range(50000000):
		if a > 1:
			tmp = tmp * a + 1
			tmp = tmp / a
	print('    ' + str(tmp))

def main():
	tb.task_main_loop('aaa', arg.id, exec_task)

main()
