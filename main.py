from multiprocessing.shared_memory import ShareableList
from loadbalancer import MultipleServer


def stop(shl,obj):
	shl.shm.close()
	shl.shm.unlink()
	del(obj,shl)
	exit(1)


if __name__ == '__main__':
	n = int(input('Enter the number of Servers : '))

	shl = ShareableList(sequence=[0,0,0,0,0],name='client_stat')

	obj = MultipleServer(n,'least connection','process',shl)
	# 'fork' and be chaned to 'process' to use multiprocessing.Process to create funnction
	# Here I used os.fork() system call to create a child process

	obj.start_balancer()

	stop(shl,obj)



