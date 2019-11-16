import os
import time

import spotipy
import spotipy.util as util
if False:
    username = "osteha"
    scope = "user-modify-playback-state"
    client = "8a04f930f4c34b3e9be7280ae09a02ba"
    secret = "194f9fbcb9044e92ba28462d8c69b59d"
    token = util.prompt_for_user_token(username, scope, client_id=client, client_secret=secret,
                                   redirect_uri="http://localhost/")
#os.environ["KIVY-AUDIO"]="sdl2"
#os.environ["SDL_AUDIODRIVER"]="alsa"
from kivy.config import Config
Config.set("input","mouse","mouse,multitouch_on_demand")

from kivy.core.audio import SoundLoader
from kivy.app import App,Builder
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.video import Video
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen,FallOutTransition,FadeTransition
from configparser import ConfigParser
import random
from functools import partial
from kivy.animation import Animation
from HorsePlay import HorseGame
from MiniGames import MiniGames




def nothing(*args):
    print("NOTHING",args)




class Game:

    minigames=MiniGames

    rule_in_anim=Animation(x=1920//2-200,d=.5,t="out_quint")
    rule_out_anim=Animation(x=1920//2+100,d=.5,t="in_quint")

    video_out=Animation(opacity=0,d=.5)
    video_in=Animation(opacity=1,d=.5)


    def __init__(self,screen):
        self.screen=screen
        self.spotify=self.screen.app.spotify
        self.length=screen.game_length
        self.players=screen.player_count
        self._round=0
        self._gamestate="running"
        self.enter_time=0
        self.rounds=self.get_rounds()
        self.video=self.get_video(path="Countdowns_10",is_random=True)
        self.game_widget=None

        self.actions=[["t",{"description":"a","action":"minigame horseplay_5_horses","drinking":"sa","type":"asdas"}],
                      ["Test",{"description":"asd","action":"random cards,random cards paused","drinking":"s","type":"s"}]]

        #[["t",{"description":"a","action":"minigame horseplay_5_horses","drinking":"sa","type":"asdas"}] for i in range(10)]

        self.actions=[]


        self.video_end_action="next"
        self.skipped=False
        self.winner=random.randint(1,self.players)
        self._queue=[]
        self._rules=[]

    @property
    def gamestate(self):
        return self._gamestate

    @gamestate.setter
    def gamestate(self,value):
        print("STATE:",value)
        if value == "running" and any(i in self.video.source for i in [".jpg",".png"]):
            value="ready"
        self._gamestate=value

    def minigame_end(self,*args,**kwargs):
        self.gamestate="ready"

    def get_video(self, path=None, is_random=False, paused=False, eos="stop", player=None,volume=0):
        path = "Videos/" + path
        if is_random:
            files = os.listdir(path)
            video_path = path + "/" + random.choice(files)
        else:
            print(path)
            video_path = path

        if player is not None:

            player.source=video_path
            player.state="stop" if paused else "play"
            player.eos=eos
            player.volume=volume

            return player

        s = {
            "source": video_path,
            "state": "stop" if paused else "play",
            "options": {"allow_stretch": True},
            "volume":volume,
            "size":self.screen.size,
            "eos":eos
        }

        player = Video(**s)
        player.bind(on_eos=self.on_video_end)
        return player


    @property
    def round(self):
        return self._round

    @round.setter
    def round(self,value):
        self._round=value

        if self.round>self.length:
            self.end()

        else:
            self.screen.top_label.text=f"Round {self.round} of {self.length}.{' '*400} {self.players} players playing the game"

        self.check_queue()

    def on_enter(self,direction):
        if direction=="up":
            print("Enter")
        if self.gamestate==" ":
            raise Exception
        if direction=="down" and self.enter_time == 0:
            self.enter_time=time.time()
        elif self.skipped and direction=="up":
            self.skipped=False
        elif self.skipped:
            pass
        elif time.time() - self.enter_time > 2:
            self.enter_time=0
            self.skipped=True
            self.next()

        elif direction=="up":
            if self.gamestate in ["ready","waiting"]:
                self.next()
            self.enter_time=0

    def on_video_end(self,*args):
        print("VIDEO END")
        if self.video_end_action=="ready":
            self.video_end_action="none"
            self.ready()
        elif self.video_end_action=="next":
            self.video_end_action="none"
            self.next()

    def get_rounds(self):

        parser = ConfigParser()
        files = ["Rounds/"+i for i in os.listdir("Rounds")]
        parser.read(files)
        rounds=[]

        if len(parser)==self.length:
            round_names=parser.sections()

        elif len(parser)>self.length:
            round_names=random.sample(parser.sections(),k=self.length)

        else:
            round_names=[]
            for i in range(self.length//(len(parser)-1)):
                round_names+=random.sample(parser.sections(),k=len(parser)-1)
            round_names+=random.sample(parser.sections(),k=self.length%len(parser))

        random.shuffle(round_names)

        for i in round_names:
            rounds.append([i,dict(parser[i])])

        return rounds

    def ready(self):
        print("READY() CALLED")
        self.gamestate="ready"
        self.spotify.play()


    def next(self,*args):

        if self.gamestate=="waiting":
            if self.game_widget:
                self.game_widget.play()
            else:
                self.video.unload()
                self.play_video()
            self.gamestate="running"
            self.skipped=True
            return

        if self.game_widget:
            self.screen.minigame.remove_widget(self.game_widget)
            self.game_widget=None


        if self.actions:
            n,d=self.actions.pop(0)

        else:
            self.round+=1
            n,d=self.rounds.pop(0)

        r=Action(self,n,**d)

        t=f"[size=80][b]{r.name}[/b][/size]"
        d=f"[size=50]{r.description}[/size]"
        self.change_card(t,d)

    def end(self):
        self.rounds.append(["THE [color=FF581A]GREAT[/color] END",
                            {
                                "description":f"The game is at an end. Rejoice. Player {self.winner} won.",
                                "drinking":"none",
                                "action":"none",
                                "type":"end"
                            }])

    def queue(self,number,function):
        self._queue.append((self.round+number,function))

    def check_queue(self):
        for i in self._queue.copy():
            if i[0]==self.round:
                self._queue.remove(i)
                i[1]()

    def add_rule(self,name,color_name):

        rules = self.screen.rules
        colors={
            "red":"ff4e41",
            "blue":"2290ad"
        }

        color=colors[color_name]
        w = Label(text=f"[size=25][b][color={color}][{name}][/color][/b][/size]",
                  markup=True,
                  outline_width=1,
                  pos=(1920//2+200,1080//2-100-(len(self._rules))*50)

                  )

        self._rules.append(w)
        self.rule_in_anim.start(w)
        rules.add_widget(w, index=1)

    def change_card(self,title,description):

        t_in = Animation(y=1080 // 2 - 250, d=.2, t="out_quint")
        t_out = Animation(y=1080 // 2 , d=.2, t="in_quint")

        d_in = Animation(y=-150, d=.2, t="out_quint")
        d_out = Animation(y=-1080 // 2+100, d=.2, t="in_quint")

        t=self.screen.title
        d=self.screen.desc

        t_out.start(t)
        d_out.start(d)

        f=lambda a,b : [setattr(t,"text",title),setattr(d,"text",description),t_in.start(t),d_in.start(d)]

        t_out.bind(on_complete=f)

    def remove_rule(self,name):
        for label in self.screen.rules.children:
            if name in label.text:
                self.rule_out_anim.start(label)
                f = lambda a, b: partial(self.screen.rules.remove_widget,label)()
                self.rule_out_anim.bind(on_complete=f)
                self._rules.remove(label)

                for pos,rule in enumerate(self._rules):
                    anim=Animation(y=1080 // 2 - 100 - pos * 50,x=1920//2-200,d=.6,t="in_out_quint")
                    anim.start(rule)
                break
        else:
            print(f"TRIED TO REMOVE RULE: {name}, but could not find it in rules")
            print("RULES: ",*[i.text for i in self.screen.rules.children])


class PlayScreen(Screen):

    def __init__(self,app,player_count,game_length,**kwargs):

        super().__init__(**kwargs)
        self.app=app
        self._keyboard=Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_up=self._on_keyboard_up,on_key_down=self._on_keyboard_down)

        self.player_count=player_count
        self.game_length=game_length*5
        self.game=Game(self)

        self.video=self.game.video
        self.vid_sm=ScreenManager()
        self.vid_sm.transition=FadeTransition()
        self.vid_screen=Screen()
        self.vid_screen.add_widget(self.video)
        self.vid_sm.add_widget(self.vid_screen)

        self.top_label= Label(text=f"Round {self.game.round} of {self.game_length}.{' '*400} {self.player_count} players playing the game",
                              pos_hint={"y":.48},
                              outline_width=1
                              )

        self.title=Label(text="[size=80][b]THE [color=FF581A]GREAT[/color] DRINKING GAME[/b][/size]",
                         y=1080//2-250,
                         text_size=(1800, 400),
                         valign="top",
                         halign="center",
                         markup=True,
                         outline_width=1
                         )

        self.desc = Label(text="",
                          markup=True,
                          text_size= (1800,600),
                          y=-50,
                          outline_width=1,
                          halign="center",
                          valign="bottom"
                          )


        self.rules= FloatLayout()

        mg = self.minigame = RelativeLayout(size=(1600, 600))


        self.add_widget(self.vid_sm)
        self.add_widget(mg)
        self.add_widget(self.top_label)
        self.add_widget(self.rules)
        self.add_widget(self.title)
        self.add_widget(self.desc)
        self.bind(size=self.center_things)

    def center_things(self,*args):
        return
        self.minigame.center = self.center


    def _keyboard_closed(self):
        print('My keyboard has been closed!')
        self._keyboard.unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_up(self,keyboard, keycode,*_):
        if keycode[1]=="enter":
            self.game.on_enter("up")

    def _on_keyboard_down(self,keyboard, keycode,*_):
        if keycode[1]=="enter":
            self.game.on_enter("down")


class Action:

    def __init__(self,game,name,*,description,action,type,drinking):
        print(name)
        self.game=game
        self.name=name
        self._d={"description":description,"action":action,"type":type,"drinking":drinking}

        try:
            self.description = self.read_description(description)
        except Exception:
            self.description = description

        self.type = type.split(",")

        for i in self.type:
            if i=="rule":
                self.game.add_rule(self.name,"blue")
            elif "rule_" in i:
                self.game.add_rule(self.name,"red")
                self.game.queue(int(i.split("_")[1]),partial(self.game.remove_rule,self.name))

        self.drinking=drinking
        self.game.gamestate="running"

        acts=action.split(",")
        self.game.video.unload()
        for command in acts:
            self.run_command(command)



    def run_command(self,string,r=False):

        def get_rounds(r_filename=None,r_folder=None,r_rulename=None,r_random=False,*,r_amount):
            parser = ConfigParser()
            if r_folder is None or r_folder=="x":
                files = ["Rounds/" + i for i in os.listdir("Rounds")]
            else:
                files = [f"Rounds/{r_folder}/" + i for i in os.listdir(f"Rounds/{r_folder}")]

            if r_filename is not None and r_filename!="x":
                files = list(filter(lambda a:a.split("/")[-1]==r_filename+".ini",files))

            parser.read(files)
            rounds = []

            if r_rulename is not None and r_rulename!="x":
                sections=list(filter(lambda a:a==r_rulename,parser.sections()))
            else:
                sections=parser.sections()

            if r_amount=="all":
                r_amount=len(sections)
            else:
                r_amount=int(r_amount)

            if len(sections) == r_amount:
                round_names = sections

            elif len(sections) > r_amount:
                round_names = random.sample(sections, k=r_amount)

            else:
                round_names = []
                for i in range(r_amount // (len(sections))):
                    round_names += sections
                round_names += random.sample(parser.sections(), k=r_amount % len(parser))
            if r_random:
                random.shuffle(round_names)

            for i in round_names:
                rounds.append([i, dict(parser[i])])

            return rounds

        game=self.game
        command=string.split(" ")

        if command[0].capitalize() in ["Random","Play","None"]:
            screen = Screen()

        if command[0] == "random":
            r = True
            self.game.spotify.pause()
            if len(command) == 3 and command[2] == "paused":
                self.game.gamestate = "waiting"
                self.game.play_video = partial(game.get_video, is_random=r, path=command[1],volume=1,player=self.game.video)
                self.game.video_end_action="none"
            else:
                game.get_video(is_random=r, path=command[1],volume=1,player=self.game.video)
                self.game.video_end_action="ready"

        elif command[0].capitalize() == "Play":
            try:
                self.game.video.unload()
                game.get_video(path="other/" + command[1],volume=1,player=self.game.video)
                self.game.video_end_action="ready"

            except Exception:
                command[0] = "none"

        elif command[0]=="play_spotify":
            self.game.spotify.play(song=command[1])

        elif command[0].capitalize() == "None":
            self.game.ready()
            self.game.video.unload()
            game.get_video(is_random=True, path="Backgrounds", eos="loop",player=self.game.video)
            self.game.video_end_action = "none"


        elif command[0]=="loop":
            amount = int(command[1])
            d=dict(self._d)
            act=d["action"].split(",").copy()
            act.remove(" ".join(command))
            d["action"]=",".join(act)

            self.game.actions += [(self.name,d) for _ in range(amount)]

        elif command[0]=="queue":
            if command[1]=="cards":
                amount=command[2]
                delay=int(command[3]) if command[3]!="r" else "r"
                if len(command)>=5:
                    L=command[4].split("/")
                    folder=L[0]
                    file=L[1]
                    name=L[2].replace("+"," ")
                else:
                    folder,file,name=None,None,None
                if len(command)==6 and command[5]=="random":
                    rand=True
                else:
                    rand=False

                rounds=get_rounds(r_filename=file,r_folder=folder,r_rulename=name,r_amount=amount,r_random=rand)

                for i in reversed(rounds):
                    if delay=="r":
                        d=random.randint(0,len(self.game.rounds)-1)
                    else:
                        d=delay
                    self.game.rounds.insert(d,i)

        elif command[0]=="minigame":
            if command[1] in game.minigames:
                game.game_widget=game.minigames[command[1]](game.players)
                game.screen.minigame.add_widget(game.game_widget)
                game.gamestate="waiting"
                game.game_widget.bind(finished=game.minigame_end)
                self.game.video_end_action = "none"

        if command[0].capitalize() in ["Random", "Play", "None"]:
            self.new_screen=screen

    def read_description(self,description):

        for word in description.split(" "):
            if len(word)>0 and word[0]=="@":
                command=word.replace("@","").lower().split("_")

                if command[0]=="random":
                    if command[1]=="player":
                        new_word=f"{random.randint(1,self.game.players)}"

                    elif command[1]=="players":
                        l=[i+1 for i in range(self.game.players)]
                        new_word=f"{random.sample(l,k=int(command[2]))}"


                    elif command[1]=="direction":
                        _words=['in an ascending order by player number',
                                'in a descending order by player number']
                        new_word=f"{random.choice(_words)}"

                    elif command[1]=="number":
                        s,e=(int(i) for i in command[2:4])
                        new_word=f"{random.randint(s,e)}"

                    elif command[1]=="choice":
                        new_word=f"{random.choice(command[2:])}"

                    new_word=new_word.replace("+"," ")

                description=description.replace(word,new_word)

        return description

class StartScreen(Screen):
    player_count=1
    game_length=1

    def __init__(self,app,**kwargs):
        super().__init__(**kwargs)

        self.app=app

        self.main_box = BoxLayout(orientation="vertical",spacing=10)
        self.vid_box = BoxLayout(orientation="vertical",spacing=0,size_hint=(1,.8))
        g=Game(self)
        g.video.unload()
        self.video=g.get_video(path="other/nyan.mp4",volume=1)

        self.controls_box=BoxLayout(orientation="horizontal",spacing=20,size_hint=(1,.04))

        self.add_button= Button(text= f"Players: {self.player_count}", on_press = self.player_pressed)
        self.length_button= Button(text= f"Length: {self.game_length}", on_press = self.length_pressed)
        self.play_button= Button(text= "Play", on_press = self.play)

        self.vid_box.add_widget(self.video)
        self.main_box.add_widget(self.vid_box)
        self.main_box.add_widget(self.controls_box)
        self.controls_box.add_widget(self.add_button)
        self.controls_box.add_widget(self.length_button)
        self.controls_box.add_widget(self.play_button)

        self.add_widget(self.main_box)

    def length_pressed(self,instance):
        self.game_length+=1
        instance.text=f"Length: {self.game_length}"

    def player_pressed(self,instance):
        self.player_count+=1
        instance.text=f"Players: {self.player_count}"

    def play(self,instance):
        self.video.state="stop"
        self.video.unload()
        self.manager.switch_to(PlayScreen(self.app,self.player_count,self.game_length))


class SpotifyController:

    def __init__(self,token):
        return

        self.sp = spotipy.Spotify(auth=token, requests_session=True)
        if self.sp.current_playback() is None:
            input("ACTIVATE SPOTIFY TO CONTINUE AND THEN ENTER")
        else:
            print("SPOTIFY ACTIVE")

    def play(self,song=None,offset=None):
        return
        print(song,offset)
        if song is not None:
            if song.__class__ is list:
                self.sp.start_playback(uris=song)
            elif offset is not None:
                self.sp.start_playback(context_uri=song,offset=offset)
            else:
                self.sp.start_playback(context_uri=song)
        elif not self.sp.current_playback()["is_playing"]:
            self.sp.start_playback()

    def pause(self):
        return
        if self.sp.current_playback()["is_playing"]:
            self.sp.pause_playback()

spotify=SpotifyController(None)


class DrinkApp(App):

    def build(self):
        self.spotify=spotify
        sm = ScreenManager()
        sm.add_widget(StartScreen(self,name="start"))
        sm.transition = FadeTransition()

        return sm

DrinkApp().run()