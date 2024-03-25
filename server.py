from multiprocessing.shared_memory import ShareableList 
from threading import Lock
from datetime import datetime as dt

from dbHandler import dbHandle as db

class s_server:
	"""
	This class describes the functionality of the server.
	"""

	def __init__(self,mlock,ports:list,shl:ShareableList)->None:
		"""
		Constructs a new instance of the server

		:param      mlock:  The lock object to synchronize the access of the shared memory.
		:type       mlock:  multiprocessing.Lock
		:param      ports:  The ports
		:type       ports:  list
		:param      shl:    The shl
		:type       shl:    ShareableList
		"""
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
		self.count=0

	def send_to_servers(self,msg:str):
		"""
		Sends to servers.

		:param      msg:  The message
		:type       msg:  str
		"""
		pass


	def send_msg(self,gui, message:str, s_sock, rate:bool):
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
		pass

	def stat_updater(self,gui):
		"""
		Updates the statistic count of the clients in the GUI.

		:param      gui:  The graphical user interface
		:type       gui:  ui.server_app
		"""
		# self.query_handler(operation='UPDATE',table='server',value=(self.shl[0],self.today_clients,self.monthly_clients,self.total_clients_reached,self.lost))
		# self.retrive()
		pass


	def handle_client(self,c_sock, gui,shl_status:ShareableList,idx:int):
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
		pass

	
	def accept_clients(self,s_sock,gui, name:str, shl_status:ShareableList,idx:int):
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
		pass



	def serve(self,name:str, idx:int, shl_status:ShareableList):
		pass

	def __del__(self):
		"""
		Destructor of this class. deletes all the objects that are created using this class at the end to free the memory.
		"""
		self.shl.shm.close()
		del(self.date, self.clients, self.client_names, self.cl_in_time, self.mp_lock, 
			self.lock,self.current_client, self.shl, self.addr, self.port, self.name, self.db)


# s = s_server()
# s.server('server-1',0)