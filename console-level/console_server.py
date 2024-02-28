from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from threading import Thread, Lock
from time import sleep
from datetime import datetime as dt
import sqlite3 as sql
PORT=5000

lock = Lock()

monthly_clients=0
today_clients=0
total_clients_reached=0
lost = 0
avg_rating =  0
name = 'Server A'
date = f"{dt.now().strftime('%d %b %y')}"
time = f"{dt.now().strftime('%I:%M:%S %p')}"

clients = []
client_names={}
current_client=None


conn=sql.connect('storage.db')


def query_handler(operation='SELECT',table='server',value=None):
	global conn, date
	with lock:
		cursor =  conn.cursor()
		if operation=='SELECT':
			q = f'{operation} * FROM {table};'
			cursor.execute(q)
			return cursor.fetchall()
		elif operation=='INSERT' and value!=None:
			q = f"INSERT INTO {table} VALUES {value};"
			cursor.execute(q)
			conn.commit()
		elif operation =='UPDATE' and value!=None:
			q = f"UPDATE {table} SET \
					Average_Rating = {update_rating(value[0]):.2f},\
					Today_Count = {today_clients},\
					Monthly_Count = {monthly_clients},\
					Total_Approaches = {total_clients_reached},\
					Lost_Count = {lost} WHERE Date = '{date}';"
			cursor.execute(q)
			conn.commit()
		cursor.close()
	

def retrive():
	global name, avg_rating, lost, monthly_clients, total_clients_reached, today_clients
	data = query_handler()
	if data[-1][0]!=date:
		query_handler('INSERT','server',(date,name,data[-1][2],today_clients,data[-1][4],data[-1][5],data[-1][6]))
	else:
		avg_rating = data[-1][2]
		today_clients = data[-1][3]
		monthly_clients = data[-1][4]
		total_clients_reached = data[-1][5]
		lost = data[-1][6]

def session_details(conn):
	global lock
	with lock:
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM session;")
		data = cursor.fetchall()
		cursor.close()
		return data

def add_session(conn,values:tuple):
	global lock
	with lock:
		cursor = conn.cursor()
		cursor.execute(f"INSERT INTO session VALUES {values}")
		cursor.close()
		conn.commit()

def update_exit_time(conn, name:str):
	global lock
	with lock:
		cursor = conn.cursor()
		cursor.execute(f"UPDATE session SET Out_Time = '{dt.now().strftime('%I:%M:%S %p')}' WHERE User='{name}' AND Date = '{date}';")
		cursor.close()
		conn.commit()

def update_rating(rate):
	global avg_rating, monthly_clients
	if avg_rating == 0:
		avg_rating = rate
	else:
		avg_rating = (avg_rating*(monthly_clients-1)+rate)/monthly_clients
	return avg_rating


def display_stat():
	global clients,lost
	trigger='stat'
	while True:
		if trigger==None:
			trigger = input()
		if trigger in ['stop','close','quit','exit', 'finish']:
			print('Closing Server....')
			sleep(1)
			print('server closed')
			break
		if trigger == 'stat':
			trigger = None
			time = f"{dt.now().strftime('%I:%M:%S %p')}"
			print(f"\
					Name : Server A\n\
					Date : {date}\n\
					Time : {time}\n\
					Average Rating : {avg_rating:.2f}\n\
					Clients Count : \n\
						\tToday : {today_clients}\n\
						\tThis Month : {monthly_clients}\n\
						\tTotal Approaches : {total_clients_reached}\n\
						\tClients Lost : {lost}\n\
					Current Client : {current_client}")


def send_msg(message, s_sock, rate, conn):
	global clients, lock, current_client

	if rate:
		current_client = client_names[s_sock.getpeername()]
		# s_sock.sendall("Server A : Rate this server from 1.0 to 5.0 ".encode())
		rating = message.split()[-1]
		print(dt.now().strftime('%d %b %y - %I:%M:%S %p ->'),current_client,'exited the server')
		update_rating(float(rating.split()[-1].strip()))
		update_exit_time(conn, current_client)
	else:
		print(dt.now().strftime('%d %b %y - %I:%M:%S %p ->'),message)
		with lock:
			for c_sock in clients:
				# current_client = client_names[c_sock.getpeername()]
				# print(f'message sent to - {c_sock.getpeername()}')
				try:
					c_sock.sendall(message.encode())
				except (ConnectionResetError, BrokenPipeError, OSError):
					clients.remove(c_sock)
					c_sock.close()


def handle_client(c_sock):
	global clients, lock, current_client
	conn2 = sql.connect('storage.db')
	while True:
		try:
			data = c_sock.recv(1024)
			if not data:
				break
			message = data.decode()
			if 'joined the server' in message:
				c_name = message.split()[0]
				client_names[c_sock.getpeername()] = c_name
				current_client = c_name
				value = (date, c_name, f"{dt.now().strftime('%I:%M:%S %p')}", 0)
				add_session(conn2,value)
			if 'stop' in message:
				send_msg(message, c_sock, True,conn2)
				# c_sock.sendall('Connection Closed EOC'.encode())
				with lock:
					clients.remove(c_sock)
				c_sock.close()
				break
			else:
				send_msg(message, c_sock, False,conn2)
		except ConnectionResetError:
			break
	# with lock:
	# 	clients.remove(c_sock)
	# c_sock.close()

def accept_clients(s_sock):
	global monthly_clients, total_clients_reached, clients, lock, lost, today_clients, current_client
	while True:
			c_sock, c_addr = s_sock.accept()
			c_sock.sendall(name.encode())
			total_clients_reached+=1
			if len(clients) == 3:
				c_sock.sendall('Server busy, try after 5 mins!'.encode())
				lost+=1
				c_sock.close()
				# break
			
			else:
				with lock:
					monthly_clients+=1
					today_clients+=1
					clients.append(c_sock)
				# print(f'{c_addr} added')
				cl_thread = Thread(target=handle_client, args=(c_sock,))
				cl_thread.start()

if __name__ == '__main__':
	retrive()
	s_sock = socket(AF_INET, SOCK_STREAM)
	s_sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	s_sock.bind(('localhost', PORT))
	s_sock.listen(1)
	print(dt.now().strftime('%d %b %y - %I:%M:%S %p ->'),"Chat server started.")

	accept_thread = Thread(target=accept_clients, args=(s_sock,),daemon = True)
	accept_thread.start()

	stat = Thread(target=display_stat)
	stat.start()
	stat.join()
	s_sock.close()
	query_handler(operation='UPDATE',table='server',value=(avg_rating,today_clients,monthly_clients,total_clients_reached,lost))
	retrive()
	conn.close()