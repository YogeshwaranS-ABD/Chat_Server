# Chat_Server
 This is a chat server apllication made in python language.

-[] Writing the documentation.

This Repository has the server and client scripts and a Database file along with a class file for GUI. The database file is named as storage.db and has two tables named server and session.

The server script is imported into another script where the number of instances of the server is created.

Both server and client scripts are written assuming that the database already has the tables in the following schema.

### servers :
>	1. (Date: String)
>	2. (Name: String)
>	3. (Average_Rating: Float)
>	4. (Today_Count: Int)
>	5. (Monthly_Count: Int)
>	6. (Total_Approaches: Int)
>	7. (Lost_Count: Int) 


### session :
>	1. (Date : String)
>	2. (User : String)
>	3. (In_Time : String)
>	4. (Out_Time: String)


This repository has a database with empty tables in the above schema.

## main.py:
	The number of servers need to be started will be received from th e user as input.
	-shl: Shared memory object named client status, that was created to store the counting of clients, daily, monthly, total and the lost clients and the average rating of the service.
	-An object is created for MultipleServer with number of servers to be started, algorithm ('least connection', 'round robin') for balancing the clients among servers, and the approach to start the server either by 'fork' or by 'process' and the created shared memory object as arguments.
	-The load balancer is started calling obj.start_balancer().
	-Finally stop() is called to release the shared memory block and to delete those objects.




## Class s_server:
	args:
		1. mlock - A lock object from multiprocessing module to synchronize the actions of 3 servers, used as self.mp_lock
		2. ports - A list of port numbers on which the other servers and self are running
		3. shl 	 - A Shared Memory object of multiprocessing.shared_memory.SharableList() to share the details among the servers.

	Upon Construction the object can have following:
		1. self.lock - A lock aobject from threading module to syncronize the data transfer between the clients.
		2. self.mp_lock - as mentiond under args,1.
		3. self.date - The date on which the server started.
		4. self.port - The port number in which the server is listening and handling clients. Initially set to zero.
		5. self.name - Name of the specifed server in the format Server-1,2,3...
		6. self.clients - A list of client sockets, that are used in broadcasting the message.
		7. self.client_names - A cdictionary in which the all the client's ip address is set as key and their name is the value.
								{('127.0.0.1',54875),'client-name'}
		8. self.cl_in_time - A dictionary in which the values are stored as client_name:in_time as key-value pair
		9. self.addr - A list of all the running servers' ip addresses. created with the help of ports argument.
		10.self.shl - An object which is mapped to the schared memory block, through which no. of clients can be communicated among the servers.
		12.self.db - the object of dbHandle class from dbHandel.py to do all the dtabase related work like Select, Insert, Update.

	Member Methods:
		1. server(self,name:str, idx:int, shl_status:ShareableList) -> None
				name: Name of the server
				idx: index of the self.addr, through which the server instance has to serve the clients.
				shl_staus: A shareable list that has the client count stats
			When called, it creats a seperate socket and bind to the address value as in self.addr[idx] and makes it to listen. This function is also responsible to call the GUI on the main thread through gui.app.mainloop(). The client accepting part was handled by a seperate thread using the accept_client([args]) function.

		2. accept_clients(self,s_sock,gui, name, shl_status,idx) -> None
				s_sock: the socket object of the server.
				gui:	the GUI object, which is passed to handle_client([args]) method, which will use it to display the received msg from the server.
				name:	Name of the server, which will be sent to the client upon accpting a connection.
				shl_status: The shared memory block which, has the number of available connection a server can do. Like a semaphore, upon accepting a connection, it will be decremented. further passed to handle_client to increment if any client leaces the server.
				idx:	Index position of the server's adress in self.addr, which will be passed to handle_client() method.
			This function accepts a new connection and creates a new thread to handle each clients. If the connection is from port 5000, then the msg is received at the instance and send to other servers. Else, the counts are incremented accordingly and a cl_thread is created with function handle_client and started. Countings like today's clients count, monthly, total and lost clients are incremented upon respective events. The count incrementation are all done on the shared memory block by acquring and releasing the mp_lock.

		3. handle_client(self,c_sock, gui,shl_status,idx) -> None
				c_sock: Socket object of the client that needs to be served.
				gui: 	GUI object of the server, which is used to display the incomming message from each client.
				shl_status: An object of the shared memory block. It has the number of available connection of each server.
