import socket, paramiko, threading

class SSH_Server:
    def check_auth_password(self, username, password):
        return paramiko.AUTH_FAILED 
        
    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_FAILED

def handle_connection(client_sock, server_key):
    """
    Handles a client connection by adding the server key, starting the SSH server,
    binding the server socket, generating a server key, and accepting client connections.

    Args:
        client_sock (socket.socket): The client socket object.
        server_key (paramiko.RSAKey): The server key object.

    Returns:
        None
    """
    transport.add_server_key(server_key)
    ssh = SSH_Server()
    transport.start_server(server=ssh)
            
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', 22)) # Port 22
    server_sock.listen(100)
            
    server_key = paramiko.RSAKey.generate(2048)
                                                
    while True:
        client_sock, addr = server_sock.accept()
        print('Connection from %s:%d' % (addr[0], addr[1]))
        threading.Thread(target=handle_connection, args=(client_sock, server_key)).start()

def main(honey_ip, honey_port):
    # Your main code logic here
    print(f"Running main code logic with honey_ip={honey_ip} and honey_port={honey_port}")

if __name__ == '__main__':
    honey_ip = '0.0.0.0'  # Replace with the actual IP address
    honey_port = 22  # Replace with the actual port number
    main(honey_ip, honey_port)
    
   