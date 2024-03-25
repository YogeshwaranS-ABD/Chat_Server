from multiprocessing.shared_memory import ShareableList
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from loadbalancer import Balancer
from writer import write_log

class Iterative(Balancer):
	def __init__(self,n:int, algorithm:str, shl:ShareableList) -> None:
		super().__init__(n,algorithm,shl)
		self.c_count = 0

	def start_balancer(self):
		s = socket(AF_INET, SOCK_STREAM)
		s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s.bind(('localhost',12345))
		s. listen(3)

		self.start_servers()
		write_log('LB, Servers are started')

		addr=''
		while True:
			try:
				print('===> waiting for new conncetion <===\n')
				c_sock, c_addr = s.accept()
				write_log(f"LB, Connection received from : {c_addr}")

				if self.algorithm == 'round robin':
					addr = self.round_robin()
				elif self.algorithm == 'least connection':
					addr = self.least_connection(self.servers_sem)

				if addr=='':
					c_sock.sendall('SNA wait'.encode())
					write_log(f'LB, Connection not available for {c_addr}')

				else:
					c_sock.sendall(str(addr).encode())
					write_log(f'LB, sent {addr} to {c_addr} for connection')
					self.c_count+=1

				# print(addr, ' given to' ,c_sock.getpeername(),'\n')
				# print(list(self.sm.buf))
				c_sock.close()
				write_log(f"LB, connection closed witn {c_addr}")
			except:
				self.shl.shm.close()
				write_log(f"LB, {self.c_count} within the total elapesd time.e")
				break

		self.stop_servers()

		s.close()
		print('\nServer Closed')

	def __del__(self):
		super().__del__()
		write_log(f"LB, {self.c_count} within the total elapesd time")

if __name__ == '__main__':

	write_log("LB, Iterative Load Balancer Started")

	shl = ShareableList(sequence=[0,0,0,0,0],name='client_stat')

	obj = Iterative(3,'least connection',shl)

	obj.start_balancer()


	