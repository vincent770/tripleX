import rumps

class Bar(rumps.App):
    def __init__(self, name, icon, cbs):
        super(Bar, self).__init__(name)
        self.menu = ["show", "send", "recive"]
        self.icon = icon
        self.cbs = cbs

    @rumps.clicked("show")
    def prefs(self, _):
        rumps.alert("jk! no send available!")
        rumps.notification("Awesome title", "amazing subtitle", "hi!!1")

    @rumps.clicked("send")
    def prefs(self, _):
        # rumps.alert("jk! no send available!")
        # rumps.notification("Awesome title", "amazing subtitle", "hi!!1")
        print('copy..')
        self.cbs('COPY')

    @rumps.clicked("recive")
    def onoff(self, sender):
        print('paste..')
        self.cbs('PASTE')
        # sender.state = not sender.state


if __name__ == "__main__":
    from myThreading import MyThread #重写的线程类
    

    def run():
        x_menubar = Bar(name='tripleX', 
                icon='../../media/Icon.icns',
                cbs = print )
        x_menubar.run()


    MyThread(run).join()

    print('finished....')