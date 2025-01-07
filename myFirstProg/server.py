import socket
import ssl
import threading
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import ttk

CERT_FILE = "C:/Users/AHMED/mydomain.crt"
KEY_FILE = "C:/Users/AHMED/mydomain.key"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 12345))
server_socket.listen(5)

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

tasks = []

def log_event(event):
    with open("server_log.txt", "a") as log_file:
        log_file.write(event + "\n")


def send_email(subject, body):
    sender_email = "emmoo77889@gmail.com"
    sender_password = "rprf ncce rdql ruzr"
    recipient_email = "emmm66778@gmail.com"

    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
        log_event("Email sent successfully.")
    except Exception as e:
        log_event(f"Failed to send email: {e}")

def handle_client(client_socket):
    try:
        ssl_client_socket = ssl_context.wrap_socket(client_socket, server_side=True)
        request = ssl_client_socket.recv(1024).decode().strip()
        command, *args = request.split(" ")

        if command.lower() == "add":
            task = " ".join(args)
            tasks.append(task)
            response = f"Task '{task}' added successfully."
            log_event(response)
            send_email("New Task Added", f"The following task was added: {task}")

        elif command.lower() == "list":
            if tasks:
                response = "Tasks:\n" + "\n".join(f"{i+1}. {task}" for i, task in enumerate(tasks))
            else:
                response = "No tasks available."
            log_event("Listed tasks.")

        elif command.lower() == "delete":
            try:
                task_number = int(args[0]) - 1
                if 0 <= task_number < len(tasks):
                    deleted_task = tasks.pop(task_number)
                    response = f"Task '{deleted_task}' deleted successfully."
                    send_email("Task Deleted", f"The following task was deleted: {deleted_task}")
                else:
                    response = "Invalid task number."
            except (IndexError, ValueError):
                response = "Please specify a valid task number."
            log_event(response)

        elif command.lower() == "sendfile":
            try:
                file_path = " ".join(args)
                if os.path.exists(file_path):
                    ssl_client_socket.send(b"START_FILE")
                    with open(file_path, "rb") as file:
                        while chunk := file.read(1024):
                            ssl_client_socket.send(chunk)
                    ssl_client_socket.send(b"END_FILE")
                    response = f"File '{file_path}' sent successfully."
                else:
                    response = "File not found."
                log_event(response)
            except Exception as e:
                response = f"Error sending file: {e}"
                log_event(response)

        else:
            response = "Unknown command. Available commands: add, list, delete, sendfile."

        ssl_client_socket.send(response.encode())
        ssl_client_socket.close()
    except Exception as e:
        log_event(f"Error: {e}")

def start_server():
    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

root = tk.Tk()
root.title("Task Manager Server")
root.geometry("800x400")
root.configure(bg="#282c34")

label = ttk.Label(root, text="Task Manager Server is running with SSL...", font=("Arial", 14), foreground="white", background="#282c34")
label.pack(pady=60)

threading.Thread(target=start_server, daemon=True).start()

root.mainloop()
