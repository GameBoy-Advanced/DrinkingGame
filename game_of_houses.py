from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from collections import OrderedDict
from kivy.animation import Animation
from kivy.clock import Clock
from functools import partial
from kivy.core.audio import SoundLoader


class MiniGame(BoxLayout):
    title=ObjectProperty("House Of Games")
    active_player=ObjectProperty(None)
    gamebox=ObjectProperty(None)
    gamepoint=1

    def __init__(self,players=None,**kw):
        super().__init__(**kw)

        if not players:
            players=["jaakko", "pekka"]
        self.state="start"
        self.players=players
        self.no_of_players=len(players)
        self._keyboard=Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)
        self.scores=dict((player,0) for player in self.players)
        print(self.scores)
        games = [
            NewSmashGame
        ]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self,value):
        print(value)
        self._state=value

    def next(self):
        if self.state=="start":
            self.state="closed"
            self.gamebox.game=NewSmashGame()
        if self.state=="game_end":
            self.gamebox.game.next()


    def pause(self):
        if self.state=="paused":
            self.state=str(self.old_state)
            self.gamebox.game.unpause()
        else:
            self.old_state=str(self.state)

            self.state="paused"
            self.gamebox.game.pause()

    def resume(self):

        self.gamebox.game.unpause()

    def _keyboard_closed(self):
        pass

    def _on_keyboard_up(self,keyboard,keycode,*args):
        if keycode[1]=="enter":
            return self.next()
        if keycode[1]=="spacebar":
            return self.pause()
        if keycode[1]=="y":
            return self.correct()
        if keycode[1]=="n":
            return self.incorrect()

        if keycode[1] in [str(i) for i in range(self.no_of_players)]:
            return self.player_button(int(keycode[1]))

    def player_button(self,button_number,*args):

        if self.state=="open" or self.state=="open_"+str(button_number):
            self.pause()
            self.state="answer"
            self.active_player=self.players[button_number]

    def correct(self):
        correct_sound = SoundLoader.load("GameOfHousesThings/sounds/correct.wav")
        Clock.schedule_once(lambda a:correct_sound.play())
        self.correct_sound=SoundLoader.load("")
        if self.state=="answer":
            self.scores[self.active_player]+=self.gamepoint
            self.gamebox.game.reveal()
        self.active_player=""

    def incorrect(self):

        incorrect_sound = SoundLoader.load("GameOfHousesThings/sounds/incorrect.wav")
        incorrect_sound.play()

        if self.state=="answer":
            self.resume()

        self.active_player=""



class NewSmashGame(BoxLayout):

    first_word=ObjectProperty("")
    second_word=ObjectProperty("")
    third_word=ObjectProperty("")
    title=ObjectProperty("Väkisinmakuupussi")
    description=ObjectProperty("")

    fw_opacity=ObjectProperty(0)
    sw_opacity=ObjectProperty(0)
    tw_opacity=ObjectProperty(0)
    d_opacity=ObjectProperty(0)

    def __init__(self,**kw):
        super().__init__(**kw)
        pad_y=max(0,(self.height-700)/2)
        pad_x=max(0,(self.width-1200)/2)
        self.padding=[pad_x,pad_y,pad_x,pad_y]
        with open("GameOfHousesThings/new_smash","r",encoding="UTF-8") as file:
            data=file.read().split("#")[0].split("\n")

        exname="Kategoria"
        self.rounds=OrderedDict()
        self.rounds[exname]=[data[1].split(";")]
        for i in range((len(data)-3)//6):
            i+=3
            name=data[i]
            rounds=[]
            for o in range(1,5):
                rounds.append([*data[i+o].split(";")])
            self.rounds[name]=rounds

        self.current_category=None
        self.round_number=0
        self.trigs=[]

        self.next_category()
        self.next()

    @property
    def words(self):
        return self.first_word,self.second_word,self.third_word
    @words.setter
    def words(self,value):
        self.first_word,self.second_word,self.third_word=value

    def next_category(self):
        self.current_category=self.rounds.popitem(last=False)
        self.title=self.current_category[0]

    def next(self):

        if len(self.current_category[1])==0:
            self.next_category()

        Animation(d_opacity=0).start(self)
        Animation(fw_opacity=0).start(self)
        Animation(tw_opacity=0).start(self)
        Animation(sw_opacity=0).start(self)

        Clock.schedule_once(self.begin_round,2)






    def begin_round(self,*a):
        info=self.current_category[1].pop(0)

        self.words=info[0].split(",")
        self.description=info[1]

        show_desc=partial(Animation(d_opacity=1).start,self)
        show_1=partial(Animation(fw_opacity=1).start,self)
        show_2=partial(Animation(sw_opacity=1).start,self)
        show_3=partial(Animation(tw_opacity=1).start,self)
        Clock.schedule_once(lambda a:setattr(self.parent.parent,"state","open"))
        self.trigs=[
        Clock.schedule_once(lambda a:show_desc(),3),
        Clock.schedule_once(lambda a:show_1(),7),
        Clock.schedule_once(lambda a:show_3(),11)
        ]


    def pause(self):

        #list(lambda a: Animation(**{i:1}).start(self) for i in filter(lambda a:getattr(self,a)==0,["d_opacity","fw_opacity","tw_opacity"]))
        #dicts=[{i:1} for i in filter(lambda a:getattr(self,a)==0,["d_opacity","fw_opacity","tw_opacity"])]
        #anims =list((lambda a:Animation(**i).start(self)) for i in dicts)
        #[print({i:1}) for i in filter(lambda a:getattr(self,a)==0,["d_opacity","fw_opacity","tw_opacity"])]
        anims=[]
        if self.d_opacity==0:
            anims.append(lambda a:Animation(d_opacity=1).start(self))
        if self.fw_opacity==0:
            anims.append(lambda a:Animation(fw_opacity=1).start(self))
        if  self.tw_opacity==0:
            anims.append(lambda a:Animation(tw_opacity=1).start(self))

        for i in self.trigs:
            i.cancel()

        self.unpause=lambda: setattr(self,"trigs",[Clock.schedule_once(i,2+(pos*4)) for pos,i in enumerate(anims)])

    def reveal(self):

        anims=[
            lambda a: (Animation(fw_opacity=.5,d=.25)+Animation(fw_opacity=1)).start(self),
            lambda a: (Animation(tw_opacity=.5,d=.25)+Animation(tw_opacity=1)).start(self),
            lambda a: (Animation(sw_opacity=.5,d=.25)+Animation(sw_opacity=1)).start(self)
        ]

        for pos,i in enumerate(anims):
            Clock.schedule_once(i,pos/4)

        self.parent.parent.state="game_end"

class GameBox(BoxLayout):

    _game=ObjectProperty(None)

    def __init__(self,**kw):
        super().__init__(**kw)
        self.bind(parent=self.hook)

    def hook(self,*args):
        self.parent.gamebox=self

    @property
    def game(self):
        return self._game

    @game.setter
    def game(self,value):
        if self.game is not None:
            self.remove_widget(self.game)

        self.add_widget(value)
        self._game=value

class ActivePlayer(Label):
    pass
class GameName(Label):
    pass

class GameOfHousesApp(App):
    pass

class AnswerSmashGame(BoxLayout):

    pass

GameOfHousesApp().run()