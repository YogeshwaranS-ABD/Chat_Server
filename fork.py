from multiprocessing.shared_memory import ShareableList
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os import fork, _exit, waitpid

from loadbalancer import Balancer

class Fork(Balancer):
	def __init__(self,n:int, algorithm:str, shl:ShareableList) -> None:
		super().__init__(n,algorithm,shl)

	def handle_client(self,c_sock):
		addr=''
		if self.algorithm == 'round robin':
			addr = self.round_robin()
		elif self.algorithm == 'least connection':
			addr = self.least_connection(self.servers_sem)

		if addr=='':
			c_sock.sendall('SNA wait'.encode())
		else:
			c_sock.sendall(str(addr).encode())

	def start_balancer(self):
		s = socket(AF_INET, SOCK_STREAM)
		s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s.bind(('localhost',12345))
		s. listen(10)

		self.start_servers()

		while True:
			try:
				print('===> waiting for new conncetion <===\n')
				c_sock, _= s.accept()

				pid = fork()
				if pid==0:
					self.handle_client(c_sock)
					print('child exiting\n')
					self.shl.shm.close()
					_exit(0)
					# _ = waitpid(0,0)
				else:
					c_sock.close()

			except:
				break

		s.close()
		exit(1)

if __name__ == '__main__':
	shl = ShareableList(sequence=[0,0,0,0,0],name='client_stat')

	obj = Fork(3,'least connection',shl)

	obj.start_balancer()