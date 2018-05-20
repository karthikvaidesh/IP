 Steps for Server:
	1.compile the source file GbnServer.java using the command :	javac GbnServer.java
	2.run the GbnServer file using command:	java GbnServer <port_num> <file_name> <probability>
								   example: java GbnServer 7735 abc.txt 0.01
	  Note: <file_name> is the file to be created on the server.
 
 
 
 Steps for Client:
	1.compile the source file GbnClient.java using the command :	javac GbnClient.java
	2.run the GbnClient file using command:	java GbnClient <server_hostname> <server_port_num> <file_to_be_transferred> <N> <MSS>
								   example: java GbnClient 192.168.0.114 7735 test_file.txt 64 500
	  Note: 1) <file_to_be_transferred> is the file to be transferred to the client.
			2) <file_to_be_transferred> must exist in the same directory as of GbnClient.java