import sqlite3 as sql
from datetime import datetime as dt


class dbHandle:

	def __init__(self,mlock,shared_list)->None:
		self.mp_lock = mlock
		self.shl = shared_list
		self.date = f"{dt.now().strftime('%d %b %y')}"

	def update_rating(self,rate):
		with self.mp_lock:
			if self.shl[0] == 0:
				self.shl[0] = rate
			else:
				self.shl[0] = (self.shl[0]*(self.shl[2]-1)+rate)/self.shl[2]
			return self.shl[0]

	def query_handler(self,operation='SELECT',table='server',value=None):
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

	def retrive(self, name='Master'):
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
		with self.mp_lock:
			conn = sql.connect('storage.db')
			cursor = conn.cursor()
			cursor.execute(f"UPDATE session SET Out_Time = '{dt.now().strftime('%I:%M:%S %p')}' WHERE User='{c_name}' AND Date = '{self.date}' AND In_Time = '{cl_in_time[c_name]}';")
			cursor.close()
			conn.commit()
			conn.close()

	def add_session(self,values:tuple,cl_in_time):
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
