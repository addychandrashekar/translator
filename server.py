# Import required modules
import deepl
import requests
import socket
import threading


HOST = '127.0.0.1'
PORT = 1234 # You can use any port between 0 to 65535
LISTENER_LIMIT = 5
active_clients = [] # List of all currently connected users

users_primary_language = {"addy": "English", "bob": "Chinese"}
language_to_deepl = {
    "Chinese": "ZH",
    "English": "EN-US"
}

def translate_message(message, preferred_language):
    translator = deepl.Translator(auth_key="150a2461-7620-0d22-a228-9d295b658aa7:fx")
    result = translator.translate_text(message, target_lang=language_to_deepl[preferred_language])
    print("result: ")
    result = result.text
    print("result: ")
    

    return result


# Function to listen for upcoming messages from a client
def listen_for_messages(client, username):
    while 1:

        message = client.recv(2048).decode('utf-8')
        if message != '':
            send_messages_to_all(message, username)

        else:
            print(f"The message send from client {username} is empty")


# Function to send message to a single client
def send_message_to_client(client, message, preferred_language):
    client.sendall(message.encode())

# Function to send any new message to all the clients that
# are currently connected to this server
def send_messages_to_all(message, username):
    for user, client, preferred_language in active_clients:
        if f"SERVER~{username}" not in message:
            message = translate_message(message, preferred_language)
            final_msg = username + '~' + message
            send_message_to_client(client, final_msg, preferred_language)
        
        else:
            split_arr = message.split(f"SERVER~")
            message = translate_message(split_arr[1], preferred_language)
            final_msg = f"SERVER~{message}"
            send_message_to_client(client, final_msg, preferred_language)


# Function to handle client
def client_handler(client):
    
    # Server will listen for client message that will
    # Contain the username
    while 1:
        print("client's username in server.py: ", client)
        username = client.recv(2048).decode('utf-8')
        if username != '':
            active_clients.append((username, client, users_primary_language[username]))
            prompt_message = "SERVER~" + f"{username} added to the chat"
            send_messages_to_all(prompt_message, username)
            break
        else:
            print("Client username is empty")

    threading.Thread(target=listen_for_messages, args=(client, username, )).start()

# Main function
def main():

    # Creating the socket class object
    # AF_INET: we are going to use IPv4 addresses
    # SOCK_STREAM: we are using TCP packets for communication
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Creating a try catch block
    try:
        # Provide the server with an address in the form of
        # host IP and port
        server.bind((HOST, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")

    # Set server limit
    server.listen(LISTENER_LIMIT)

    # This while loop will keep listening to client connections
    while 1:

        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")

        threading.Thread(target=client_handler, args=(client, )).start()


if __name__ == '__main__':
    main()