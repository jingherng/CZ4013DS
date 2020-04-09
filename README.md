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

assume that the server address and port number are known to the client (e.g., the server address and port number may be specified as arguments in the command that starts the client). 

server does not know the client address in advance

client address is obtained by the server when it receives a request from a client.

The client provides an interface that repeatedly asks the user to enter a request and sends the request to the server. Each reply or error message returned from the server should be printed on the screen. The interface provided by the client should include an option for the user to terminate the client. For simplicity, you may design a text-based interface on the console, i.e., a graphical user interface is not necessary. 

required to design the structures for request and reply messages, and describe your design in the report. 

must marshal the integer values, strings etc. before transmission and unmarshal them upon receipt.

You are required to implement the system with two different invocation
semantics: at-least-once and at-most-once. To do so, you will need to implement
techniques like timeouts, filtering duplicate request messages, and maintaining
histories. You can consult the textbook and the lecture notes for the details of
invocation semantics and associated techniques. Which semantics to use may be
specified as an argument in the command that starts the client/server. You can
assign a request identifier to each request for detecting duplicate requests. As part
of this project, you should simulate the loss of request and reply messages in
your program, and design experiments to compare the two invocation
semantics. Show that at-least-once invocation semantics can lead to wrong results
for non-idempotent operations, while at-most-once invocation semantics work
correctly for all operations. Describe your experiments and discuss the results in
the report. 

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




expected to design request/reply message formats, fully implement marshalling/unmarshalling and the fault-tolerance measures by yourself. You may use a byte array to store the marshaled data. Do NOT use any existing RMI, RPC, CORBA, Java object serialization facilities and input/output stream classes in Java.



The grading will be based on the course project only. The submission deadline of the course project remains at April 24 (Friday, week 14). Please be reminded that the submission includes the lab report, your source code and a demo video. The report and source code are to be submitted electronically through NTULearn (in the Assignment folder). The video is to be uploaded to a publicly accessible place with the link indicated on the cover page of your report. Given the uncertainty in this unusual period, I would suggest you submitting your project as early as possible if you can. If you do not submit by the due date, you will not get any mark for this course.
