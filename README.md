# Chat_Server
 This is a chat server apllication made in python language.


This Repository has the server and client scripts and a Database file along with a class file for GUI. The database file is named as storage.db and has two tables named server and session.

The server script is imported into another script where the number of instances of the server is created.

Both server and client scripts are written assuming that the database already has the tables in the following schema.

1. servers : {
			(Date: String)
			(Name: String)
			(Average_Rating: Float)
			(Today_Count: Int)
			(Monthly_Count: Int)
			(Total_Approaches: Int)
			(Lost_Count: Int) 
		}

2. session : {
			(Date : String)
			(User : String)
			(In_Time : String)
			(Out_Time: String)
		}

This repository has a database with empty tables in the above schema.

Currently i'm working to make this code more reusable through modular concepts.