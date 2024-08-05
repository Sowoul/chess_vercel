from flask import Flask, render_template
from flask_socketio import SocketIO




class Piece:
    def __init__(self, val=0, color=None, type=None):
        self.val = val
        self.color = color
        self.type = type
    def __str__(self):
        return f"[{self.type}({self.color})]"

    def to_dict(self):
        return {
            'val': self.val,
            'color': self.color,
            'type': self.type
        }





class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
    
    def setup(self):
        for i in range(8):
            self.board[1][i] = Piece(1, 'B', '♟')
            self.board[-2][i] = Piece(1, 'W', '♙')
        self.board[0][0] = self.board[0][-1] = Piece(5, 'B', '♜')
        self.board[-1][0] = self.board[-1][-1] = Piece(5, 'W', '♖')
        self.board[0][1] = self.board[0][-2] = Piece(3, 'B', '♞')
        self.board[-1][1] = self.board[-1][-2] = Piece(3, 'W', '♘')
        self.board[0][2] = self.board[0][-3] = Piece(3, 'B', '♝')
        self.board[-1][2] = self.board[-1][-3] = Piece(3, 'W', '♗')
        self.board[0][4] = Piece(100, 'B', '♚')
        self.board[-1][4] = Piece(100, 'W', '♔')
        self.board[0][3] = Piece(9, 'B', '♛')
        self.board[-1][3] = Piece(9, 'W', '♕')

    def move(self, start, end):
        pos1 = self.getpiece(start)
        x1, y1 = ord(start[0]) - ord('a'), 8-int(start[1])
        self.board[y1][x1] = None
        x2, y2 = ord(end[0]) - ord('a'), 8-int(end[1])
        self.board[y2][x2] = pos1

    def getpiece(self, location):
        x, y = ord(location[0]) - ord('a'), 8-int(location[1]) 
        return self.board[y][x]

    def to_dict(self):
        return [
            [piece.to_dict() if piece else None for piece in row]
            for row in self.board
        ]
    def __str__(self):
        final="     "
        for elem in ['   a   ','   b   ','   c   ','   d   ','   e   ', '   f   ', '   g   ', '   h   ']:
            final+=f"{elem}"
        final+='\n'
        rw=1
        for row in self.board:
            final+=f"{rw}    "
            for elem in row:
                final+=f"{elem} " if elem else '   .   '
            final+='\n\n'
            rw+=1
        return final

undo=[]
redo=[]



def make_board(arr):
    temp=Board()
    for i,row in enumerate(arr):
        for j,elem in enumerate(row):
            if elem:
                temp.board[i][j]=Piece(elem['val'] , elem['color'], elem['type'])
    return temp



board=Board()
board.setup()



app=Flask(__name__)
socket = SocketIO(app=app)





@app.route('/')
def index():
    return render_template('index.html', board=board.to_dict())





@socket.on('connect')
def aa():
    socket.emit('getboard' , {'board' : board.to_dict()})





@socket.on('move')
def mv(msg):
    temp = make_board(msg["board"])
    if not temp.getpiece(msg["start"]):
        socket.emit('failure' , {'reason' : 'No Piece Selected'})
        return
    temp.move(msg["start"] , msg["to"])
    store = temp.to_dict()
    undo.append(store)
    global redo
    redo=[]
    socket.emit('getboard', {"board":store})





@socket.on('resetboard')
def reset():
    global board
    board =  Board()
    global undo
    undo=[]
    global redo
    redo=[]
    board.setup()
    store=board.to_dict()
    socket.emit('getboard', {'board':store})





@socket.on('undo')
def und():
    if len(undo)<=1:
        if len(undo)==1:
            redo.append(undo.pop())
        temp= Board()
        temp.setup()
        store=temp.to_dict()
        socket.emit('getboard',{ 'board'  : store})
        return
    redo.append(undo.pop())
    global board
    board=make_board(undo[-1])
    socket.emit('getboard',{'board' :undo[-1]})




@socket.on('redo')
def red():
    if len(redo)==0:
        return
    undo.append(redo.pop())
    global board
    board=make_board(undo[-1])
    socket.emit('getboard',{'board' :undo[-1]})





if __name__ == '__main__':
    socket.run(app=app, debug=True, port=8080)
