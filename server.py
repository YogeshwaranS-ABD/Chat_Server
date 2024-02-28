from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from socket import AF_INET, SOCK_STREAM
from threading import Thread, Lock
import os
from datetime import datetime as dt
import sqlite3 as sql
from ui import server_app

class s_server:
	def __init__(self,mlock,ports)->None:
		self.lock = Lock()
		self.mp_lock = mlock
		self.date = f"{dt.now().strftime('%d %b %y')}"
		self.time = f"{dt.now().strftime('%I:%M:%S %p')}"
		self.port = 0
		self.name = ''
		self.monthly_clients=0
		self.today_clients=0
		self.total_clients_reached=0
		self.lost = 0
		self.avg_rating =  0
		self.clients = []
		self.client_names={}
		self.current_client='None'
		self.count=0
		self.addr = [('localhost',i) for i in ports]
		self.conn = sql.connect('storage.db')

	def query_handler(self,operation='SELECT',table='server',value=None):
		with self.lock:
			cursor =  self.conn.cursor()
			if operation=='SELECT':
				q = f"{operation} * FROM {table};"
				cursor.execute(q)
				return cursor.fetchall()
			elif operation=='INSERT' and value!=None:
				q = f"INSERT INTO {table} VALUES {value};"
				cursor.execute(q)
				self.conn.commit()
			elif operation =='UPDATE' and value!=None:
				q = f"UPDATE {table} SET \
						Average_Rating = {self.update_rating(value[0]):.2f},\
						Today_Count = {self.today_clients},\
						Monthly_Count = {self.monthly_clients},\
						Total_Approaches = {self.total_clients_reached},\
						Lost_Count = {self.lost} WHERE Date = '{self.date}';"
				cursor.execute(q)
				self.conn.commit()
			cursor.close()

	def retrive(self):
		data = self.query_handler()
		if data[-1][0]!=self.date:
			self.query_handler('INSERT','server',(self.date,self.name,data[-1][2],self.today_clients,data[-1][4],data[-1][5],data[-1][6]))
			self.avg_rating = data[-1][2]
			self.monthly_clients = data[-1][4]
			self.total_clients_reached = data[-1][5]
			self.lost = data[-1][6]
		else:
			self.avg_rating = data[-1][2]
			self.today_clients = data[-1][3]
			self.monthly_clients = data[-1][4]
			self.total_clients_reached = data[-1][5]
			self.lost = data[-1][6]

	def session_details(self,conn):
		with self.lock:
			cursor = conn.cursor()
			cursor.execute("SELECT * FROM session;")
			data = cursor.fetchall()
			cursor.close()
			return data

	def add_session(self,conn,values:tuple):
		with self.lock:
			cursor = conn.cursor()
			cursor.execute(f"INSERT INTO session VALUES {values}")
			cursor.close()
			conn.commit()

	def update_exit_time(self,conn:sql.Connection, c_name:str):
		with self.lock:
			cursor = conn.cursor()
			cursor.execute(f"UPDATE session SET Out_Time = '{dt.now().strftime('%I:%M:%S %p')}' WHERE User='{c_name}' AND Date = '{self.date}';")
			cursor.close()
			conn.commit()

	def update_rating(self,rate):
		if self.avg_rating == 0:
			self.avg_rating = rate
		else:
			self.avg_rating = (self.avg_rating*(self.monthly_clients-1)+rate)/self.monthly_clients
		return self.avg_rating


	def send_to_servers(self,msg):
		with self.mp_lock:
			for i in self.addr:
				if i[1]!=self.port:
					sock = socket(AF_INET,SOCK_STREAM)
					sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
					sock.bind(('localhost',5000))
					sock.connect(i)
					sock.sendall(msg.encode())


	def send_msg(self,gui, message, s_sock, rate, conn):
		if rate:
			self.current_client = self.client_names[s_sock.getpeername()]
			# s_sock.sendall("Server A : Rate this server from 1.0 to 5.0 ".encode())
			rating = message.split()[-1]
			gui.msg_post(f"{dt.now().strftime('%d %b %y - %I:%M:%S %p ->')} {self.current_client} exited the server")
			self.send_to_servers(f"{self.current_client} exited the server")
			self.update_rating(float(rating.split()[-1].strip()))
			self.update_exit_time(conn, self.current_client)
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
		if len(self.clients)!=0:
			gui.update_stat([self.avg_rating, self.today_clients,self.monthly_clients,self.lost, self.total_clients_reached, self.current_client])
		else:
			gui.update_stat([self.avg_rating, self.today_clients,self.monthly_clients, self.lost, self.total_clients_reached, "None"])


	def handle_client(self,c_sock, gui):
		conn2 = sql.connect('storage.db')
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
					self.add_session(conn2,value)
				if 'stop' in message:
					self.send_msg(gui,message, c_sock, True,conn2)
					# c_sock.sendall('Connection Closed EOC'.encode())
					with self.lock:
						self.clients.remove(c_sock)
					c_sock.close()
					break
				else:
					self.send_msg(gui,message, c_sock, False,conn2)
					self.send_to_servers(message)
			except (ConnectionResetError,BrokenPipeError,OSError) as e:
				print(os.getpid(),e)
				with self.lock:
					self.clients.remove(c_sock)
				c_sock.close()
				break

	
	def accept_clients(self,s_sock,gui, name):
		while True:
			c_sock, c_addr = s_sock.accept()
			
			if c_addr[1]!=1234:
				c_sock.close()

			elif c_addr[1] != 5000 and c_addr[1]!=1234:
				c_sock.sendall(name.encode())
				self.total_clients_reached+=1
				if len(self.clients) == 3: #3 is for number of clients per server
					c_sock.sendall('Server busy, try after 5 mins!'.encode())
					self.lost+=1
					c_sock.close()
					
				else:
					with self.lock:
						self.monthly_clients+=1
						self.today_clients+=1
						self.clients.append(c_sock)
					cl_thread = Thread(target=self.handle_client, args=(c_sock,gui))
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




	def server(self,name, idx):
		self.name = name
		self.port = self.addr[idx][1]
		self.retrive()
		s_sock = socket(AF_INET,SOCK_STREAM)
		s_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
		s_sock.bind(self.addr[idx])
		s_sock.listen(1)

		print(s_sock, os.getpid())

		gui = server_app(self.name,self.avg_rating,[self.today_clients,self.monthly_clients, self.lost, self.total_clients_reached], self.current_client)

		accept_thread = Thread(target=self.accept_clients, args=(s_sock,gui, name),daemon = True)
		accept_thread.start()

		gui.app.mainloop()

		self.query_handler(operation='UPDATE',table='server',value=(self.avg_rating,self.today_clients,self.monthly_clients,self.total_clients_reached,self.lost))
		self.retrive()

		self.conn.close()
		s_sock.close()


# s = s_server()

# s.server('server-1',0)