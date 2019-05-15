import rumps

class Bar(rumps.App):
    def __init__(self, name, icon, cbs):
        super(Bar, self).__init__(name)
        self.menu = ["show", "send", "receive"]
        self.icon = icon
        self.cbs = cbs

    def alert(self, title=None, message='', ok=None, cancel=None, other=None, icon_path=None):
        return rumps.alert(title, message, ok, cancel, other, icon_path)

    @rumps.clicked("show")
    def show(self, _):
        self.cbs('SHOW')

    @rumps.clicked("send")
    def send(self, _):
        self.cbs('COPY')

    @rumps.clicked("receive")
    def receive(self, sender):
        self.cbs('PASTE')
        # sender.state = not sender.state

if __name__ == "__main__":

    # def fun(cmd):
    #     global x_menubar
    #     print(cmd)
    #     x_menubar.alert(title='tirle', message='message', ok='ok', cancel='can', other='ohter', icon_path=None)

    x_menubar = Bar(name='tripleX', 
                icon='../../media/Icon.icns',
                cbs = print )
        
    
    x_menubar.run()

