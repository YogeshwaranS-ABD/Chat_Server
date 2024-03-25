from multiprocessing.shared_memory import ShareableList 
from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from socket import AF_INET, SOCK_STREAM
from threading import Thread
from datetime import datetime as dt

from ui import server_app
from server import s_server
from writer import write_log

class implement_server(s_server):
	def __init__(self,mlock,ports:list,shl:ShareableList) -> None:
		super().__init__(mlock,ports,shl)

	def send_to_servers(self,msg:str):
		"""
		Sends to servers.

		:param      msg:  The message
		:type       msg:  str
		"""
		with self.mp_lock:
			for i in self.addr:
				if i[1]!=self.port:
					sock = socket(AF_INET,SOCK_STREAM)
					sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
					sock.bind(('localhost',5000))
					sock.connect(i)
					sock.sendall(msg.encode())


	def send_msg(self,gui, message:str, s_sock:socket, rate:bool):
		"""
		Sends a message to other clients if the sending client is not rating the server.

		:param      gui:      The graphical user interface
		:type       gui:      ui.server_app
		:param      message:  The message
		:type       message:  str
		:param      s_sock:   The socket object of the client that send the message
		:type       s_sock:   socket
		:param      rate:     If the client wants to rate or not
		:type       rate:     bool
		"""
		if rate:
			self.current_client = self.client_names[s_sock.getpeername()]
			# s_sock.sendall("Server A : Rate this server from 1.0 to 5.0 ".encode())
			rating = message.split()[-1]
			gui.msg_post(f"{dt.now().strftime('%d %b %y - %I:%M:%S %p ->')} {self.current_client} exited the server")
			self.send_to_servers(f"{self.current_client} exited the server")
			self.db.update_rating(float(rating.split()[-1].strip()))
			gui.update_stat([self.shl[0], self.shl[1],self.shl[2],self.shl[4], self.shl[3], self.current_client])
			self.db.update_exit_time(self.current_client, self.cl_in_time)
			write_log(f'{self.name}, Client gave the rating of {rating} as feedback')
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
		"""
		Updates the statistic count of the clients in the GUI.

		:param      gui:  The graphical user interface
		:type       gui:  ui.server_app
		"""
		# self.query_handler(operation='UPDATE',table='server',value=(self.shl[0],self.today_clients,self.monthly_clients,self.total_clients_reached,self.lost))
		# self.retrive()
		if len(self.clients)!=0:
			gui.update_stat([self.shl[0], self.shl[1],self.shl[2],self.shl[4], self.shl[3], self.current_client])
		else:
			gui.update_stat([self.shl[0], self.shl[1],self.shl[2], self.shl[4], self.shl[3], "None"])


	def handle_client(self,c_sock:socket, gui,shl_status:ShareableList,idx:int):
		"""
		A function to handle a client, this function will be invoked in seperate threads for each client.

		:param      c_sock:      The c sock
		:type       c_sock:      socket
		:param      gui:         The graphical user interface
		:type       gui:         ui.server_app
		:param      shl_status:  The status of each server, that will be maintained in a sharable list.
		:type       shl_status:  ShareableList
		:param      idx:         The index position of the PORT number to get the address for binding
		:type       idx:         int
		"""
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
					write_log(f'{self.name},Connection accepted from client {c_name} and updated the databse and GUI')

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
					write_log(f'{self.name},Number of available connection was incremented.')
					break
				else:
					self.send_msg(gui,message, c_sock, False)
					self.send_to_servers(message)
			except (ConnectionResetError,BrokenPipeError,OSError) as e:
				# print(os.getpid(),e)
				with self.lock:
					self.clients.remove(c_sock)
				c_sock.close()
				break

	
	def accept_clients(self,s_sock:socket,gui, name:str, shl_status:ShareableList,idx:int):
		"""
		{ function_description }

		:param      s_sock:      The socket object of this server
		:type       s_sock:      socket
		:param      gui:         The graphical user interface
		:type       gui:         ui.server_app
		:param      name:        The name of this server
		:type       name:        str
		:param      shl_status:  The status of each server, that will be maintained in a sharable list.
		:type       shl_status:  ShareableList
		:param      idx:         The index position of the PORT number to get the address for binding
		:type       idx:         int
		"""
		while True:
			c_sock, c_addr = s_sock.accept()

			if c_addr[1] != 5000:
				c_sock.sendall(name.encode())
				with self.mp_lock:
					self.shl[3]+=1
				if len(self.clients) == 100: #_ is for number of clients per server
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
					self.count+=1

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




	def serve(self,name:str, idx:int, shl_status:ShareableList):
		"""
		A function to create a server with it's GUI and a seprate thread to accept the clients as they request to connect.

		:param      name:        The name of this server
		:type       name:        str
		:param      idx:         The status of each server, that will be maintained in a sharable list.
		:type       shl_status:  ShareableList
		:param      idx:         The index position of the PORT number to get the address for binding
		:type       idx:         int
		"""
		self.name = name
		self.port = self.addr[idx][1]

		s_sock = socket(AF_INET,SOCK_STREAM)
		s_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s_sock.bind(self.addr[idx])
		s_sock.listen(1)
		write_log(f'{self.name},Socket was created and binded to the address localhost:{self.port}.')

		# print(s_sock, os.getpid())

		gui = server_app(self.name,self.shl[0],[self.shl[1],self.shl[2], self.shl[4], self.shl[3]], self.current_client)

		accept_thread = Thread(target=self.accept_clients, args=(s_sock,gui, name, shl_status,idx),daemon = True)
		accept_thread.start()

		write_log(f'{self.name},GUI has started')
		gui.app.mainloop()

		self.db.query_handler(operation='UPDATE',table='server',value=(self.shl[0],self.shl[1],self.shl[2],self.shl[3],self.shl[4]))

		s_sock.close()

		write_log(f'{self.name}, The latest count values are updated in the database.')
		print(f"{self.name} Handled {self.count} clients")
