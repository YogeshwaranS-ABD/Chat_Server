from multiprocessing.shared_memory import ShareableList
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import fork, kill

from loadbalancer import Balancer

class PreFork(Balancer):
	def __init__(self,n:int, algorithm:str, shl:ShareableList) -> None:
		super().__init__(n,algorithm,shl)

	def create_child(self,s):
		pid = fork()
		if pid<0:
			print('Error')
			exit()
		elif pid>0:
			return pid
		self.handle_client(s)

	def handle_client(self,s):
		while(1):
			try:
				print("pre-fork\n")
				print('===> waiting for new conncetion <===\n')
				c_sock, _= s.accept()

				addr=''
				if self.algorithm == 'round robin':
					addr = self.round_robin()
				elif self.algorithm == 'least connection':
					addr = self.least_connection(self.servers_sem)

				if addr=='':
					c_sock.sendall('SNA wait'.encode())
				else:
					c_sock.sendall(str(addr).encode())
				print("...> Client handled <...\n")
			except:
				break

	def start_balancer(self):
		s = socket(AF_INET, SOCK_STREAM)
		s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s.bind(('localhost',12345))
		s. listen(10)

		self.start_servers()

		# pre-forking
		pids=[]
		for _ in range(10):
			pids.append(self.create_child(s))
		
		self.stop_servers()

		s.close()
		self.shl.shm.close()
		self.shl.shm.unlink()

		for i in range(10):
			kill(pids[i],15) #15 - interger value of signal SIGTERM. 9 also can be used as in SIGKILL


if __name__ == '__main__':
	shl = ShareableList(sequence=[0,0,0,0,0],name='client_stat')

	obj = PreFork(3,'least connection',shl)

	obj.start_balancer()

