from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from time import sleep
from ui import client_app, dialog, dialog2

class SingleClient:
	"""
	This class describes the functionality of a single client.
	"""

	def __init__(self,PORT:int=12345):
		"""
		Constructs a new instance of the client.

		:param      PORT:  The port number to which thr connection request will be made while start-up.
		:type       PORT:  int
		"""
		self.PORT = PORT
		self.c_sock = socket(AF_INET, SOCK_STREAM)
		self.attempt = 0

	def reopen_socket(self)->None:
		"""
		This function is to close and re-open the socket of the self.
		"""
		self.c_sock.close()
		self.c_sock = socket(AF_INET,SOCK_STREAM)

	def recv_msg(self,c_sock:socket, ui:client_app)->None:
		"""
		Actively running function to receive the incomming message and to update the GUI as a separete thread.

		:param      c_sock:  The socket object of this client
		:type       c_sock:  socket
		:param      ui:      The user interface of this client
		:type       ui:      ui.client_app
		"""
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


	def start_client(self,wait:float|int=10):
		"""
		Starts a client by connecting to the server and runs the GUI of the client.

		:param      wait:  The waiting time of the client before re-connecting to the server.
		:type       wait:  float | int
		"""
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
				sleep(wait)
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