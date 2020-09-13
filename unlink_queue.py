import posix_ipc
import task_broker_common as tb

queue = posix_ipc.MessageQueue('/aaa_to_broker', 0)
queue.unlink()
queue = posix_ipc.MessageQueue('/broker_to_aaa', 0)
queue.unlink()
queue = posix_ipc.MessageQueue('/broker_to_aaa:0', 0)
queue.unlink()
queue = posix_ipc.MessageQueue('/broker_to_aaa:1', 0)
queue.unlink()

