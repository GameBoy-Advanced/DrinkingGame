from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line,Color
from kivy.animation import Animation
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from functools import partial
from random import gauss,random
from kivy.app import ObjectProperty

def make_special_part(number_of_args_passed):

    def inner(func,*args,**kwargs):
        passed_args=args[:number_of_args_passed]

        def even_inner(*inner_args,**kwargs):
            print(passed_args)
            return func(*passed_args)

        return even_inner

    return inner

part_3=make_special_part(3)
part_2=make_special_part(1)

class MiniGame:

    pass
class GoalLine(Widget):
    def __init__(self,points,**kwargs):
        super().__init__(**kwargs)
        self.points=points

class HorseGame(RelativeLayout):
    finished=ObjectProperty(False)
    def __init__(self,players,**kwargs):
        super().__init__(**kwargs)
        self.game=HorsePlay(players)
        self.add_widget(self.game)

    def play(self,*args,**kwargs):
        self.game.play()

class HorsePlay(BoxLayout):
    orientation = "vertical"
    padding = 200,200,200,200
    def __init__(self,players,**kwargs):

        super().__init__(**kwargs)
        self.players=players
        self.loaded=False
        self._finish_list=[]
        self.bind(size=self.load)

    def load(self,*args,**kwargs):
        print(self.width,"LOAD")
        if not self.loaded:
            self.loaded=True
            self.tracks=[HorseTrack(i+1) for i in range(self.players)]
            for track in self.tracks:
                self.add_widget(track)
        else:
            gl=self.goalline=int((self.width-200)*0.9)
            goalpoints=[gl,self.top,gl,self.y]
            self.add_widget(GoalLine(goalpoints))

    def play(self):
        self.get_moves()


    def finish(self,track):

        self.parent.finished=True
        self._finish_list.append(track)
        l=Label(text=f"[b][size=50]{len(self._finish_list)}[/size][/b]",markup=True,x=-100+self.width/2)
        #l.center_y=self.height/2
        track.add_widget(l)



    def get_moves(self,*args,amount=10,**kwargs):
        print(self.width,amount)
        width=self.width-400
        length=(width*0.9)-100
        move=length/amount

        for track in self.tracks:
            anims=[]
            times=[]

            y1 = 0
            y2 = 5

            pace=0.1+gauss(0,0.01)
            bobble_anim = Animation(y=y2, d=pace, t="out_circ") + Animation(y=y1, d=pace, t="in_circ")

            for i in range(amount):
                sigma=((1.5*i)/amount)
                duration=max(1,gauss(1.5,sigma))
                x_position=(i+1)*move
                t="in_out_quint"

                a=Animation(x=x_position,d=duration)
                anims.append(a)
                times.append(duration)

            anims.append(Animation(x=length+100,d=4,t="out_circ"))
            anims[-1].bind(on_start=part_2(self.finish,track))

            anim=Animation(d=.2)
            for i in anims:
                anim+=i

            anim.start(track.poslayout)

            bobble_anim.repeat=True

            bobble_anim.start(track.animlayout)


class AnimLayout(RelativeLayout):
    tn=ObjectProperty(0)

class PositionLayout(RelativeLayout):
    pass

class Horse(RelativeLayout):
    angle=0
    horse_size=50
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        colors=[max(0.3,random()) for _ in range(3)]
        self.color=(*colors,1)

class HorseNumber(RelativeLayout):
    tn=ObjectProperty(0)

class HorseTrack(RelativeLayout):


    def __init__(self,track_number,**kwargs):
        super().__init__(**kwargs)
        self.animlayout=AnimLayout()
        self.animlayout.tn=track_number
        self.poslayout=PositionLayout()
        self.horse=Horse()




        self.add_widget(Label())

        self.add_widget(self.poslayout)

        self.poslayout.add_widget(self.animlayout)
        self.poslayout.add_widget(HorseNumber(tn=track_number))
        self.animlayout.add_widget(self.horse)

        self.tn=track_number

        self.bind(size=self.load)

    def load(self,*args):
        self.add_widget(TrackGround(),index=10)


class TrackGround(Widget):
    pass

class TestGame(App):
    def build(self):
        return HorseGame(8,size=(1920,1080))


if __name__=="__main__":
    TestGame().run()