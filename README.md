# Chat_Server
 This is a chat server apllication made in python language.

- [ ] Writing the documentation.

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
> ***Note:*** In this application, PORT number 5000 is reserved for communication between servers. PORT number 12345 is for the load balancer, to which the clients request to connect.

## main.py:
The number of servers need to be started will be received from th e user as input.
1. shl: Shared memory object named client status, that was created to store the counting of clients, daily, monthly, total and the lost clients and the average rating of the service.
2. An object is created for MultipleServer with number of servers to be started, algorithm ('least connection', 'round robin') for balancing the clients among servers, and the approach to start the server either by 'fork' or by 'process' and the created shared memory object as arguments.
3. The load balancer is started calling obj.start_balancer().
4. Finally stop() is called to release the shared memory block and to delete those objects.


## loadbalancer.py
### class MultipleServer
>args:
1. _n_ : Integer: Number of servers need to be started.
2. _algorithm_ : String: Either 'least connection' or 'round robin'
3. _approach_ : String: Either 'fork' or 'process'
4. _shl_ : ShareableList: A shared memory object to store the counts of clients.

>Upon Construction the object can have following:
1. _self.algorithm_ : stores the value of the argument _algorithm_
2. _slef.approach_ : A variable to store the value of _approach_ argument.
3. _self.shl_ : A object for the argument _shl_
4. _self.ports_ : A list of available port number. These are created upon construction. It will have _n_ number of ports created starting from 5010.
5. _self.count_ : A count variable used in round robin approach
6. _self.processes_ : A list of processes object if the approach was process.
7. _self.mp_lock_ : A object of multiprocessing.Lock() class.
8. _self.db_ : An object of the class dbHandle from dbHandler.py
9. _self.servers_sem_ : A ShareableList Object to be used to track the max number of clients of a server. The server will no longer accept a connection if it's corresponding value is zero. This is only applicable if _algorithm='least connection'_.

>**_Member Methods:_**
1. **Approach based methods**
	* *start_server(self, serve) -> None* if *self.approach* is *'process'*
	* *fork_server(self, serve) -> None* if *self.approach* is *'fork'*
2. **Approach based methods**
	* *round_robin(self) -> tuple* returns the address of the servers in a circular fashion
	* *lest_connection(self,shl_status:ShareableList) -> tuple* returns the address of the who has the least number of connected clients.

3. **start_balancer(self) -> None:**
	* When called, it will create a new socket and bind it to a port number **_12345_**, to which all the clients will request to connect.
	* An object is created for the class **_s_server_** with name **_SERVER_** with the variable named **_serve_** by passing _self.mp_lock, self.ports, self.shl_ as arguments.
	* With respect to *self.approach*, the serve object is passed to either ***fork_server()*** or ***start_server()***.
	* Once the servers are started, wait for the clients to connect. Upon accepting the client get the adddress of the available server based on the _self.algorithm_ by callling _self.round_robin_ or _self.least_connection_.
	* Send the address to the client if the _addr_ variable not an empty string, else send 'SNA wait' as in server not available, wait. finally close the client socket, and return to wait for the new connection.


## server.py:
###		Class s_server:
>args:
1. _mlock_ - A lock object from multiprocessing module to synchronize the actions of 3 servers, used as self.mp_lock
2. *ports* - A list of port numbers on which the other servers and self are running
3. *shl*	 - A Shared Memory object of multiprocessing.shared_memory.SharableList() to share the details among the servers.

>Upon Construction the object can have following:
1. _self.lock_ - A lock aobject from threading module to syncronize the data transfer between the clients.
2. _self.mp_lock_ - as mentiond under args,1.
3. _self.date_ - The date on which the server started.
4. _self.port_ - The port number in which the server is listening and handling clients. Initially set to zero.
5. _self.name_ - Name of the specifed server in the format Server-1,2,3...
6. _self.clients_ - A list of client sockets, that are used in broadcasting the message.
7. _self.client_names_ - A cdictionary in which the all the client's ip address is set as key and their name is the value.					{('127.0.0.1',54875),'client-name'}
8. _self.cl_in_time_ - A dictionary in which the values are stored as client_name:in_time as key-value pair
9. _self.addr_ - A list of all the running servers' ip addresses. created with the help of ports argument.
10. _self.shl_ - An object which is mapped to the schared memory block, through which no. of clients can be communicated among the servers.
12. _self.db_ - the object of dbHandle class from dbHandel.py to do all the dtabase related work like Select, Insert, Update.

>**_Member Methods:_**
1. **server(self,name:str, idx:int, shl_status:ShareableList) -> None**
	* _name_: Name of the server
	* _idx_: index of the self.addr, through which the server instance has to serve the clients.
	* _shl_staus_: A shareable list that has the client count stats
		* When called, it creats a seperate socket and bind to the address value as in self.addr[idx] and makes it to listen. This function is also responsible to call the GUI on the main thread through gui.app.mainloop(). The client accepting part was handled by a seperate thread using the accept_client([args]) function.

2. **accept_clients(self,s_sock,gui, name, shl_status,idx) -> None**
   * _s_sock_: the socket object of the server.
   * _gui_:	the GUI object, which is passed to handle_client([args]) method, which will use it to display the received msg from the server.
   * _name_:	Name of the server, which will be sent to the client upon accpting a connection.
   * _shl_status_: The shared memory block which, has the number of available connection a server can do. Like a semaphore, upon accepting a connection, it will be decremented. further passed to handle_client to increment if any client leaces the server.
   * _idx_:	Index position of the server's adress in self.addr, which will be passed to handle_client() method.
   		* This function accepts a new connection and creates a new thread to handle each clients. If the connection is from port 5000, then the msg is received at the instance and send to other servers. Else, the counts are incremented accordingly and a cl_thread is created with function handle_client and started. Countings like today's clients count, monthly, total and lost clients are incremented upon respective events. The count incrementation are all done on the shared memory block by acquring and releasing the mp_lock.

3. **handle_client(self,c_sock, gui,shl_status,idx) -> None**
   *  _c_sock_: Socket object of the client that needs to be served.
   *  _gui_: 	GUI object of the server, which is used to display the incomming message from each client.
   *  _shl_status_: An object of the shared memory block. It has the number of available connection of each server.
   		* This thread receives the message from the client and calls *self.send_msg(), self.send_to_servers()* to send the message to all the clients and the other servers respectively.
   		* This thread also calls the _stat_updater()_ function to update the details in the GUI upon arrival and departure of each client.
   		* This thread adds the user details to the session table in the database storage.db . When 'stop' is received, the respective client socket is removed from the _self.clients_ list. finally the available connection count of this server is incremented in the shared memory.

4. **send_msg(self, gui, message, s_sock, rate)->None:**
	* _gui_ : GUI object, used to display the log in the GUI.
	* _message_ : The message that needs to be sent to the other clients as well as other servers.
	* _s_sock_ : socket object of the sender client. This is passed as an argument to update the current client field in the GUI.
	* _rate_ : A boolean to determine if the client wants to exit.
		* If so, then the message contains the rating they given, with this, the average rating of the server is calculated and to be updated in the GUI.
		* This function is also responsible for updating the exit time of the client in the database after they have given the rating, if not given, then their exit time will be 0.

5. **send_to_servers(self,msg)->None:**
	* _msg_ : The message string that was received from the client and needs to be transmitted to other parallel servers
		* When called the message was sent to all the other servers through the reserved port ***5000***.

6. **stat_updater(self, gui)->None:**
	* _gui_ : GUI objet in which the values are updated.
		* when called, it calls gui.update_stat() with the values to be updated as arguments.

## dbHandler.py

### class dbHandle
>args:
1. _mlock_ : Object of multiprocessing.Lock() class to syncronize the database handling among the servers
2. _shared_list_ : A ShareableList object that stores the client count details.

>Upon Construction the object can have following:
1. _self.mp_lock_ : which stores the reference of the _mlock_ argument.
2. _self.shl_ : To store the reference to the shared memory block of the argument _shared_list_.
3. _self.date_ : Today's date.

>**_Member Methods:_**
1. **update_rating(self, rate) -> float:**
	* _rate_ : rating given by the leaving client. 
		* This function was called by the *send_msg()* function from the s_server class object when a client is about to leave. The passed argument is used to calculate the average rating and then the new value is stored in the shared memory object.
2. **query_handler(self, operation='SELECT', table='server', value=None):**
	* _operation_ : SELECT / INSERT / UPDATE.
	* _table_ : name of the table from/to which the data if fetched/updated respectively.
	* _value_ : Values to be updated/inserted in the database. Defaults to None, if the _operation_ is other than SELECT, then values need to be passed.
		* Based on the argument _operation_ the corresponding actions are carried out with the database.
		* When called with no arguments, this function returns the list of values from the table server.
3. **retrive(self, name='Master') -> list | None:**
	* _name_ : Name of the server that inserts the data into the databse.
		* When called, it calls the _query_handler()_ function without passing any arguments to fetch the data from the databse. If an empty list is returned, then inserts a new row of records.
		* Else, from the returned list, picks up the latest record and assign the values like total clients reached, lost clients, and monthly clients to the shared memory.
		* This function will be called by the load balancer on startup to setup the values in the newly created shared memory.
4. **update_exit_time(self, c_name:str, cl_in_time:dict) -> None:**
	* _c_name_ : Name of the client, who is leaving.
	* _cl_in_time_ : A dictionary with clinet name as key and their entry time as its corresponding value
		* when called, it will update the exit time of the client in the session table.
5. **add_session(self, values:tuple, cl_in_time:dict) -> None:**
	* _values_ : new record of the new client, that need to be inserted in the database.
	* _cl_in_time_ : A dictionary with clinet name as key and their entry time as its corresponding value.
		* when called it inserts a new record for the newly connected client.

## client.py
### class SingleClient

* args: None
>Upon Construction the object can have following:
1. _self.PORT_ : port number of the load balncer to which the client need to connect. It dafaults to 12345.
2. _self.c_sock_ : A new socket is created
3. _self.attempt_ : A integer, in which the no. of times the client attempted to connect to the server.

>**_Member Methods:_**
 1. **reopen_socket(self)->None:**
 	* When called, the object's socket is closed and then reopen for new connection attempt.
2. **recv_msg(self, c_sock:socket, ui:client_app) -> None:**
 	* _c_sock_ : A socket object of the client (self).
 	* _ui_ : An object for the GUI.
 		* This method was called as a new thread from the _start_client_ method.
 		* When created as a new thread, it waits to receive the mesage from the server and updates the GUI with that message by calling _ui.send_msg_ method from _client_app_ class in ui.py
 		* When the socket is closed, this thread will be terminated.
3. **start_client(self)->None:**
	* _wait_ : Float or int value in seconds, need to wait before retrying. It defaults to 10s.
	* When this function is called, the client UI is started and the connection attempt to the server is made.
	* Upon succesful connection, it receives the address of one of the servers that are running. Then the _self.c_sock_ is closed and re-opened to connect to the new address. Then the server name is received and the GUI is started.
	* Upon failed connection, i.e if the string 'SNA wait' is received, and the self.attempt is 1, the program exits. else if the self.attempt is 0, then it will be incremented to one and then retry to connect after 10 seconds.

## ui.py
* This file has the GUI components of the server and client.
> **class server_app**
* this class contains the GUI components of the single server application, which will be used in _s_server_ class
* Constructor of this class need to be passed with the details, that needs to be displayed on the GUI.
	* _s_name_ : Name of the server.
	* _rating_ : Average Rating of the server
	* _count_ : A list that has number of clients on today, monthly, total approached and lost.
	* _current_client_ : Name of the current client, defaults to None.

> **class client_app**
* args:
	* _c_sock_ : socket object of the client
	* _server_name_ : Name of the server, the client is connected with.
* This class contains the GUI components of the client application.
* The message typed in the text field is sent to the server through the c_sock socket object and the same is also updated in the GUI. this functionality is provided by the member method named _**send_msg()**_.
* Upon clicking the finish button a feedback Dialogue box appears to get the rating for the server. This functionality is provided by the member method **_feedbk(self)_**

> The other classe **class dialog2** will open a dialogu box upon failed connection attempt before retrying.