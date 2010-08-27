# -*- coding: utf-8 -*-
# Copyright (c) 2010 Tom Burdick <thomas.burdick@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import socket
from .connections import SocketConnection

class ClientConnection(SocketConnection):
    """Represents a connection to a server from a client. A SocketConnection template
    implementation.
    """
    def __init__(self, loop, sock, protocol, client):
        SocketConnection.__init__(self, loop, sock)
        self.client = client 
        self.protocol = protocol

    def read(self, data):
        """Pass along the data from the real connection to the protocol."""
        self.protocol.data(data)

    def error(self, error):
        """There as an error, so clear any circular references and
        tell the protocol.
        
        """
        self.protocol.connection_lost(error)
        self.protocol.transport = None
        self.client.connection_lost(error)
        
    def close(self):
        """Close a client connection and clear circular references.
        
        This should not be called by a protocol. This should be called
        by the server holding on to this connection.
        
        """
        SocketConnection.close(self)
        self.protocol.connection_lost()
        self.protocol.transport = None
        self.client.connection_lost()

class SocketClient(object):
    """A simple socket client."""
    def __init__(self, loop, factory):
        self.loop = loop
        self.factory = factory
        self.connection = None

    def _connect(self, sock):
        protocol = self.factory.build()
        self.connection = ClientConnection(self.loop, sock, protocol, self)
        protocol.make_connection(self.connection)
  
    def connect(self):
        """Should be overridden to create a socket and pass it to _connect."""
        pass

    def connection_lost(self, reason=None):
        """A stub to deal with lost connections. Reconnect, log, die, do
        whatever makes sense for each case here.

        This gets called when you call close.
        
        """
        pass

    def close(self):
        """Close the client connection."""
        self.connection.close()
        self.connection = None

class UnixClient(SocketClient):
    """A unix client is a socket client that connects to a domain socket."""
    def __init__(self, loop, factory, path):
        SocketClient.__init__(self, loop, factory)
        self.path = path

    def connect(self):
        """Create and connect to the socket."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self.path)
        self._connect(sock)

class TcpClient(SocketClient):
    """A unix client is a socket client that connects to a domain socket."""
    def __init__(self, loop, factory, host, port):
        SocketClient.__init__(self, loop, factory)
        self.host = host
        self.port = port

    def connect(self):
        """Create and connect to the socket."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        self._connect(sock)
