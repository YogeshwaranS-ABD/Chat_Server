from multiprocessing.shared_memory import SharedMemory
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from multiprocessing import Process, Lock
from server import s_server as SERVER
import os

class MultipleServer:
	
	def __init__(self,n:int, algorithm:str, approach:str) -> None:
		self.algorithm = algorithm.lower()
		self.ports = [x for x in range(5010,5010+n)]
		self.count=0
		self.processes = []
		self.number = n
		self.mp_lock = Lock()
		self.approach = approach
		# self.mm = shared_list
		# self.sm = SharedMemory(name='status',create=True,size=n)
		# sl = ShareableList([0 for i in range(n)],name='status')

	def start_servers(self,serve):
		for i in range(self.number):
			p = Process(target=serve.server, args=(f"Server-{i+1}",i))
			p.start()
			self.processes.append(p)

	def fork_server(self,serve):
		for i in range(self.number):
			pid = os.fork()
			if pid==0:
				serve.server(f"Server-{i+1}",i)
				self.processes.append(os.getppid)

	def stop_servers(self):
		for i in range(self.number):
			self.processes[i].join()

	def round_robin(self):
		if self.count==self.number:
			self.count=0
		addr = ('localhost',self.ports[self.count])
		self.count+=1
		return addr

	# def close_sm(self):
	# 	self.sm.close()

	# 	self.sm.unlink()


	def least_connection(self):
		with self.mp_lock:
			temp_sl = SharedMemory(name='status',create=False)
			for i in range(self.number):
				if temp_sl.buf[i]!=1:
					temp_sl.buf[i]=1
					temp_sl.close()
					temp_sl.unlink()
					return ('localhost',self.ports[i])

		# sock = socket(AF_INET,SOCK_STREAM)
		# sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		# sock.bind(('localhost',1234))
		# sock.settimeout(0.050)
		# for i in range(3):
		# 	if not sock.connect_ex(('localhost',self.ports[i])):
		# 		return ('localhost',self.ports[i])
		# sock.close()


	def start_balancer(self):	

		s = socket(AF_INET, SOCK_STREAM)
		s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s.bind(('localhost',12345))
		s. listen(3)

		serve = SERVER(self.mp_lock,self.ports, self.mm)

		if self.approach=='process':
			self.start_servers(serve)
		elif self.approach=='fork':
			self.fork_server(serve)
		else:
			raise ValueError('Invalid Approach method passed as argument')

		addr=''
		while True:
			try:
				print('waiting for new conncetion\n')
				c_sock, c_addr = s.accept()

				if self.algorithm == 'round robin':
					addr = self.round_robin()
				# elif self.algorithm in ['least connection','free server']:
				# 	addr = self.least_connection()

				if addr=='':
					c_sock.sendall('SNA wait'.encode())
				else:
					c_sock.sendall(str(addr).encode())

				print(addr, ' given to' ,c_sock.getpeername(),'\n')
				# print(list(self.sm.buf))
				c_sock.close()
			except Exception as e:
				print(e)
				break

		if self.approach=='process':
			self.stop_servers()

if __name__ == '__main__':
	n = int(input('Enter the number of Servers : '))

	mm = ''#Manager()
	# shared_list = mm.list([0,0,0,0,0])
	# 'fork' and be chaned to 'process' to use multiprocessing.Process to create funnction
	# Here I used os.fork() system call to create achild process
	obj = MultipleServer(n,'round robin','fork',mm)
	obj.start_balancer()
	


