import socket
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os
import threading

QUIZ = "QUIZ"
UPLOAD = "UPLOAD"
DOWNLOAD = "DOWNLOAD"
CREATE = "CREATE"

HOST = '127.0.0.1'
PORT = 65432

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz, File Transfer Client")

        self.command_label = tk.Label(root, text="Enter command (QUIZ, UPLOAD, DOWNLOAD, CREATE):")
        self.command_label.pack()

        self.command_entry = tk.Entry(root, width=50)
        self.command_entry.pack()

        self.result_text = tk.Text(root, height=15, width=60)
        self.result_text.pack()

        self.send_button = tk.Button(root, text="Send Command", command=self.send_command)
        self.send_button.pack()

        self.sock = None

    def connect_to_server(self):
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.sock.connect((HOST, PORT))
                self.result_text.insert(tk.END, "Connected to server.\n")
            except Exception as e:
                messagebox.showerror("Error", f"Could not connect: {e}")
                self.sock = None

    def send_command(self):
        command = self.command_entry.get().strip()
        if command:
            threading.Thread(target=self._send_command_thread, args=(command,)).start()

    def _send_command_thread(self, command):
        self.connect_to_server()
        if self.sock:
            try:
                self.sock.sendall(command.encode())
                response = self.sock.recv(1024).decode()
                self.result_text.insert(tk.END, f"Server Response: {response}\n")
            except Exception as e:
                self.result_text.insert(tk.END, f"Error: {e}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
