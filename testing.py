import socket
import platform
import getpass
import uuid

def get_info():
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(5, -1, -1)])
        system_info = platform.system()
        machine_info = platform.machine()
        processor_info = platform.processor()
        username = getpass.getuser()

        info_string = f"IP Address: {ip_address}\nMAC Address: {mac_address}\nSystem: {system_info}, Machine: {machine_info}, Processor: {processor_info}\nUsername: {username}"
        return info_string
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print(get_info())
