import os
from multiprocessing import Process, Lock
from multiprocessing.shared_memory import ShareableList
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from server import s_server as SERVER
from dbHandler import dbHandle as db


class MultipleServer:
	"""
	This class describes the functionality of the load balancer.
	"""
	
	def __init__(self,n:int, algorithm:str, approach:str, shl:ShareableList) -> None:
		"""
		Constructs a new instance of the load balancer.

		:param      n:          Total number of servers to be created under the load balancer
		:type       n:          int
		:param      algorithm:  The algorithm to be used to split the clietns between the servers
		:type       algorithm:  str
		:param      approach:   The approach used to create those multiple servers
		:type       approach:   str
		:param      shl:        The sharable list that stores the values of the client statistics so far.
		:type       shl:        ShareableList
		"""
		self.algorithm = algorithm.lower()
		self.approach = approach
		self.number = n
		self.shl = shl
		self.ports = [x for x in range(5010,5010+n)]
		self.count=0
		self.processes = []
		self.mp_lock = Lock()	#this lock object will be shared between the servers to syncronize the writing in database
		self.db = db(self.mp_lock,self.shl)
		self.db.retrive()	# This is to fetch the data from the database and to put it in shared memory.
		self.servers_sem = ShareableList([1 for i in range(n)]) #replace 1 with the max no. of clients per server.

	def start_servers(self,serve:SERVER):
		"""
		Creates the server with multiprocessing.Process() as approach

		:param      serve:  The server object of the class s_server from server.py
		:type       serve:  server.s_server
		"""
		for i in range(self.number):
			p = Process(target=serve.server, args=(f"Server-{i+1}",i,self.servers_sem))
			p.start()
			self.processes.append(p)

	def fork_server(self,serve:SERVER):
		"""
		Creates the server with forking as approach

		:param      serve:  The server object of the class s_server from server.py
		:type       serve:  server.s_server
		"""
		try:
			for i in range(self.number):
				pid = os.fork()
				if pid==0:
					serve.server(f"Server-{i+1}",i,self.servers_sem)
		except:
			pass

	def stop_servers(self):
		"""
		Stops servers that are cerated using Process() call.
		"""
		for i in range(self.number):
			self.processes[i].join()

	def round_robin(self):
		"""
		Round robin algorithm to balance the load.
		"""
		if self.count==self.number:
			self.count=0
		addr = ('localhost',self.ports[self.count])
		self.count+=1
		return addr


	def least_connection(self,shl_status:ShareableList):
		"""
		The Least-Connection algorithm to balance the load.

		:param      shl_status:  The sharable list that stores the number of available connection to each server.
		:type       shl_status:  ShareableList
		"""
		temp_sl = ShareableList(name=shl_status.shm.name)
		with self.mp_lock:
			m = max(list(temp_sl))
		# print('-'*45,m)
		if m!=0:
			with self.mp_lock:
				i = temp_sl.index(m)
				temp_sl[i]-=1
			# print('='*10,temp_sl,'='*10)
			temp_sl.shm.close()
			return ('localhost',self.ports[i])
		else:
			with self.mp_lock:
				self.shl[4]+=1
		return ''


	def start_balancer(self):
		"""
		Starts the load balancer and binds it to the address localhost:12345
		"""	

		s = socket(AF_INET, SOCK_STREAM)
		s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s.bind(('localhost',12345))
		s. listen(3)

		serve = SERVER(self.mp_lock,self.ports, self.shl)

		if self.approach=='process':
			self.start_servers(serve)
		elif self.approach=='fork':
			self.fork_server(serve)
		else:
			raise ValueError('Invalid Approach method passed as argument')

		addr=''
		while True:
			try:
				print('===> waiting for new conncetion <===\n')
				c_sock, c_addr = s.accept()

				if self.algorithm == 'round robin':
					addr = self.round_robin()
				elif self.algorithm in ['least connection','free server']:
					addr = self.least_connection(self.servers_sem)

				if addr=='':
					c_sock.sendall('SNA wait'.encode())
				else:
					c_sock.sendall(str(addr).encode())

				# print(addr, ' given to' ,c_sock.getpeername(),'\n')
				# print(list(self.sm.buf))
				c_sock.close()
			except:
				break

		if self.approach=='process':
			self.stop_servers()

		s.close()
		del(serve)

	def __del__(self):
		self.shl.shm.close()
		self.servers_sem.shm.unlink()
		del(self.db,self.shl, self.servers_sem, self.ports, self.algorithm, self.count, self.processes,
			self.number, self.mp_lock, self.approach)