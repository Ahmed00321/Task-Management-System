import socket
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, filedialog
import imaplib
from email import message_from_bytes
import webbrowser
from flask import Flask, render_template_string, redirect, url_for

CERT_FILE = "C:/Users/AHMED/mydomain.crt"

app = Flask(__name__)

tasks = []


def send_request(command):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.load_verify_locations(CERT_FILE)
        secure_socket = ssl_context.wrap_socket(client_socket, server_hostname="localhost")

        secure_socket.connect(("localhost", 12345))
        secure_socket.send(command.encode())

        response = secure_socket.recv(1024).decode()

        if response == "START_FILE":
            with open("received_file", "wb") as file:
                while True:
                    chunk = secure_socket.recv(1024)
                    if chunk == b"END_FILE":
                        break
                    file.write(chunk)
            response = "File received successfully and saved as 'received_file'."

        secure_socket.close()
        return response
    except ConnectionRefusedError:
        return "Unable to connect to the server."
    except ssl.SSLError as e:
        return f"SSL Error: {e}"


def add_task():
    task = simpledialog.askstring("Add Task", "Enter task description:")
    if task:
        tasks.append(task)
        response = send_request(f"add {task}")
        if "added successfully" in response:
            messagebox.showinfo("Task Added", f"Task '{task}' added successfully.")
        else:
            messagebox.showinfo("Response", response)


def list_tasks():
    response = send_request("list")

    tasks.clear()
    tasks.extend(response.split("\n"))

    messagebox.showinfo("Tasks", '\n'.join(tasks))


def delete_task():
    task_number = simpledialog.askinteger("Delete Task", "Enter task number to delete:")
    if task_number is not None and 0 <= task_number < len(tasks):
        task = tasks.pop(task_number)
        response = send_request(f"delete {task_number}")
        messagebox.showinfo("Task Deleted", f"Task '{task}' deleted successfully.")
    else:
        messagebox.showwarning("Invalid Task", "Invalid task number.")


def send_file():
    file_path = filedialog.askopenfilename(title="Select File")
    if file_path:
        response = send_request(f"sendfile {file_path}")
        messagebox.showinfo("Response", response)
    else:
        messagebox.showerror("Error", "No file selected.")


def send_email():
    response = send_request("list")
    tasks = response if "Tasks:" in response else "No tasks available."

    sender_email = "emmoo77889@gmail.com"
    sender_password = "rprf ncce rdql ruzr"
    recipient_email = simpledialog.askstring("Recipient Email", "Enter recipient's email:")

    if recipient_email:
        subject = "Task Manager - Task List"
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(tasks, "plain"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
            messagebox.showinfo("Success", "Email sent successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")


def read_last_email():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        email = "emmm66778@gmail.com"
        app_password = "csmu scdv ujpa zbco"
        mail.login(email, app_password)

        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        if result != "OK":
            raise Exception("Failed to search emails")

        email_ids = data[0].split()
        if not email_ids:
            messagebox.showinfo("No Emails", "No emails found in your inbox.")
            return

        latest_email_id = email_ids[-1]
        result, email_data = mail.fetch(latest_email_id, "(RFC822)")
        if result != "OK":
            raise Exception("Failed to fetch email")

        raw_email = email_data[0][1]
        msg = message_from_bytes(raw_email)

        email_subject = msg["Subject"]
        email_from = msg["From"]

        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    email_body = part.get_payload(decode=True).decode()
                    break
        else:
            email_body = msg.get_payload(decode=True).decode()

        mail.close()
        mail.logout()

        messagebox.showinfo("Last Email", f"From: {email_from}\nSubject: {email_subject}\n\n{email_body}")

    except imaplib.IMAP4.error as e:
        messagebox.showerror("IMAP Error", f"IMAP Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


def open_http_page():
    webbrowser.open("http://localhost:8000")


@app.route('/')
def show_tasks():
    return render_template_string('''
        <html>
        <head><title>Task List</title></head>
        <body>
            <h1>Task List</h1>
            <ul>
                {% for task in tasks %}
                    <li>{{ task }}</li>
                {% endfor %}
            </ul>
        </body>
        </html>
    ''', tasks=tasks)


if __name__ == "__main__":
    from threading import Thread
    def run_flask():
        app.run(debug=True, use_reloader=False, port=8000)

    thread = Thread(target=run_flask)
    thread.start()

    root = tk.Tk()
    root.title("Task Manager Client")
    root.geometry("1000x1000")
    root.configure(bg="#282c34")

    style = ttk.Style()
    style.configure("TButton", font=("Arial", 15), padding=10, width=20)

    title_label = tk.Label(root, text="Task Manager Client", font=("Arial", 30, "bold"), bg="#282c34", fg="white")
    title_label.pack(pady=30)

    add_button = ttk.Button(root, text="Add Task", command=add_task)
    add_button.pack(pady=20)

    list_button = ttk.Button(root, text="List Tasks", command=list_tasks)
    list_button.pack(pady=20)

    delete_button = ttk.Button(root, text="Delete Task", command=delete_task)
    delete_button.pack(pady=20)

    send_file_button = ttk.Button(root, text="Send File", command=send_file)
    send_file_button.pack(pady=20)

    send_email_button = ttk.Button(root, text="Send Email", command=send_email)
    send_email_button.pack(pady=20)

    read_email_button = ttk.Button(root, text="Read Last Email", command=read_last_email)
    read_email_button.pack(pady=20)

    open_http_button = ttk.Button(root, text="Open HTTP", command=open_http_page)
    open_http_button.pack(pady=20)

    root.mainloop()
