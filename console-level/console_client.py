from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from datetime import datetime as dt

PORT=5000

date = f"{dt.now().strftime('%d %b %y')}"
time = f"{dt.now().strftime('%I:%M:%S %p')}"

# flag = True
def stat_display(c_sock,c_name):
	print(f"\
		Name : {c_name}\n\
		Date : {date}\n\
		Time : {time}\n\
		Server Name : {c_sock.getpeername()}")

def receive_messages(gui):
	while True:
		global c_sock
		try:
			data = c_sock.recv(1024)
			data = data.decode()
			if not data:
				break
			if data == 'Connection Closed':
				c_sock=0
				break
			elif 'EOC' in data:
				gui.send_msg(data[:len(data)-3])
				gui.send_msg('Connection Closed')
				gui.send_msg('Press Enter to Exit')
				c_sock=0
				break
			elif 'Server busy' in data:
				gui.send_msg(data)
				gui.send_msg('Waiting to Reconnect...')
				sleep(5)
				gui.send_msg('Connection Lost, Press Enter to Exit')
				c_sock.close()
				c_sock=0
				break
			print(data)
		except (ConnectionResetError,OSError):
			gui.send_msg('Connection Interuppted')
			break

def client(gui):

	global c_sock
	c_sock = socket(AF_INET, SOCK_STREAM)
	c_sock.connect(('localhost', PORT))
	print("Connected to server.")

	gui.login()
	c_name = gui.name

	c_sock.sendall((c_name+' joined the server').encode())

	receive_thread = Thread(target=receive_messages, args=(gui,))
	receive_thread.start()


	while True:
		try:
			message = gui.text_box.get()
			print(message)
			if message == 'stat':
				stat_display(c_sock, c_name)
				continue
			message = f'{c_name} : '+message

			#send message
			if c_sock!=0:
				c_sock.sendall(message.encode())
			elif c_sock==0:
				receive_thread.join()
				break

		except ConnectionResetError:
			c_sock.close()
			break
		except (BrokenPipeError, OSError):
			print('Server Closed the Connection')
			break
	
	# receive_thread.join()
	if c_sock!=0:
		c_sock.close()