from multiprocessing.shared_memory import ShareableList
from loadbalancer import MultipleServer


def stop(shl:ShareableList,obj:MultipleServer):
	"""
	This function is to release the shared memory and delete the objects used.

	:param      shl:  The sharable list that was created with the name of 'client_stat'
	:type       shl:  ShareableList
	:param      obj:  The object of the loadbalancer class.
	:type       obj:  MultipleServer
	"""
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

	obj.start_balancer() #This fuction call will start the Load balancer block in loadbalancer.py

	stop(shl,obj) #At last, stop() function is called to close, release and delete the shared memory and the objects.



