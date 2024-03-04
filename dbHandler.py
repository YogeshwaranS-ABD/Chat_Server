import sqlite3 as sql
from datetime import datetime as dt


class dbHandle:
	"""
	This class defines the functionalities related to the database handling.
	"""

	def __init__(self,mlock,shared_list)->None:
		"""
		Constructs a new instance of the database handler

		:param      mlock:        The lock object to synchronize the access to the database and the shared memory.
		:type       mlock:        multiprocessing.Lock
		:param      shared_list:  The shared list that stores the values from the database.
		:type       shared_list:  ShareableList
		"""
		self.mp_lock = mlock
		self.shl = shared_list
		self.date = f"{dt.now().strftime('%d %b %y')}"

	def update_rating(self,rate:float)->None:
		"""
		Updates the new average rating in the shared memory after the client given a feedback.

		:param      rate:  The rating given by a client
		:type       rate:  float
		"""
		with self.mp_lock:
			if self.shl[0] == 0:
				self.shl[0] = rate
			else:
				self.shl[0] = (self.shl[0]*(self.shl[2]-1)+rate)/self.shl[2]
			return self.shl[0]

	def query_handler(self,operation:str='SELECT',table:str='server',value=None) -> list | None:
		"""
		A function to handle the database queries like SELECT, UPDATE an dINSERT.

		:param      operation:  The operation to be performed
		:type       operation:  str
		:param      table:      The table on which the operation will be caried out
		:type       table:      str
		:param      value:      The tupe of record to be inserted at the end of the table.
		:type       value:      tuple | None

		:returns:   If SELECT is the operation returns the list of records of the table server, else None
		:rtype:     list | None
		"""
		conn = sql.connect('storage.db')
		cursor =  conn.cursor()
		if operation=='SELECT':
			with self.mp_lock:
				q = f"{operation} * FROM {table};"
				cursor.execute(q)
				return cursor.fetchall()
		elif operation=='INSERT' and value!=None:
			with self.mp_lock:
				q = f"INSERT INTO {table} VALUES {value};"
				cursor.execute(q)
				conn.commit()
		elif operation =='UPDATE' and value!=None:
			q = f"UPDATE {table} SET \
							Average_Rating = {self.update_rating(value[0]):.2f},\
							Today_Count = {self.shl[1]},\
							Monthly_Count = {self.shl[2]},\
							Total_Approaches = {self.shl[3]},\
							Lost_Count = {self.shl[4]} WHERE Date = '{self.date}';"
			with self.mp_lock:
				cursor.execute(q)
				conn.commit()
		cursor.close()
		conn.close()

	def retrive(self, name:str='Master'):
			"""
			A function to fetch the recent record and to store them in the ShareableList, if no record found it inserts a new with zeros

			:param      name:  The name of the server that want the data.
			:type       name:  str
			"""
			data = self.query_handler()
		# with self.mp_lock:
			if data==[]:
				self.query_handler('INSERT','server',(self.date,name,self.shl[0],self.shl[1],self.shl[2],self.shl[3],self.shl[4]))
			elif data[-1][0]!=self.date:
				self.query_handler('INSERT','server',(self.date,name,data[-1][2],self.shl[1],data[-1][4],data[-1][5],data[-1][6]))
				self.shl[0] = data[-1][2] #Avg. Rating
				self.shl[2] = data[-1][4] #Monthly_Count
				self.shl[3] = data[-1][5] #Total_Reached
				self.shl[4] = data[-1][6] #Lost_Count
			else:
				self.shl[0] = data[-1][2] #Avg. Ratin
				self.shl[1] = data[-1][3] #Today_Count
				self.shl[2] = data[-1][4] #Monthly_Co
				self.shl[3] = data[-1][5] #Total_Reac
				self.shl[4] = data[-1][6] #Lost_Count

	def update_exit_time(self,c_name:str,cl_in_time:dict):
		"""
		A function that updates the exit time of the client in the database.

		:param      c_name:      The name of the client leaving
		:type       c_name:      str
		:param      cl_in_time:  The dictionary that stores the in_time of the client respective to their name.
		:type       cl_in_time:  dict
		"""
		with self.mp_lock:
			conn = sql.connect('storage.db')
			cursor = conn.cursor()
			cursor.execute(f"UPDATE session SET Out_Time = '{dt.now().strftime('%I:%M:%S %p')}' WHERE User='{c_name}' AND Date = '{self.date}' AND In_Time = '{cl_in_time[c_name]}';")
			cursor.close()
			conn.commit()
			conn.close()

	def add_session(self,values:tuple,cl_in_time:dict):
		"""
		Adds a new record for the newly connected client in the session table.

		:param      values:      The values to be insterted into the table
		:type       values:      tuple
		:param      cl_in_time:  The dictionary that stores the in_time of the client respective to their name.
		:type       cl_in_time:  dict
		"""
		with self.mp_lock:
			cl_in_time[values[1]]=values[2]
			conn = sql.connect('storage.db')
			cursor = conn.cursor()
			cursor.execute(f"INSERT INTO session VALUES {values}")
			cursor.close()
			conn.commit()
			conn.close()

	def __del__(self):
		self.shl.shm.close()
		del(self.mp_lock,self.date, self.shl)
