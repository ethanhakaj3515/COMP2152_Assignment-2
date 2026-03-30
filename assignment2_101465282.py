"""
Author: <Ethan Hakaj>
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime

# TODO: Print Python version and OS name (Step iii)
platform_info = platform.platform()
print(f"Python Version: {platform.python_version()}")
print(f"Operating System: {platform_info}")


# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}


# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"
class NetworkTool:
    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if value:
            self.__target = value
        else:
            print("Target cannot be an empty string. Keeping previous target.")

    def __del__(self):
        print("NetworkTool instance destroyed")


# Q3: What is the benefit of using @property and @target.setter?
# TODO: Your 2-4 sentence answer here... (Part 2, Q3)

# Using @property and @target.setter allows for controlled access to the target attribute, ensuring that it cannot be set to an empty string and providing a clean interface for accessing and modifying the target.


# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)

# PortScanner inherits from NetworkTool, allowing it to reuse the target management functionality (getter and setter) without needing to reimplement it. This promotes code reuse and keeps the PortScanner class focused on its specific scanning functionality while leveraging the common features provided by NetworkTool.

# TODO: Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()
#
# - scan_port(self, port):
#     Q4: What would happen without try-except here?
class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()
#     TODO: Your 2-4 sentence answer here... (Part 2, Q4)

# Without try-except, any socket error (like connection refused or timeout) would cause the entire scanning process to crash, preventing the scanner from completing its task and potentially losing all progress made up to that point. Using try-except allows the scanner to handle errors gracefully, log them, and continue scanning other ports without interruption.

#     - try-except with socket operations
#     - Create socket, set timeout, connect_ex
#     - Determine Open/Closed status
#     - Look up service name from common_ports (use "Unknown" if not found)
#     - Acquire lock, append (port, status, service_name) tuple, release lock
#     - Close socket in finally block
#     - Catch socket.error, print error message
#
# - get_open_ports(self):
#     - Use list comprehension to return only "Open" results
#
#     Q2: Why do we use threading instead of scanning one port at a time?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q2)

# Using threading allows the port scanner to scan multiple ports concurrently, significantly reducing the total time required to complete the scan. Scanning one port at a time would be much slower, especially if many ports are being scanned, as it would have to wait for each connection attempt to timeout before moving on to the next port.

# - scan_range(self, start_port, end_port):
#     - Create threads list
#     - Create Thread for each port targeting scan_port
#     - Start all threads (one loop)
#     - Join all threads (separate loop)


# TODO: Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error

def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                port INTEGER,
                status TEXT,
                service TEXT,
                scan_date TEXT
            )
        """)
        for port, status, service in results:
            cursor.execute("""
                INSERT INTO scans (target, port, status, service, scan_date)
                VALUES (?, ?, ?, ?, ?)
            """, (target, port, status, service, datetime.datetime.now().isoformat()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection

def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT target, port, status, service, scan_date FROM scans")
        rows = cursor.fetchall()
        if rows:
            for target, port, status, service, scan_date in rows:
                print(f"Target: {target}, Port: {port}, Status: {status}, Service: {service}, Date: {scan_date}")
        else:
            print("No past scans found.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    pass
    # TODO: Get user input with try-except (Step ix)
    # - Target IP (default "127.0.0.1" if empty)
    # - Start port (1-1024)
    # - End port (1-1024, >= start port)
    # - Catch ValueError: "Invalid input. Please enter a valid integer."
    # - Range check: "Port must be between 1 and 1024."

    input_target = input("Enter target IP address (default 127.0.0.1): ").strip()
    if not input_target:
        input_target = "127.0.0.1"
    while True:
        try:
            start_port = int(input("Enter start port (1-1024): "))
            end_port = int(input("Enter end port (1-1024): "))
            if 1 <= start_port <= 1024 and 1 <= end_port <= 1024 and end_port >= start_port:
                break
            else:
                print("Port must be between 1 and 1024, and end port must be greater than or equal to start port.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    # TODO: After valid input (Step x)
    # - Create PortScanner object
    # - Print "Scanning {target} from port {start} to {end}..."
    # - Call scan_range()
    # - Call get_open_ports() and print results
    # - Print total open ports found
    # - Call save_results()
    # - Ask "Would you like to see past scan history? (yes/no): "
    # - If "yes", call load_past_scans()

    scanner = PortScanner(input_target)
    print(f"Scanning {scanner.target} from port {start_port} to {end_port}...")
    scanner.scan_range(start_port, end_port)
    open_ports = scanner.get_open_ports()
    for port, status, service in open_ports:
        print(f"Port {port}: {status} ({service})")
    print(f"Total open ports found: {len(open_ports)}")
    save_results(scanner.target, scanner.scan_results)
    if input("Would you like to see past scan history? (yes/no): ").strip().lower() == "yes":
        load_past_scans()


# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
# Diagram: See diagram_studentID.png in the repository root

# A useful new feature for the PortScanner could be to add a banner grabbing functionality, which attempts to retrieve and display the service banner for open ports. This would provide more detailed information about the services running on those ports, such as software versions, which can be valuable for security assessments. The diagram would show the PortScanner class with an additional method called grab_banner(port) that is called within scan_port() when a port is found to be open.
