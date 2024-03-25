from multiprocessing.shared_memory import ShareableList
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, timeout
from threading import Thread, get_ident

from loadbalancer import Balancer

class PreThread(Balancer):
	def __init__(self,n:int, algorithm:str, shl:ShareableList) -> None:
		super().__init__(n,algorithm,shl)

	def create_thread(self,s,i):
		t = Thread(target=self.handle_client,args=(s,))
		t.start()
		return t

	def handle_client(self,s):
		while True:
			try:
				print(f'{get_ident()}===> waiting for new conncetion <===\n')
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
				print(f"{get_ident()}...> Client handled <...\n")
			except:
				break

	def start_balancer(self):
		s = socket(AF_INET, SOCK_STREAM)
		s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s.bind(('localhost',12345))
		s. listen(10)

		self.start_servers()

		# pre-forking
		threads=[]
		for i in range(3):
			threads.append(self.create_thread(s,i))
		
		self.stop_servers()

		s.close()
		self.shl.shm.close()
		self.shl.shm.unlink()

		for i in range(3):
			threads[i].join()
			print(threads[i])

		

if __name__ == '__main__':
	shl = ShareableList(sequence=[0,0,0,0,0],name='client_stat')

	obj = PreThread(3,'least connection',shl)

	obj.start_balancer()

