# CZ4013DS

CZ4013 Project Tasks

design and implement a system for remote file access based on client-server architecture

files are stored on the local disk of the server

server implements sets of services for clients to remotely access files

client provides interface for users to invoke these services

on receiving req input from user, client sends req to server

server performs req serv & returns result to client

client present results on console to user

client-server comms use UDP


Services to be implemented by SERVER:

1) allow user to read content of file by specifying file pathname, offset(in bytes), no. of bytes
	-> service returns given no. of bytes of file content starting from designated offset in the file

	e.g. input : 2 bytes from file content 'abcd' at offset 1
		 output: 'bc'

		 input : file does not exist on server / offset exceeds file length
		 output: error message


2) allow user to insert content into a file by specifying the file pathname, offset(in bytes) and seq of bytes to write into the file
	-> service inserts seq of bytes into file at offset in the file
	-> original content of file after offset pushed forward

	e.g. input : 'b' into 'acd' at offset 1
		 output: 'abcd', ack of successful insertion

		 input : file does not exist on server / offset exceeds file length
		 output: error message


3) allow user to monitor updates made to content of specified file at server for a designated time period called monitor interval. To reg, Client provides pathname, length of monitor interval. After reg, internet address and port of client recorded by server. During the monitoring interval, every time an update is made by any client to content of file, updated file content is sent by server to registered client(s) through callback. After expiration of monitor interval, client record is removed from server to no longer deliver file content to the client. Assume user has issued reg req for monitoring is blocked from inputting any new req until monitor interval expires, i.e. dont have to use multiple threads for a client. Allow multiple clients to monitor updates to a file concurrently.


4) design & implement 2 more ops on the files through client-server communication. One idempotent the other non-idempotent.


5) implement client-side caching in the system. File content read by client is retained in buffer of client program. no cache replacement algo needs to be implemented. if file content available in cache, no need req from server. Updates made by client to file content always sent to server immediately. One-copy update semantics used by NFS is req to be implemented to maintain cache consistency. Freshness interval t specified as argument in the command.
