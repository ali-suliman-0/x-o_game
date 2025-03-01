import random
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class game:
    def __init__(self):
        self.wins_x = 0
        self.wins_o = 0
        self.player_x_token = str(uuid.uuid4())
        self.player_o_token = str(uuid.uuid4())
        self.join_player_o = False
        self.squares = {
        'square 1': '', 'square 2': '', 'square 3': '',
        'square 4': '', 'square 5': '', 'square 6': '',
        'square 7': '', 'square 8': '', 'square 9': ''
         }
        # إضافة متغير جديد لحالة اللعبة
        self.game_active = True
        self.player_role = self.__random_player()
        
    def __random_player(self):
        if random.randint(1,100) <= 50:
            return 'x'
        else:
            return 'o'
            
        
        
    def __Validation(self):
        
        lines = [

        ['square 1', 'square 2', 'square 3'],
        ['square 4', 'square 5', 'square 6'],
        ['square 7', 'square 8', 'square 9'],

        ['square 1', 'square 4', 'square 7'],
        ['square 2', 'square 5', 'square 8'],
        ['square 3', 'square 6', 'square 9'],

        ['square 1', 'square 5', 'square 9'],
        ['square 3', 'square 5', 'square 7']
    ]
        for line in lines:
            values = [self.squares[cell] for cell in line]
            if len(set(values)) == 1 and values[0] != '':
                return values[0]
    

        if all(self.squares.values()):
             return 'draw'
     
        return None
    
    def get_squares(self):
        return self.squares
    
    def get_player_x_token(self):
        return self.player_x_token
    
    def get_player_o_token(self):
        return self.player_o_token
    
    def get_player_role(self):
        return self.player_role
    
    def get_validation(self):
        return self.__Validation()
    
    def get_wins_player(self,player):
        if player == 'x':
            return self.wins_x
        elif player == 'o':
            return self.wins_o
    
    def join_player_o_token(self):
        if not self.join_player_o:
            self.join_player_o = True
            return self.player_o_token
        return None
        
    def set_square(self,token,square_number):
        # فحص ما إذا كانت اللعبة لا تزال نشطة
        if not self.game_active:
            return False
            
        if self.join_player_o:
            if self.__Validation() == None:
                if token == self.player_x_token:
                    if self.player_role == 'x':
                        if self.squares[f'square {square_number}'] == '':
                            self.player_role = 'o'
                            self.squares[f'square {square_number}'] = 'x'
                            return True
                            
                elif token == self.player_o_token:
                    if self.player_role == 'o':
                        if self.squares[f'square {square_number}'] == '':
                            self.player_role = 'x'
                            self.squares[f'square {square_number}'] = 'o'
                            return True
        return False
                            
    def add_win(self,player_win):
        if 'x' == player_win:
            self.wins_x = self.wins_x + 1
        elif 'o' == player_win:
            self.wins_o = self.wins_o + 1
                            
    def reset_squares(self):
        self.squares = {
        'square 1': '', 'square 2': '', 'square 3': '',
        'square 4': '', 'square 5': '', 'square 6': '',
        'square 7': '', 'square 8': '', 'square 9': ''
        }
    
    def update(self):
        if self.get_validation() == 'x':
            self.reset_squares()
            self.add_win('x')
        elif self.get_validation() == 'o':
            self.reset_squares()
            self.add_win('o')
        elif self.get_validation() == 'draw':
            self.reset_squares()
            
    # دالة جديدة لإنهاء اللعبة
    def end_game(self):
        self.game_active = False
        return {
            'squares': self.get_squares(),
            'wins x': self.get_wins_player('x'),
            'wins o': self.get_wins_player('o'),
            'final result': self.get_validation()
        }
    
    # دالة جديدة للتحقق مما إذا كانت اللعبة نشطة
    def is_active(self):
        return self.game_active
        
    
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)

games = {}
@app.post('/new-game')
async def new_game():
    id_game = random.randint(100,999)
    games[id_game] = game()
    return {'id game':id_game,'token player x':games[id_game].get_player_x_token()}
    
@app.put('/join/{id_game}')
def join(id_game):
    for key,value in games.items():
        if int(id_game) == key:
            # التحقق من أن اللعبة لا تزال نشطة
            if not value.is_active():
                return {'message': 'اللعبة منتهية'}
                
            player_o_token = value.join_player_o_token()
            if player_o_token != None :
                return {'id game':key,'token player o':player_o_token}

@app.put('/player-move/{id_game}/{token}/{square_number}')          
def player_move(id_game,token,square_number):
        for key,value in games.items():
            if key == int(id_game):
                # التحقق من أن اللعبة لا تزال نشطة
                if not value.is_active():
                    return {'message': 'اللعبة منتهية'}
                    
                value.update()
                if token == value.get_player_x_token():
                    if value.get_squares()[f'square {square_number}'] == '':
                        if value.get_player_role() == 'x':
                            result = value.set_square(token,square_number)
                            if result:
                                return {'message': 'تم تنفيذ الحركة بنجاح'}
                elif token == value.get_player_o_token():
                    if value.get_squares()[f'square {square_number}'] == '':
                        if value.get_player_role() == 'o':
                            result = value.set_square(token,square_number)
                            if result:
                                return {'message': 'تم تنفيذ الحركة بنجاح'}
                return {'message': 'لم يتم تنفيذ الحركة'}

@app.get('/data-game/{id_game}')
def data_game(id_game):
    for key,value in games.items():
        if key == int(id_game):
            value.update()
            return {
                'squares' : value.get_squares(),
                'player role': value.get_player_role(),
                'validation' : value.get_validation(),
                'wins x' : value.get_wins_player('x'),
                'wins o' : value.get_wins_player('o'),
                'game active': value.is_active()
            }


@app.put('/end-game/{id_game}/{token}')
def end_game(id_game, token):
    for key, value in games.items():
        if key == int(id_game):

            if token == value.get_player_x_token() or token == value.get_player_o_token():
                final_data = value.end_game()
                return {
                    'final data': final_data
                }