from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from random import randint,gauss
from kivy.app import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Line
from kivy.animation import Animation
from functools import partial

class Track(AnchorLayout):
    pass

class Horse(RelativeLayout):
    direction=ObjectProperty(None)

class HorseTrack(RelativeLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.horse_pos=0,0
        self.events=[]

    def load(self):
        self.horse=Horse()
        self.move_layout=RelativeLayout()
        self.animation_layout=RelativeLayout()

        self.add_widget(self.move_layout)
        self.move_layout.add_widget(self.animation_layout)
        self.animation_layout.add_widget(self.horse)
        self.make_events()
        self.next_anim()

    def next_anim(self,*args):
        print(self.horse.pos)
        self.events.pop(0)()

    def make_events(self,amount=30,random=20):
        times=amount#+randint(0,random)
        start=self.horse.pos[0]
        finish=self.horse.pos[0]
        diff=finish-start
        print(start,finish,"=",diff)
        base_time=30/times
        for i in range(times):
            base_x=i*100
            x=base_x+randint(-60,60)
            y=gauss(0,10)
            t=gauss(base_time,3)
            print(x,y)
            self.events.append(self.move_to(x,y,t))


    def move_to(self,x,y,t):
        anim=Animation(x=x,y=y,d=t,t="in_out_quint")
        anim.bind(on_complete=self.next_anim)
        return partial(anim.start,self.move_layout)





class HorseGame(BoxLayout):
    orientation = "vertical"
    def __init__(self,*,number_of_players=10,**kwargs):
        super().__init__(**kwargs)
        tracks = [HorseTrack() for _ in range(number_of_players)]
        #winner=tracks.pop(randint(0,len(tracks)-1))
        for track in tracks:
            self.add_widget(track)

        for track in tracks:
            track.load()




class HorseApp(App):
    pass


HorseApp().run()