import socket

account = {
    "host": "localhost" if socket.gethostname() == "REMOTE_NAME" else "REMOTE_HOST",
    "port": "PORT",
    "user": "USER",
    "password": "PASSWORD",
    "database": "Linker",
    "charset": "utf8mb4",
    "collation": "utf8mb4_general_ci",
    "autocommit": False
}
