from kivy.app import App
from kivy.animation import Animation
from kivy.uix.relativelayout import RelativeLayout
class TestApp(App):
    pass

class MovingLayout(RelativeLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        Animation(x=500,y=500,d=5).start(self)

class AnotherMovingLayout(RelativeLayout):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        Animation(x=0,y=-500,d=10).start(self)

TestApp().run()