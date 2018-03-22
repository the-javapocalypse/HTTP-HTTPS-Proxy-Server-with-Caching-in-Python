'''
Proxy Server in Python.
Features: HTTP/HTTPS requests handling
          Caching works fine for HTTPS but cannot render webpage properly for HTTP
          Logging
          Websites Blacklisting
          IP Blacklisting
'''


import socket, sys, datetime, time
from _thread import start_new_thread


class Server:
    # Constructors initializing basic architecture
    def __init__(self, blacklisted_ips=False, blacklist_websites=False):
        self.max_conn = 0
        self.buffer_size = 0
        self.socket = 0
        self.port = 0
        self.blacklisted_ip_lookup = blacklisted_ips
        self.blacklist_websites_lookup = blacklist_websites

    # Function to write log
    def write_log(self, msg):
        with open("log/log.txt", "a+") as file:
            file.write(msg)
            file.write("\n")

    # Helper Function to get Time Stamp
    def getTimeStampp(self):
        return "[" + str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + "]"

    # Function which triggers the server
    def start_server(self, conn=5, buffer=4096, port=8080):
        try:
            self.write_log(self.getTimeStampp() + "   \n\nStarting Server\n\n")

            self.listen(conn, buffer, port)

        except KeyboardInterrupt:
            print(self.getTimeStampp() + "   Interrupting Server.")
            self.write_log(self.getTimeStampp() + "   Interrupting Server.")
            time.sleep(.5)

        finally:
            print(self.getTimeStampp() + "   Stopping Server...")
            self.write_log(self.getTimeStampp() + "   Stopping Server")
            sys.exit()

    # Listener for incoming connections
    def listen(self, No_of_conn, buffer, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', port))
            s.listen(No_of_conn)
            print(self.getTimeStampp() + "   Listening...")
            self.write_log(
                self.getTimeStampp() + "   Initializing Sockets [ready] Binding Sockets [ready] Listening...")

        except:
            print(self.getTimeStampp() + "   Error: Cannot start listening...")
            self.write_log(self.getTimeStampp() + "   Error: Cannot start listening...")
            sys.exit(1)

        while True:
            # Try to accept new connections and read the connection data in another thread
            try:
                conn, addr = s.accept()
                # print(self.getTimeStampp() + "   Request received from: ", addr)
                self.write_log(
                    self.getTimeStampp() + "   Request received from: " + addr[0] + " at port: " + str(addr[1]))
                start_new_thread(self.connection_read_request, (conn, addr, buffer))

            except Exception as e:
                print(self.getTimeStampp() + "  Error: Cannot establish connection..." + str(e))
                self.write_log(self.getTimeStampp() + "  Error: Cannot establish connection..." + str(e))
                sys.exit(1)

        s.close()

    # helper Function to generate header to send response in HTTPS connections
    def generate_header_lines(self, code, length):
        h = ''
        if code == 200:
            # Status code
            h = 'HTTP/1.1 200 OK\n'
            h += 'Server: Jarvis\n'

        elif code == 404:
            # Status code
            h = 'HTTP/1.1 404 Not Found\n'
            h += 'Date: ' + time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + '\n'
            h += 'Server: Jarvis\n'

        h += 'Content-Length: ' + str(length) + '\n'
        h += 'Connection: close\n\n'

        return h

    # Function to read request data
    def connection_read_request(self, conn, addr, buffer):
        # Try to split necessary info from the header
        try:
            request = conn.recv(buffer)
            header = request.split(b'\n')[0]
            requested_file = request
            requested_file = requested_file.split(b' ')
            url = header.split(b' ')[1]

            # Stripping Port and Domain
            hostIndex = url.find(b"://")
            if hostIndex == -1:
                temp = url
            else:
                temp = url[(hostIndex + 3):]

            portIndex = temp.find(b":")

            serverIndex = temp.find(b"/")
            if serverIndex == -1:
                serverIndex = len(temp)

            # If no port in header i.e, if http connection then use port 80 else the port in header
            webserver = ""
            port = -1
            if (portIndex == -1 or serverIndex < portIndex):
                port = 80
                webserver = temp[:serverIndex]
            else:
                port = int((temp[portIndex + 1:])[:serverIndex - portIndex - 1])
                webserver = temp[:portIndex]

            # Stripping requested file to see if it exists in cache
            requested_file = requested_file[1]
            print("Requested File ", requested_file)

            # Stripping method to find if HTTPS (CONNECT) or HTTP (GET)
            method = request.split(b" ")[0]

            # Checking for blacklisted ips
            if addr[0] in self.blacklisted_ip_lookup:
                print(self.getTimeStampp() + "    IP Blacklisted")
                self.write_log(self.getTimeStampp() + "   IP Blacklisted")
                conn.close()

            # Checking for blacklisted domains
            target = webserver
            target = target.replace(b"http://", b"").split(b".")[1].decode("utf-8")
            try:
                if target in self.blacklist_websites_lookup:
                    print(self.getTimeStampp() + "   Website Blacklisted")
                    self.write_log(self.getTimeStampp() + "   Website Blacklisted")
                    conn.close()
            except:
                pass

            # If method is CONNECT (HTTPS)
            if method == b"CONNECT":
                print(self.getTimeStampp() + "   CONNECT Request")
                self.write_log(self.getTimeStampp() + "   HTTPS Connection request")
                self.https_proxy(webserver, port, conn, request, addr, buffer, requested_file)

            # If method is GET (HTTP)
            else:
                print(self.getTimeStampp() + "   GET Request")
                self.write_log(self.getTimeStampp() + "   HTTP Connection request")
                self.http_proxy(webserver, port, conn, request, addr, buffer, requested_file)

        except Exception as e:
            # print(self.getTimeStampp() + "  Error: Cannot read connection request..." + str(e))
            # self.write_log(self.getTimeStampp() + "  Error: Cannot read connection request..." + str(e))
            return

    # Function to handle HTTP Request
    def http_proxy(self, webserver, port, conn, request, addr, buffer_size, requested_file):
        # Stripping file name
        requested_file = requested_file.replace(b".", b"_").replace(b"http://", b"_").replace(b"/", b"")

        # Trying to find in cache
        try:
            print(self.getTimeStampp() + "  Searching for: ", requested_file)
            print(self.getTimeStampp() + "  Cache Hit")
            file_handler = open(b"cache/" + requested_file, 'rb')
            self.write_log(self.getTimeStampp() + "  Cache Hit")
            response_content = file_handler.read()
            file_handler.close()
            response_headers = self.generate_header_lines(200, len(response_content))
            conn.send(response_headers.encode("utf-8"))
            time.sleep(1)
            conn.send(response_content)
            conn.close()

        # If no cache hit, request from web
        except Exception as e:
            print(e)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((webserver, port))
                s.send(request)

                print(self.getTimeStampp() + "  Forwarding request from ", addr, " to ", webserver)
                self.write_log(
                    self.getTimeStampp() + "  Forwarding request from " + addr[0] + " to host..." + str(webserver))
                # Makefile for socket
                file_object = s.makefile('wb', 0)
                file_object.write(b"GET " + b"http://" + requested_file + b" HTTP/1.0\n\n")
                # Read the response into buffer
                file_object = s.makefile('rb', 0)
                buff = file_object.readlines()
                temp_file = open(b"cache/" + requested_file, "wb+")
                for i in range(0, len(buff)):
                    temp_file.write(buff[i])
                    conn.send(buff[i])

                print(self.getTimeStampp() + "  Request of client " + str(addr) + " completed...")
                self.write_log(self.getTimeStampp() + "  Request of client " + str(addr[0]) + " completed...")
                s.close()
                conn.close()

            except Exception as e:
                print(self.getTimeStampp() + "  Error: forward request..." + str(e))
                self.write_log(self.getTimeStampp() + "  Error: forward request..." + str(e))
                return

    # Function to handle HTTPS Connection
    def https_proxy(self, webserver, port, conn, request, addr, buffer_size, requested_file):
        # Stripping for filename
        requested_file = requested_file.replace(b".", b"_").replace(b"http://", b"_").replace(b"/", b"")

        # Trying to find in cache
        try:
            print(self.getTimeStampp() + "  Searching for: ", requested_file)
            file_handler = open(b"cache/" + requested_file, 'rb')
            print("\n")
            print(self.getTimeStampp() + "  Cache Hit\n")
            self.write_log(self.getTimeStampp() + "  Cache Hit\n")
            response_content = file_handler.read()
            file_handler.close()
            response_headers = self.generate_header_lines(200, len(response_content))
            conn.send(response_headers.encode("utf-8"))
            time.sleep(1)
            conn.send(response_content)
            conn.close()

        # If no Cache Hit, request data from web
        except:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # If successful, send 200 code response
                s.connect((webserver, port))
                reply = "HTTP/1.0 200 Connection established\r\n"
                reply += "Proxy-agent: Jarvis\r\n"
                reply += "\r\n"
                conn.sendall(reply.encode())
            except socket.error as err:
                pass
                # print(self.getTimeStampp() + "  Error: No Cache Hit in HTTPS because " + str(err))
                # self.write_log(self.getTimeStampp() + "  Error: No Cache Hit in HTTPS beacuse" + str(err))

            conn.setblocking(0)
            s.setblocking(0)
            print(self.getTimeStampp() + "  HTTPS Connection Established")
            self.write_log(self.getTimeStampp() + "  HTTPS Connection Established")
            while True:
                try:
                    request = conn.recv(buffer_size)
                    s.sendall(request)
                except socket.error as err:
                    pass

                try:
                    reply = s.recv(buffer_size)
                    conn.sendall(reply)
                except socket.error as e:
                    pass


if __name__ == "__main__":
    # Provide a list of ips and domains if necessary to add in blacklist. Websites need only the domains without 'www.' and '.com'
    server = Server(['127.0.0.81'],['facebook'])
    server.start_server()
