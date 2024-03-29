from tkinter import END, Button, Entry, Frame, Message, Tk, Label, Toplevel
from tkinter.scrolledtext import ScrolledText
from datetime import datetime as dt

date = f"{dt.now().strftime('%d %b %y')}"
time = f"{dt.now().strftime('%I:%M:%S %p')}"


class client_app:
	"""
	This class describes the GUI components and their functions of a client application.
	"""

	def __init__(self,c_sock,server_name:str) -> None:
		"""
		Constructs a new instance of thr client GUI.

		:param      c_sock:       The socket object of this client
		:type       c_sock:       socket
		:param      server_name:  The server name, to which this client was connected
		:type       server_name:  str
		"""
		self.c_sock=c_sock
		self.server_name = server_name
		self.app = Tk()
		self.app.withdraw()
		# self.serv_lbl = Label(self.app, text = server_name)
		self.app.geometry('750x500')
		self.app.resizable(False,False)
		self.frame1 = Frame(self.app, width=500)
		self.frame2 = Frame(self.app)
		self.greet = Message(self.app, text="Successfully connected to the server..", width=500, justify='left')
		self.msg_field = ScrolledText(self.frame1, bg='#333333', fg='white', state='disabled')
		self.msg_field.grid(row=0,column=0,sticky='ew')
		self.send_button = Button(self.frame2, text="SEND", command=self.send_msg)
		self.finish_button = Button(self.frame2, text="FINISH", command=self.feedbk)
		self.text_box = Entry(self.frame2, width=50)
		self.time_lbl = Label(self.app, text = f"{time}", justify='center')
		self.name=''
		self.app1 = Toplevel()
		self.lbl = Label(self.app1, text="Please Enter your Name to login...")
		self.user = Entry(self.app1, width=30)
		self.connect_button = Button(self.app1, text='Login', command=self.msg_start)


	
	def update_time(self):
		"""
		THis function calls itself every one second to update the time inth GUI of this client
		"""
		self.time_lbl.config(text=f"{dt.now().strftime('%I:%M:%S %p')}")
		self.time_lbl.after(1000,self.update_time)
	
	def set_title(self, name:str, app:Tk):
		"""
		Sets the title of the client GUI window as the name of this client

		:param      name:  The name of this client
		:type       name:  str
		:param      app:   The GUI object of this client
		:type       app:   tkinter.Tk class object
		"""
		if name != '':
			app.title(name+' - Chat Window')

	def msg_start(self):
		"""
		Functionality of the login Button, that set's the title of the client GUI and starts the main GUI for the client to send and receive messages.
		"""
		self.name = self.user.get()
		self.set_title(self.name,self.app)
		self.app1.destroy()
		self.c_sock.sendall(f'{self.name} joined the server'.encode())
		self.msg_box()

	def login(self):
		"""
		GUI description of the position and size of the GUI and its components.
		"""
		self.app1.title('Login')
		self.app1.geometry('320x240')
		self.lbl.pack()
		self.lbl.focus()
		self.user.pack()
		self.user.focus()
		self.connect_button.pack()
		self.app1.mainloop()

	def msg_box(self):
		"""
		The functions that defines the position of the components and starts the main GUI of the client
		"""
		self.update_time()
		self.app.deiconify()
		self.greet.pack()
		self.greet.config(text=f"Server : {self.server_name}\t\t\tDate : {date}")
		self.time_lbl.pack()
		self.frame1.pack()
		self.frame2.pack(anchor='s')
		self.text_box.pack()
		self.send_button.pack(side='right')
		self.finish_button.pack(side='left')
		self.app.mainloop()

	def send_msg(self,r_msg:str='',rec:int=0):
		"""
		Functionality of the SEND button. Sends the message string in the text box to the conected server.
		Also updates the chat window.

		:param      r_msg:  The message typed in the text box
		:type       r_msg:  str
		:param      rec:    Receive flag, if 1:just updates the chat window, else if 0: updates the chat window, and send the message to the server.
		:type       rec:    int
		"""
		msg = self.text_box.get()
		self.msg_field.configure(state='normal')
		if r_msg!='':
			self.msg_field.insert(END, r_msg+'\n')
		elif rec==0:
			# self.msg_field.insert(END, msg+'\n')
			try:
				self.c_sock.sendall(f"{self.name} : {msg}".encode())
			except (BrokenPipeError, OSError):
				self.msg_field.insert(END, 'The Server closed the connection...\n')
		self.msg_field.configure(state='disabled')
		self.text_box.delete(0,END)

	def feedbk(self):
		"""
		This fuction defines the components of the feedback window, which will appear upon clinking the FINISH button.
		"""

		self.feedback = Toplevel()
		self.lbl_1 = Label(self.feedback, text="Please rate the server, before you exit..\n\nRate from 1 to 5.\nyou can enter float values..")
		self.rate = Entry(self.feedback, width=20, justify='center')
		self.btn_submit = Button(self.feedback, command=self.exit_all, text='Submit')

		self.feedback.title('Feedback')
		self.feedback.geometry('300x150')
		self.feedback.resizable(False,False)
		self.lbl_1.pack()
		self.rate.pack()
		self.rate.focus()
		self.btn_submit.pack()
		

	def exit_all(self):
		"""
		After getting the rating from the clietn, the rating is sent to the server, and all the GUI windows will be closed upon clicking submit button
		"""
		rate = self.rate.get()
		self.c_sock.sendall(f"stop {rate}".encode())
		self.feedback.destroy()
		self.app.destroy()

class dialog:
	"""
	This class describes a dialog that appears if there is no server active on the given address.
	"""
	def __init__(self) -> None:
		self.app = Tk()
		self.app.resizable(False, False)
		self.msg = Message(self.app,bg='#333333',fg='#ffffff',width=300,pady=10, justify='center', text="Sorry, The server hasn't started yet...\n\nTry after the server is up!\n\nThank you!")
		self.btn_close = Button(self.app, text='Close', command=self.close)

		self.app.geometry('300x150')
		self.app.title('!! Alert !!')
		self.app.configure(background='#333333')
		self.msg.pack()
		self.btn_close.pack()

		self.app.mainloop()

	def close(self):
		self.app.destroy()

class dialog2:
	"""
	This class describes a dialog box that tells to wait for some time, if the server is running but busy.
	"""
	def __init__(self) -> None:
		self.app = Tk()
		self.app.resizable(False, False)
		self.msg = Message(self.app,bg='#333333',fg='#ffffff',width=300,pady=10, justify='center', text="Sorry, All servers are busy...\n\nTry after 5 minutes!\n\nThank you!")
		self.btn_close = Button(self.app, text='Close', command=self.close)

		self.app.geometry('300x150')
		self.app.title('!! Alert !!')
		self.app.configure(background='#333333')
		self.msg.pack()
		self.btn_close.pack()

		self.app.mainloop()

	def close(self):
		self.app.destroy()

class server_app:
	"""
	This class describes the GUI components of a server application.
	"""
	def __init__(self, s_name:str,rating:float,count:list =[int,int,int,int], current_client='NONE') -> None:
		"""
		Constructs a new instance of the SERVER GUI.

		:param      s_name:          The name of this server
		:type       s_name:          str
		:param      rating:          The Average rating of the server, from the database.
		:type       rating:          float
		:param      count:           The count of the clients connected to the server so far.
		:type       count:           list
		:param      current_client:  The name of the current client of this server
		:type       current_client:  str
		"""
		self.rating = rating
		self.count = count
		self.stoped = False

		self.app = Tk()
		self.app.geometry('660x590')
		self.app.configure(background='#333333')
		self.app.title(s_name)
		# self.app.resizable(False,False)

		self.stat_frame = Frame(self.app,background='#333333')
		self.msg_c_name = Message(self.stat_frame,width=300, bg='#333333',fg='#ffffff', text=f'Current-Client : {current_client}', justify='center')
		self.msg_date = Message(self.stat_frame,width=300, bg='#333333',fg='#ffffff', text='Date : '+date, justify='left')
		self.msg_time = Message(self.stat_frame,width=300, bg='#333333',fg='#ffffff', text='Time : '+time, justify='left')
		self.msg_rating = Message(self.stat_frame,width=300, bg='#333333',fg='#ffffff', text=f'Avg. Rating : {rating}', justify='left')
		self.msg_today = Message(self.stat_frame,width=300, bg='#333333',fg='#ffffff', text=f"Today : {count[0]}", justify='left')
		self.msg_month = Message(self.stat_frame,width=300, bg='#333333',fg='#ffffff', text=f"This Month : {count[1]}", justify='left')
		self.msg_lost = Message(self.stat_frame,width=300, bg='#333333',fg='#ffffff', text=f"Lost Clients : {count[2]}", justify='left')
		self.msg_approach = Message(self.stat_frame,width=300, bg='#333333',fg='#ffffff', text=f"Total Clients Approached : {count[3]}", justify='center')
		self.btn_stop = Button(self.stat_frame,text='Stop', bg='#3b2523', fg='#f5e9d3', command=self.stop)

		self.log_frame = Frame(self.app,background='#333333')
		self.log = ScrolledText(self.log_frame,bg='#222222',fg='#f5e9d3', state='disabled', selectforeground='#333333', selectbackground='#f5e9d3')

		self.stat_frame.pack(fill='x',side='top',pady=10)
		self.stat_frame.columnconfigure(0,weight=325)
		self.stat_frame.columnconfigure(1,weight=325)

		#column left
		self.msg_date.grid(column=0,row=0)#,sticky='w')
		self.msg_time.grid(column=0,row=1)#,sticky='w')
		self.msg_rating.grid(column=0,row=2)#,sticky='w')
		self.msg_c_name.grid(column=0,row=3)#,sticky='w')
		#column right
		self.msg_today.grid(column=1,row=0)
		self.msg_month.grid(column=1,row=1)
		self.msg_lost.grid(column=1,row=2)
		self.msg_approach.grid(column=1,row=3)
		#Stop-Button
		self.btn_stop.grid(row=4,columnspan=2)

		self.log_frame.pack(fill='x',side='bottom',pady=10)
		self.log.grid(sticky='ew')
		self.update_time()
		self.msg_post(f"{dt.now().strftime('%d %b %y - %I:%M:%S %p ->')}Chat server started.")


	def update_time(self):
		"""
		Updates the time of the SERVER GUI for every second.
		"""
		self.msg_time.config(text=f"{dt.now().strftime('%I:%M:%S %p')}")
		self.msg_time.after(1000,self.update_time)

	def msg_post(self,msg:str):
		"""
		Inserts the received message in the mesage field.

		:param      msg:  The message received form the client or other server.
		:type       msg:  str
		"""
		self.log.configure(state='normal')
		self.log.insert(END,msg+'\n')
		self.log.configure(state='disabled')

	def stop(self):
		"""
		The functionality of the stop button to stop the server and close it's GUI window
		"""
		self.log.configure(state='normal')
		if not self.stoped:
			self.stoped = True
			self.log.insert(END,'Stoping the server...\n')
			self.log.insert(END, 'All clients are disconnected...\n')
			self.log.insert(END, 'Database disconnected after updating the values...\n')
			self.log.insert(END,'You can now close the server...\n')
		else:
			self.log.insert(END,'\n\n!!! The server is already stoped...\n\tYou can close it now !')
		self.log.configure(state='disabled')
		self.app.destroy()
		# self.app.destroy()

	def update_stat(self,count:list):
		"""
		A function that updates the each field of the statistics bar in the GUI

		:param      count:  The counnt of the clients connected so far.
		:type       count:  list
		"""
		self.msg_rating.config(text=f"Average Rating : {count[0]:.2f}")
		self.msg_today.config(text=f"Today : {count[1]}")
		self.msg_month.config(text=f"This Month : {count[2]}")
		self.msg_lost.config(text=f"Lost : {count[3]}")
		self.msg_approach.config(text=f"Total Clients Approached : {count[4]}")
		self.msg_c_name.config(text=f'Current-Client : {count[5]}')
