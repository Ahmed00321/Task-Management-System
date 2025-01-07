# Task-Management-System

Overview
This is a secure Task Manager application built with Python. It consists of a server and client, where the communication between them is encrypted using SSL. The server allows managing tasks such as adding, listing, and deleting tasks. It also supports sending files and sending notifications via email when tasks are added or deleted.

The project includes:

A server application for handling requests from clients.
A client application with a GUI interface using Tkinter.
A simple web interface using Flask to display tasks.



Server
Accepts commands to:
Add tasks
List tasks
Delete tasks
Send files
Sends email notifications for added or deleted tasks.
Encrypts communication with clients using SSL.
Logs all events to server_log.txt.


Client
GUI application to:
Add tasks
List tasks
Delete tasks
Send files
Send emails with the task list
Read the last email
Web interface to view tasks via Flask.



Security Notes
SSL Certificates: Use valid SSL certificates for secure communication.
Email Credentials: Replace the email and app-specific password placeholders with your own. Use environment variables or a .env file for security.



Potential Improvements
Add a database for persistent task storage.
Enhance the web interface for better task management.
Add authentication for users accessing the server.
