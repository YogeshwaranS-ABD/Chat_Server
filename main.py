from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from multiprocessing import Process, Lock
from server import s_server as SERVER

class MultipleServer:
	
	def __init__(self,n:int, algorithm:str) -> None:
		self.algorithm = algorithm.lower()
		self.count=0
		self.processes = []
		self.number = n
		self.ports = [x for x in range(5010,5010+n)]

	def start_servers(self,serve):
		for i in range(self.number):
			p = Process(target=serve.server, args=(f"Server-{i+1}",i))
			p.start()
			self.processes.append(p)

	def stop_servers(self):
		for i in range(self.number):
			self.processes[i].join()

	def round_robin(self):
		if self.count==self.number:
			self.count=0
		addr = ('localhost',self.ports[self.count])
		self.count+=1
		return addr


	def least_connection(self):
		sock = socket(AF_INET,SOCK_STREAM)
		sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		sock.bind(('localhost',1234))
		sock.settimeout(0.050)
		for i in range(3):
			if not sock.connect_ex(('localhost',self.ports[i])):
				return ('localhost',self.ports[i])
		sock.close()


	def start_balancer(self):	

		s = socket(AF_INET, SOCK_STREAM)
		s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s.bind(('localhost',12345))
		s. listen(3)

		mp_lock = Lock()
		serve = SERVER(mp_lock,self.ports)

		self.start_servers(serve)

		addr=''
		while True:
			try:
				print('\nwaiting for new conncetion')
				c_sock, c_addr = s.accept()

				if self.algorithm == 'round robin':
					addr = self.round_robin()
				elif self.algorithm in ['least connection','free server']:
					addr = self.least_connection()

				if addr=='':
					c_sock.sendall('SNA wait'.encode())
				else:
					c_sock.sendall(str(addr).encode())

				print(addr, ' given to' ,c_sock.getpeername(),'\n')
				c_sock.close()
			except:
				break

		self.stop_servers()


if __name__ == '__main__':
	n = int(input('Enter the number of Servers : '))
	MultipleServer(n,'least connection').start_balancer()
