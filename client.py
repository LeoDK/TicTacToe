import socket
import grid
import asn1tools

DEF_SERVER = "127.0.0.1"
DEF_SERVER_PORT = 50001
DEF_CLIENT_PORT = 50002

class Client:

    def __init__ (self, name, server_ip=DEF_SERVER, port=DEF_CLIENT_PORT, server_port=DEF_SERVER_PORT):
        self.name = name
        # Connexion socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('localhost', port))
        # Protocol syntax
        self.protocol = asn1tools.compile_files('TicTacToe.asn')
        self.connected = False

        try:
            print("Trying to connect to server ...")
            self.s.connect((server_ip, server_port))
            self.s.send( self.protocol.encode('Command', ('hello', {'name':self.name})) )

            data = self.s.recv(256)
            if 'invalidName' in self.protocol.decode('ServerAnswer', data):
                self.quit()
                raise Exception("Provided name is not correct")

            if 'helloX' in self.protocol.decode('ServerAnswer', data):
                self.player = 'X'
            else: # HelloO
                self.player = 'O'

            self.connected = True
            print("Connected to server :")
            print("Address :" + self.s.getpeername()[0])
            print("Port :" + str(self.s.getpeername()[1]))

        except Exception as e:
            print("Initialization error")
            self.quit()
            raise e

    def play (self, x, y):
        self.s.send( self.protocol.encode('Command', ('action'+self.player, {'x':x, 'y':y})) )

    def startGame (self):
        self.g = grid.Grid(' ')

        playing = (self.player == 'X')
        other = 'O' if playing else 'X'
        data = self.s.recv(256)
        decoded = self.protocol.decode('ServerAnswer', data)

        while 'validPosition' in decoded or 'invalidPosition' in decoded or 'play' in decoded:
            if decoded[0] == 'validPosition':
                x = decoded[1]['x']
                y = decoded[1]['y']
                self.g.grid[x][y] = self.player if playing else other
                playing = False
                print(self.g)

            else: # Play or invalidPosition
                if decoded[0] == 'invalidPosition':
                    print("Invalid position")
                playing = True
                x,y = Client.askPosUI ()
                self.play(x,y)

            data = self.s.recv(256)
            decoded = self.protocol.decode('ServerAnswer', data)

        if decoded[0] == 'tie':
            print("It's a tie !")

        elif decoded[0] == 'win':
            x = decoded[1]['x']
            y = decoded[1]['y']
            self.g.grid[x][y] = (self.player if playing else other)
            print("You won !")

        else: # lose
            x = decoded[1]['x']
            y = decoded[1]['y']
            self.g.grid[x][y] = self.player if playing else other
            print("You lost !")

        print("Final board:")
        print(self.g)

        self.quit()

    def quit (self):
        print("Shutting down client ...")
        self.s.close()

    @staticmethod
    def askPosUI ():
        x = int( input("x ? ") )
        y = int( input("y ? ") )
        print("")
        return (x,y)
