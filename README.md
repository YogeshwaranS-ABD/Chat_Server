# Chat_Server
 This is a chat server apllication made in python language.


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

Currently i'm working to make this code more reusable through modular concepts.
