from multiprocessing.shared_memory import ShareableList 
from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Lock
import os
from datetime import datetime as dt

from dbHandler import dbHandle as db
from ui import server_app

class s_server:
	def __init__(self,mlock,ports,shl)->None:
		self.lock = Lock()	
		self.mp_lock = mlock
		self.date = f"{dt.now().strftime('%d %b %y')}"
		self.port = 0
		self.name = ''
		self.clients = []
		self.client_names={}
		self.current_client='None'
		self.cl_in_time = {}
		self.addr = [('localhost',i) for i in ports]
		self.shl = ShareableList(name=shl.shm.name)
		self.db = db(self.mp_lock,shl)

	def send_to_servers(self,msg):
		with self.mp_lock:
			for i in self.addr:
				if i[1]!=self.port:
					sock = socket(AF_INET,SOCK_STREAM)
					sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
					sock.bind(('localhost',5000))
					sock.connect(i)
					sock.sendall(msg.encode())


	def send_msg(self,gui, message, s_sock, rate):
		if rate:
			self.current_client = self.client_names[s_sock.getpeername()]
			# s_sock.sendall("Server A : Rate this server from 1.0 to 5.0 ".encode())
			rating = message.split()[-1]
			gui.msg_post(f"{dt.now().strftime('%d %b %y - %I:%M:%S %p ->')} {self.current_client} exited the server")
			self.send_to_servers(f"{self.current_client} exited the server")
			self.db.update_rating(float(rating.split()[-1].strip()))
			gui.update_stat([self.shl[0], self.shl[1],self.shl[2],self.shl[4], self.shl[3], self.current_client])
			self.db.update_exit_time(self.current_client, self.cl_in_time)
		else:
			gui.msg_post(f"{dt.now().strftime('%d %b %y - %I:%M:%S %p ->')} {message}")
			with self.lock:
				for c_sock in self.clients:
					try:
						c_sock.sendall(message.encode())
					except (ConnectionResetError, BrokenPipeError, OSError):
						self.clients.remove(c_sock)
						c_sock.close()

	def stat_updater(self,gui):
		# self.query_handler(operation='UPDATE',table='server',value=(self.shl[0],self.today_clients,self.monthly_clients,self.total_clients_reached,self.lost))
		# self.retrive()
		if len(self.clients)!=0:
			gui.update_stat([self.shl[0], self.shl[1],self.shl[2],self.shl[4], self.shl[3], self.current_client])
		else:
			gui.update_stat([self.shl[0], self.shl[1],self.shl[2], self.shl[4], self.shl[3], "None"])


	def handle_client(self,c_sock, gui,shl_status,idx):
		while True:
			try:
				data = c_sock.recv(1024)
				if not data:
					break
				message = data.decode()
				if 'joined the server' in message:
					c_name = message.split()[0]
					self.client_names[c_sock.getpeername()] = c_name
					self.current_client = c_name
					self.stat_updater(gui)
					value = (self.date, c_name, f"{dt.now().strftime('%I:%M:%S %p')}", 0)
					self.db.add_session(value,self.cl_in_time)
				if 'stop' in message:
					self.send_msg(gui,message, c_sock, True)
					# c_sock.sendall('Connection Closed EOC'.encode())
					with self.lock:
						self.clients.remove(c_sock)
					temp_sl = ShareableList(name=shl_status.shm.name)
					with self.mp_lock:
						temp_sl[idx]+=1
					# print('='*10,temp_sl,'='*10)
					temp_sl.shm.close()
					c_sock.close()
					break
				else:
					self.send_msg(gui,message, c_sock, False)
					self.send_to_servers(message)
			except (ConnectionResetError,BrokenPipeError,OSError) as e:
				print(os.getpid(),e)
				with self.lock:
					self.clients.remove(c_sock)
				c_sock.close()
				break

	
	def accept_clients(self,s_sock,gui, name, shl_status,idx):
		while True:
			c_sock, c_addr = s_sock.accept()

			if c_addr[1] != 5000:
				c_sock.sendall(name.encode())
				with self.mp_lock:
					self.shl[3]+=1
				if len(self.clients) == 2: #_ is for number of clients per server
					c_sock.sendall(' Server busy, try after 5 mins!'.encode())
					with self.mp_lock:
						self.shl[4]+=1
					c_sock.close()
					
				else:
					with self.mp_lock:
						self.shl[2]+=1
						self.shl[1]+=1
						self.clients.append(c_sock)
					cl_thread = Thread(target=self.handle_client, args=(c_sock,gui,shl_status,idx))
					cl_thread.start()

			else:
				msg = c_sock.recv(1024).decode()
				c_sock.close()
				gui.msg_post(f"{dt.now().strftime('%d %b %y - %I:%M:%S %p ->')} {msg}")
				with self.lock:
					for sock in self.clients:
						try:
							sock.sendall(msg.encode())
						except (ConnectionResetError, BrokenPipeError, OSError):
							self.clients.remove(sock)
							sock.close()




	def server(self,name:str, idx:int, shl_status:ShareableList):
		self.name = name
		self.port = self.addr[idx][1]

		s_sock = socket(AF_INET,SOCK_STREAM)
		s_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s_sock.bind(self.addr[idx])
		s_sock.listen(1)

		# print(s_sock, os.getpid())

		gui = server_app(self.name,self.shl[0],[self.shl[1],self.shl[2], self.shl[4], self.shl[3]], self.current_client)

		accept_thread = Thread(target=self.accept_clients, args=(s_sock,gui, name, shl_status,idx),daemon = True)
		accept_thread.start()

		gui.app.mainloop()

		self.db.query_handler(operation='UPDATE',table='server',value=(self.shl[0],self.shl[1],self.shl[2],self.shl[3],self.shl[4]))

		s_sock.close()

	def __del__(self):
		self.shl.shm.close()
		del(self.date, self.clients, self.client_names, self.cl_in_time, self.mp_lock, 
			self.lock,self.current_client, self.shl, self.addr, self.port, self.name, self.db)


# s = s_server()
# s.server('server-1',0)