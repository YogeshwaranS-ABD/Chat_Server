from multiprocessing.shared_memory import ShareableList
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread

from loadbalancer import Balancer

class Threaded(Balancer):
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
		print("...> Client handled <...\n")



	def start_balancer(self):
		s = socket(AF_INET, SOCK_STREAM)
		s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s.bind(('localhost',12345))
		s. listen(10)

		self.start_servers()


		threads=[]
		while(1):
			try:
				print('===> waiting for new conncetion <===')
				c_sock, _= s.accept()
				t = Thread(target=self.handle_client,args=(c_sock,))
				t.start()
				print('Thread started\n')
			except:
				break


		
		self.stop_servers()

		for t in threads:
			t.join()

		s.close()
		self.shl.shm.close()
		self.shl.shm.unlink()


if __name__ == '__main__':
	shl = ShareableList(sequence=[0,0,0,0,0],name='client_stat')

	obj = Threaded(3,'least connection',shl)

	obj.start_balancer()

