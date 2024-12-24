import socket
import threading
import soil_data_parse as parser
# import time
# import mqtt_lib as mqtt
import mqtt_lib_gcp as mqtt

def thread_excepthook(args):
    print(f"Unhandled exception in thread {args.thread.name}: {args.exc_type}, {args.exc_value}")

threading.excepthook = thread_excepthook

# Limit the number of threads = no. of simutaneous devices
max_threads = 5
thread_semaphore = threading.Semaphore(max_threads)
lock = threading.Lock()

# Function to handle client communication
def handle_client(client_socket,client_address,broker_client):
    with thread_semaphore:  # Ensure the number of active threads doesn't exceed the limit
        with client_socket:
            if client_socket.fileno() == -1:
                print('Scoket is not free')
            try:
                with lock:
                    print(f"Thread started for {client_address}")
                while True:
                    try:
                        data = client_socket.recv(1024)  # Receive up to 1024 bytes
                        if not data:
                            with lock:
                                print(f"Client {client_address} disconnected.")
                            break
                        hex_data = data.hex()
                        with lock:
                            print(f"Received (Hex): {hex_data}")
                        c_data = parser.auto_parse(data)
                        with lock:
                            print(c_data)
                        # send data
                        for item in c_data:
                            # mqtt.send_data(client=broker_client,topic=mqtt.topic+'\data',data=item)
                            mqtt.send_data(broker_client,topic=mqtt.topic_name,data=item)

                    except ConnectionResetError:
                        with lock:
                            print(f"Client {client_address} reset the connection.")
                        break
            except Exception as e:
                with lock:
                    print(f"Error in thread for {client_address}: {e}")
            finally:
                try:
                    client_socket.close()
                    with lock:
                        print(f"Connection with {client_address} closed.")
                except Exception as e:
                    with lock:
                        print(f"Error closing socket for {client_address}: {e}")

def start_server(host='0.0.0.0', port=8100):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # broker_client = mqtt.init_broker_client()
    publisher = mqtt.init_gcp()
    if publisher is None:
        print('MQTT client initialization error')
        exit(1)
    try:
        # Bind and listen on the specified host and port
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server running on {host}:{port}. Press Ctrl+C to stop.")

        while True:
            print("Waiting for a connection...")
            try:
                client_socket, client_address = server_socket.accept()
                print(f"Connection accepted from {client_address}")

                print(f"Before thread: Socket fileno for {client_address} is {client_socket.fileno()}")
                # Start a new thread for each client
                # lock.acquire()
                client_thread = threading.Thread(target=handle_client, 
                                                 args=(client_socket,client_address,publisher), 
                                                 daemon=True)
                client_thread.start()
                print(f"After thread: Socket fileno for {client_address} is {client_socket.fileno()}")
                # client_thread = start_new_thread(handle_client,arg=(client_socket, client_address))
                
            except Exception as e:
                print(f"Error handling client: {e}")
    except KeyboardInterrupt:
        server_socket.close()
        # mqtt.disconnect(broker_client=broker_client)
        print("\nKeyboard interrupt received. Shutting down the server.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure the server socket is closed in any case
        server_socket.close()
        # mqtt.disconnect(broker_client=broker_client)
        print("Socket closed. Server stopped.")

# Start the server
if __name__ == "__main__":
    start_server()
