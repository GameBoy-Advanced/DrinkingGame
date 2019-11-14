from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.graphics import Line,Rectangle
from kivy.properties import ObjectProperty
from kivy.app import App
from functools import partial,reduce
from random import choice
from kivy.clock import Clock
from math import sqrt


class CombatArenaGame(RelativeLayout):

    def __init__(self,team1,team2,match_style="duel",round_time=2,**kwargs):
        super().__init__(**kwargs)
        self.grid=GridLayout(cols = 8,rows = 5)
        self.tiles=[[Tile((x,y)) for y in range(self.grid.rows)] for x in range(self.grid.cols)]
        for col in self.tiles:
            for tile in col:
                self.grid.add_widget(tile)

        self.add_widget(self.grid)
        self.add_widget(TileLines(self))
        self.team1,self.team2=[],[]
        self.flatgrid=reduce(lambda a,b:a+b,self.tiles)
        empty_tiles=list(self.flatgrid)
        for team,team_names in zip((self.team1,self.team2),(team1,team2)):
            for mobster_name in team_names:
                tile=choice(empty_tiles)
                empty_tiles.remove(tile)
                team.append(mobsters[mobster_name](tile))

        self.turn=0

    def do_turn(self):



        distance=lambda x,y,fx,fy: sqrt((x-fx)**2+(y-fy)**2)

        def attack(amob):
            x,y=pos=amob.tile.grid_position

            t=list(filter(lambda a: a.mobster is not None and
                                    distance(x,y,*a.grid_position)<=a.attack_range and
                                    a != amob,
                          self.flatgrid))

            if len(t)!=0:
                return choice(t)




        if self.turn//2==0:
            team=self.team1
        else:
            team=self.team2

        mob=team.pop(0)



class TileLines(Widget):

    def __init__(self,minigame,**kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            for i in range(minigame.grid.cols):
                pass


class Mobster(Widget):
    tile,attack,attack_range=(ObjectProperty(None) for _ in range(3))
    name=ObjectProperty("monster")

    animation_index=ObjectProperty(0)
    animation=ObjectProperty("idle")

    def __init__(self,hp,attack,tile,attack_range=1,name="monster",moves=3,**kwargs):
        super().__init__(**kwargs)
        self.tile=tile
        self.hp=hp
        self.attack=attack
        self.attack_range=attack_range
        self.name=name

        self.bind(size=self.align)

        tile.mobster=self

    def align(self,*args):
        if self.parent is not None:
            self.center=self.parent.center



mobsters={
    "warrior":partial(Mobster,10,2,attack_range=1,name="warrior"),

}

class Tile(RelativeLayout):
    _mobster=ObjectProperty(None)

    def __init__(self,grid_position,**kwargs):
        super().__init__(**kwargs)
        self.grid_position=grid_position

    @property
    def mobster(self):
        return self._mobster

    @mobster.setter
    def mobster(self,value):
        if self._mobster:
            self.remove_widget(self._mobster)

        self._mobster=value
        self.add_widget(value)




class MGTestApp(App):

    def build(self):
        return CombatArenaGame(["warrior"],["warrior"])


MGTestApp().run()