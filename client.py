from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from ui import client_app, dialog, dialog2

class SingleClient:
	def __init__(self):
		self.PORT = 12345
		self.c_sock = socket(AF_INET, SOCK_STREAM)
		self.attempt = 0

	def reopen_socket(self):
		self.c_sock.close()
		self.c_sock = socket(AF_INET,SOCK_STREAM)

	def recv_msg(self,c_sock, ui):
		while True:
			try:
				msg = c_sock.recv(1024).decode()
				if not msg:
					break
				else:
					ui.send_msg(msg,1)
			except:
				c_sock.close()
				break


	def start_client(self):
		try:
			self.c_sock.connect(('localhost',self.PORT))
			serve_addr = self.c_sock.recv(1024)
			if serve_addr == b'SNA wait':
				if self.attempt == 1:
					print('The connection is lost...')
					exit(1)
				gui = dialog2()
				self.attempt+=1
				print("Retrying in 10s")
				sleep(10)
				self.reopen_socket()
				self.start_client()
			else:
				serve_addr = eval(serve_addr)
			
			self.reopen_socket()
			self.c_sock.connect(serve_addr)

			server_name = self.c_sock.recv(1024).decode()

			gui = client_app(self.c_sock,server_name)

			receive_thread = Thread(target=self.recv_msg, args=(self.c_sock, gui), daemon=True)
			receive_thread.start()

			gui.login()
		except:
			gui = dialog()


if __name__ == '__main__':
	SingleClient().start_client()