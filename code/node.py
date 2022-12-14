import random
from concurrent import futures
import logging
import socket
import asyncio
from time import sleep

import grpc
import pokemonou_pb2
import pokemonou_pb2_grpc

import configparser

# Global variables
global board, t, p, b, pokedex, path_
def create_board():
    global board
    board = {}
    # load config file
    parser = configparser.ConfigParser()
    parser.read('config.ini')

    # Get all the keys in a section
    pokemon = parser.options('pokemon')
    pokemon = sorted(pokemon)

    trainer = parser.options('trainer')
    trainer = sorted(trainer)
    

    t, p, b = parser.get('param', 't'), parser.get('param', 'p'), parser.get('param', 'b')
    t, p, b = int(t), int(p), int(b)

    for i in range(b):
        for j in range(b):
            board[(i, j)] = {}
            board[(i, j)]['trainer'] = ''
            board[(i, j)]['pokemon'] = []
        
    # assign randomly
    for i in range(p):
        x = random.randint(0, b-1)
        y = random.randint(0, b-1)
        board[(x, y)]['pokemon'].append(pokemon[i])
        
    for i in range(t):
        x = random.randint(0, b-1)
        y = random.randint(0, b-1)
        # assign trainer to location of board where there is no trainer and no pokemon
        if (board[(x, y)]['trainer'] == '' and board[(x, y)]['pokemon'] == []):
            board[(x, y)]['trainer'] = trainer[i]
        else:
            x = random.randint(0, b-1)
            y = random.randint(0, b-1)
            board[(x, y)]['trainer'] = trainer[i]
    return board, b, p

# implement the Pokemonou service
class Pokemonou(pokemonou_pb2_grpc.PokemonouServicer):
    global board, b, p, pokedex, path_
    pokedex = {} # key = trainer, value = {pokemon: (x, y)}, (x, y) is where the pokemon captured
    path_ = {}
    def __init__(self):
        self.lock = 'server'
        self.board, self.b, self.p = create_board()
        self.pokemon_left = self.p
        self.pokedex = pokedex
        self.path = path_
 
    def check_board(self, request, context):
        """Missing associated documentation comment in .proto file."""
        hostname = request.hostname
        pos = []
        mov_indicator = []
        # find the location of the hostname
        if ('trainer' in hostname):
            for key, value in self.board.items():
                if (value['trainer'] == hostname):
                    pos.append(key[0])
                    pos.append(key[1])
                    break
            # check all the 8 directions if trainer can move
            i, j = pos[0], pos[1]
            moves = [[i - 1, j - 1], [i - 1, j], [i - 1, j + 1], [i, j - 1], [i, j + 1], [i + 1, j - 1], [i + 1, j], [i + 1, j + 1]]
    
            for position in moves:
                if (position[0] < 0 or position[1] < 0 or position[0] > self.b-1 or position[1] > self.b-1): # out of bound
                    mov_indicator.append(-1)
                elif(self.board[(position[0], position[1])]['trainer'] != ''): # if the block contains trainer
                    mov_indicator.append(-1)
                elif(self.board[(position[0], position[1])]['pokemon'] == []): # if the block is empty
                    mov_indicator.append(0)
                else: # if the block contains pokemon
                    mov_indicator.append(1)
            self.lock = hostname
            return pokemonou_pb2.check_position(x = mov_indicator, lock=self.lock, alive=0, pokemon_left=self.pokemon_left, current_position=pos)
        else:
            flag = 0
            for key, value in self.board.items():
                if (hostname in value['pokemon']):
                    pos.append(key[0])
                    pos.append(key[1])
                    flag = 1
                    break
                else:
                    return pokemonou_pb2.check_position(x = [-1], lock = self.lock, alive=0, pokemon_left=self.pokemon_left, current_position=[-1, -1])
            # check all the 8 directions if trainer can move
            i, j = pos[0], pos[1]
            moves = [[i - 1, j - 1], [i - 1, j], [i - 1, j + 1], [i, j - 1], [i, j + 1], [i + 1, j - 1], [i + 1, j], [i + 1, j + 1]]
            for position in moves:
                if (position[0] < 0 or position[1] < 0 or position[0] > self.b - 1 or position[1] > self.b - 1): # out of bound
                    mov_indicator.append(-1)
                elif(self.board[(position[0], position[1])]['trainer'] != ''): # if the block contains trainer
                    mov_indicator.append(-1)
                else: # if the block is empty or contains pokemon
                    mov_indicator.append(1)
            self.lock = hostname
            self.flag = flag
            return pokemonou_pb2.check_position(x = mov_indicator, lock=self.lock, alive=1, pokemon_left=self.pokemon_left, current_position=pos)

    def move(self, request, context):
        hostname = request.hostname
        if(self.lock != request.hostname):
            return pokemonou_pb2.complete_move(success=0)
        
        elif('trainer' in request.hostname):
            self.board[(request.cur_x, request.cur_y)]['trainer'] = ''
            self.board[(request.newx, request.newy)]['trainer'] = request.hostname
            
            if (not request.hostname in self.path):
                self.path[request.hostname] = []
                print(self.path[request.hostname])
            pos = (request.newx, request.newy)
            self.path[request.hostname].append(pos)
            
            if (request.toCapture == 1):
                if not hostname in self.pokedex:
                    self.pokedex[hostname] = {}
                for poke in self.board[(request.newx, request.newy)]['pokemon']:
                    self.pokedex[hostname][poke] = (request.newx, request.newy)   
                
                self.pokemon_left -= len(self.board[(request.newx, request.newy)]['pokemon'])
                self.board[(request.newx, request.newy)]['pokemon'] = [] # clear the pokemon in the block
            self.lock = 'server'
            self.print_board()
            return pokemonou_pb2.complete_move(success=1)
        elif('pokemon' in request.hostname):
            self.board[(request.cur_x, request.cur_y)]['pokemon'].pop(request.hostname)
            self.board[(request.x, request.y)]['pokemon'][request.hostname] = request.hostname
            # keep track of path
            if (not hostname in self.path):
                self.path[hostname] = []
            self.path[hostname].append((request.newx, request.newy))
            
            self.lock = 'server'
            self.print_board()
            return pokemonou_pb2.move_response(success=1)

    def list_pokemon(self, request, context):
        return pokemonou_pb2.captured_pokemon(pokemon_name=list(self.pokedex[request.hostname].keys()))

    def list_trainer(self, request, context):
        hostname = request.hostname
        for key, value in self.pokedex.items():
            if (hostname in value):
                return pokemonou_pb2.trainer_info(trainer_name=key, pos = list(value[hostname]))
            
        return pokemonou_pb2.trainer_info(trainer_name='None', pos = [-1]) 
  
    def path(self, request, context):
        hostname = request.hostname
        #return pokemonou_pb2.path_info(path=self.path[hostname])
        return pokemonou_pb2.path_info(pos='position')
    
    def print_board(self):
        # load config file
        parser = configparser.ConfigParser()
        parser.read('config.ini')
        for i in range(self.b):
            for j in range(self.b):
                if(self.board[(i, j)]['trainer'] != ''):
                    print('|',parser['trainer'][self.board[(i, j)]['trainer']], end = '|')
                elif(self.board[(i, j)]['pokemon'] != []):
                    print('|', parser['pokemon'][self.board[(i, j)]['pokemon'][0]], end = '|')
                else:
                    print('|__|', end = ' ')
            print()

def serve():        
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=15))
    pokemonou_pb2_grpc.add_PokemonouServicer_to_server(Pokemonou(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
    server.stop()

async def trainer():
    #global pokedex
    async with grpc.aio.insecure_channel('server:50051') as channel:
        flag = 1
        hostname = socket.gethostname()
        while(flag > 0):
            stub = pokemonou_pb2_grpc.PokemonouStub(channel)
            # request to get its position
            response = await stub.check_board(pokemonou_pb2.name(hostname=socket.gethostname()),wait_for_ready=True)
            flag = response.pokemon_left
            x = response.current_position[0]
            y = response.current_position[1]
            moves = [[x - 1, y - 1], [x - 1, y], [x - 1, y + 1], [x, y - 1], [x, y + 1], [x + 1, y - 1], [x + 1, y], [x + 1, y + 1]]
            toCapture = 0
            if flag:
                if 1 in response.x:
                    available_moves = [i for i, j in enumerate(response.x) if j == 1]
                    index = random.choice(available_moves)
                    toCapture = 1
                elif 0 in response.x:
                    available_moves = [i for i, j in enumerate(response.x) if j == 0]
                    index = random.choice(available_moves)
                status = await stub.move(pokemonou_pb2.move_position(cur_x = x, cur_y = y, newx = moves[index][0], newy = moves[index][1], hostname=socket.gethostname(), toCapture=toCapture),wait_for_ready=True)
                if status.success == 1:
                    print("I made a move.")
            #else: # print list of pokemons that trainer capture before the game exit
                #pokemon_captured = await stub.list_pokemon(pokemonou_pb2.name(hostname=socket.gethostname()))
                #print('list of pokemone captured: ',pokemon_captured.pokemon_name)
                #path = await stub.path(pokemonou_pb2.name(hostname=hostname))
                #print('my path: ', path.pos)
                
async def pokemon():
    async with grpc.aio.insecure_channel('server:50051') as channel:
        alive = 1
        hostname = socket.gethostname()
        while(alive > 0):
            stub = pokemonou_pb2_grpc.PokemonouStub(channel)
            # request to get its position
            response = await stub.check_board(pokemonou_pb2.name(hostname=hostname),wait_for_ready=True)
            alive = response.alive
            x = response.current_position[0]
            y = response.current_position[1]
            moves = [[x - 1, y - 1], [x - 1, y], [x - 1, y + 1], [x, y - 1], [x, y + 1], [x + 1, y - 1], [x + 1, y], [x + 1, y + 1]]
            toCapture = 0
            
            #if alive:
            if 1 in response.x:
                available_moves = [i for i, j in enumerate(response.x) if j == 1]
                index = random.choice(available_moves)
                status = await stub.move(pokemonou_pb2.move_position(cur_x = x, cur_y = y, newx = moves[index][0], newy = moves[index][1], hostname=hostname, toCapture=toCapture),wait_for_ready=True)
            else:
                status = await stub.move(pokemonou_pb2.move_position(cur_x = x, cur_y = y, newx = x, newy = y, hostname=hostname, toCapture=toCapture),wait_for_ready=True)
        
            if status.success == 1:
                print("I made a move.")  
                
            if not alive:
                info = await stub.list_trainer(pokemonou_pb2.name(hostname=hostname), wait_for_ready=True)
                if info.pos != [-1]:
                    print(f'Captured by {info.trainer_name} at position {tuple(info.pos)}') 
                #path = await stub.path(pokemonou_pb2.name(hostname=hostname))
                #print('my path: ', path.pos) 
                  
if __name__ == "__main__":
    if(socket.gethostname() == 'server'):
        serve()
    elif('trainer' in socket.gethostname()):
        asyncio.run(trainer())
    else:
        asyncio.run(pokemon())