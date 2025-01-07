import socket
import random
import os

# Quiz data
quiz_data = {
    "What is the capital of France?": "Paris",
    "What is the highest mountain in the world?": "Mount Everest",
    "What is the largest planet in our solar system?": "Jupiter",
    "What is the chemical symbol for water?": "H2O",
    "What is the name of Earth's only natural satellite?": "The Moon"
}

# Constants for commands
QUIZ = "QUIZ"
UPLOAD = "UPLOAD"
DOWNLOAD = "DOWNLOAD"
CREATE = "CREATE"


def shuffle_questions(questions):
    return random.sample(list(questions.items()), len(questions))


def handle_upload(conn, file_name):
    with open(file_name, "wb") as f:
        while True:
            data = conn.recv(1024)
            if data == b"END":  # End of file signal
                break
            f.write(data)
    conn.sendall(b"File uploaded successfully.")


def handle_download(conn, file_name):
    if os.path.exists(file_name):
        conn.sendall(b"READY")
        with open(file_name, "rb") as f:
            while chunk := f.read(1024):
                conn.sendall(chunk)
        conn.sendall(b"END")  # End of file signal
    else:
        conn.sendall(b"ERROR: File not found.")


def handle_create_file(conn, file_name, content):
    try:
        with open(file_name, "w") as f:
            f.write(content)
        conn.sendall(f"File {file_name} created successfully.".encode())
    except Exception as e:
        conn.sendall(f"ERROR: Could not create file. {e}".encode())


HOST = '127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reuse the port
    s.bind((HOST, PORT))
    s.listen()
    print("Server listening on port", PORT)

    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                command, *args = data.split(" ", 2)  # Parse command

                if command == QUIZ:
                    shuffled_questions = shuffle_questions(quiz_data)
                    score = 0

                    for question, answer in shuffled_questions:
                        conn.sendall(question.encode())  # Send question
                        user_answer = conn.recv(1024).decode().strip()  # Receive answer
                        if user_answer.lower() == answer.lower():
                            conn.sendall(b"Correct!")
                            score += 1
                        else:
                            conn.sendall(f"Incorrect. The answer is {answer}.".encode())

                    conn.sendall(f"Quiz over! You scored {score} out of {len(quiz_data)}.".encode())

                elif command == UPLOAD and len(args) > 0:
                    file_name = args[0]
                    conn.sendall(b"READY")
                    handle_upload(conn, file_name)

                elif command == DOWNLOAD and len(args) > 0:
                    file_name = args[0]
                    handle_download(conn, file_name)

                elif command == CREATE and len(args) > 1:
                    file_name = args[0]
                    content = args[1]
                    handle_create_file(conn, file_name, content)

                else:
                    conn.sendall(b"ERROR: Invalid command")
