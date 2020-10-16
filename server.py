import socket
import grid
import asn1tools

DEF_CLIENT = "127.0.0.1"
DEF_SERVER_PORT = 50001
DEF_CLIENT_PORT = 50002

class Server:

    def __init__ (self, client_ip=DEF_CLIENT, port=DEF_SERVER_PORT, client_port=DEF_CLIENT_PORT):
        # Listening socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', port))
        # Protocol syntax
        self.protocol = asn1tools.compile_files('TicTacToe.asn')

        try:
            print("Listening for incoming connexions ...")
            self.state = "Listening"
            self.s.listen(5)

            # Waiting for 2 clients
            sock, addr = self.s.accept()
            self.cl1 = Client(sock, addr, '', 'X')
            self.cl1.sock.send( self.protocol.encode('ServerAnswer', ('helloX', {})) )
            self.cl1.name = self.protocol.decode( 'Command', self.cl1.sock.recv(128) )[1]['name']
            while not Server.checkName( self.cl1.name ):
                self.cl1.sock.send( self.protocol.encode('ServerAnswer', ('invalidName', {})) )
                self.cl1.name = self.protocol.decode( 'Command', self.cl1.sock.recv(128) )[1]['name']

            print("Player 1 connected:")
            print(self.cl1)

            sock, addr = self.s.accept()
            self.cl2 = Client(sock, addr, '', 'O')
            self.cl2.sock.send( self.protocol.encode('ServerAnswer', ('helloO', {})) )
            self.cl2.name = self.protocol.decode( 'Command', self.cl2.sock.recv(128) )[1]['name']
            while not Server.checkName( self.cl2.name ):
                self.cl2.sock.send( self.protocol.encode('ServerAnswer', ('invalidName', {})) )
                self.cl2.name = self.protocol.decode( 'Command', self.cl2.sock.recv(128) )[1]['name']

            print("Player 2 connected:")
            print(self.cl2)

            self.state = "Connected"

        except Exception as e:
            print("Initialization error")
            self.quit()
            raise e

    def waitPlayer (self, client):
        client.sock.send( self.protocol.encode('ServerAnswer', ('play', {})) )
        data = self.protocol.decode( 'Command', client.sock.recv(128) )[1]
        x = data['x']
        y = data['y']

        while not self.checkPos(x,y):
            client.sock.send( self.protocol.encode('ServerAnswer', ('invalidPosition', {})) )
            data = self.protocol.decode( 'Command', client.sock.recv(128) )[1]
            x = data['x']
            y = data['y']

        self.g.grid[x][y] = client.player
        return (x,y)

    def startGame (self):
        self.g = grid.Grid(' ')
        self.state = "Playing"
        client = self.cl1
        x,y = 0,0
        while not (self.checkWin()[0] or self.checkTie()):
            x,y = self.waitPlayer (client)
            self.cl1.sock.send( self.protocol.encode('ServerAnswer', ('validPosition', {'x':x, 'y':y})) )
            self.cl2.sock.send( self.protocol.encode('ServerAnswer', ('validPosition', {'x':x, 'y':y})) )
            if client == self.cl1:
                client = self.cl2
            else:
                client = self.cl1
            client.sock.send( self.protocol.encode('ServerAnswer', ('play', {})) )

        if self.checkTie():
            print("It's a tie !")
            self.cl1.sock.send( self.protocol.encode('ServerAnswer', ('tie', {})) )
            self.cl2.sock.send( self.protocol.encode('ServerAnswer', ('tie', {})) )

        else: # There is a winner
            winner = self.checkWin()[1]
            loser = self.cl1 if (self.cl2 == winner) else self.cl2
            print("Winner : " + winner.name)
            winner.sock.send( self.protocol.encode('ServerAnswer', ('win', {'x':x, 'y':y})) )
            loser.sock.send( self.protocol.encode('ServerAnswer', ('lose', {'x':x, 'y':y})) )

        self.quit()

    def quit (self):
        print("Shutting down server...")
        self.cl1.sock.close()
        self.cl2.sock.close()
        self.s.close()
        self.state = "Closed"

    @staticmethod
    def checkName (name):
        return (name != '') and (len(name)<=32) # Purely arbitrary

    def checkPos (self, x, y):
        return (0<=x) and (x<=2) and (y<=2) and (0<=y) and (self.g.grid[x][y] == self.g.neutral)

    def checkTie (self):
        for line in self.g.grid:
            for elem in line:
                if elem == self.g.neutral:
                    return False
        return not self.checkWin()[0]

    def checkWin (self):
        f = lambda x : self.cl1 if x == 'X' else self.cl2
        # Check lignes
        for x in range(3):
            if self.g.grid[x][0] != self.g.neutral and self.g.grid[x][0] == self.g.grid[x][1] and self.g.grid[x][0] == self.g.grid[x][2]:
                return (True, f(self.g.grid[x][0]))
        # Check colonnes
        for y in range(3):
            if self.g.grid[0][y] != self.g.neutral and self.g.grid[0][y] == self.g.grid[1][y] and self.g.grid[0][y] == self.g.grid[2][y]:
                return (True, f(self.g.grid[0][y]))
        # Check diag
        if self.g.grid[0][0] != self.g.neutral and self.g.grid[0][0] == self.g.grid[1][1] and self.g.grid[0][0] == self.g.grid[2][2]:
            return (True, f(self.g.grid[0][0]))
        if self.g.grid[0][2] != self.g.neutral and self.g.grid[0][2] == self.g.grid[1][1] and self.g.grid[0][2] == self.g.grid[2][0]:
            return (True, f(self.g.grid[1][1]))
        return (False, None)

class Client:

    def __init__ (self, sock, addr, name, player):
        self.sock = sock
        self.addr = addr
        self.name = name
        self.player = player # 'X' or 'O'

    def __str__ (self):
        ret = ""
        ret = ret + "Name :" + self.name + "\n"
        ret = ret + "Address :" + self.addr[0] + "\n"
        ret = ret + "Port :" + str(self.addr[1])
        return ret
