from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from collections import OrderedDict
from kivy.animation import Animation
from kivy.clock import Clock
from functools import partial

class MiniGame(BoxLayout):
    title=ObjectProperty("House Of Games")
    active_player=ObjectProperty("")
    gamebox=ObjectProperty(None)

    def __init__(self,players=None,**kw):
        super().__init__(**kw)

        if not players:
            players=["jaakko", "pekka"]
        self.state="start"
        self.players=players
        self.no_of_players=len(players)
        self._keyboard=Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

        games = [
            NewSmashGame
        ]

    def next(self):
        if self.state=="start":
            self.gamebox.game=NewSmashGame()

    def pause(self):
        print("here",self.state)
        if self.state=="paused":
            self.state=self._state
            self.gamebox.game.unpause()
        else:
            self._state=self.state
            self.state="paused"
            self.gamebox.game.pause()


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
            return self.player_button(int(keycode))

    def player_button(self,button_number,*args):

        if self.state=="open" or self.state=="open_"+str(button_number):
            self.state="master"



class NewSmashGame(BoxLayout):

    first_word=ObjectProperty("")
    second_word=ObjectProperty("")
    third_word=ObjectProperty("")
    title=ObjectProperty("")
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
        with open("GameOfHousesThings/new_smash","r") as file:
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


    @property
    def words(self):
        return self.first_word,self.second_word,self.third_word
    @words.setter
    def words(self,value):
        self.first_word,self.second_word,self.third_word=value

    def next_category(self):
        self.current_category=self.rounds.popitem(last=False)
        self.title=self.current_category[0]
        self.next()

    def next(self):
        info=self.current_category[1].pop(0)

        self.words=info[0].split(",")
        self.description=info[1]

        show_desc=partial(Animation(d_opacity=1).start,self)
        show_1=partial(Animation(fw_opacity=1).start,self)
        show_2=partial(Animation(sw_opacity=1).start,self)
        show_3=partial(Animation(tw_opacity=1).start,self)
        self.trigs=[
        Clock.schedule_once(lambda a:show_desc(),1),
        Clock.schedule_once(lambda a:show_1(),5),
        Clock.schedule_once(lambda a:show_3(),9)
        ]



    def pause(self):

        anims=[]

        if self.d_opacity==0:
            anims.append(partial(Animation(d_opacity=1).start,self))
        if self.fw_opacity==0:
            anims.append(partial(Animation(fw_opacity=1).start,self))
        if  self.tw_opacity==0:
            anims.append(partial(Animation(tw_opacity=1).start,self))

        for i in self.trigs:
            i.cancel()

        self.trigs=[]


        for pos,i in enumerate(anims):
            Clock.schedule_once(lambda a:i(),2+pos)






class GameBox(BoxLayout):


    def __init__(self,**kw):
        super().__init__(**kw)
        self._game=None
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