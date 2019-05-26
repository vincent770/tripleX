from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QCheckBox, QSystemTrayIcon, \
    QSpacerItem, QSizePolicy, QMenu, QAction, QStyle, qApp, QVBoxLayout,QMessageBox, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize

class Window_tray(QMainWindow):

    def __init__(self,cbs,title=''):
        # Be sure to call the super class method
        QMainWindow.__init__(self)
 
        self.setMinimumSize(QSize(480, 80))             # Set sizes
        self.setWindowTitle("tripleX "+title)  # Set a title
        self.label1 = QLabel("Welcome to use tripleX.", self)
        # self.check_box = QCheckBox('History message')

        self.textEdit = QTextEdit()
     
        central_widget = QWidget(self)                  # Create a central widget
        self.setCentralWidget(central_widget)           # Set the central widget
        grid_layout = QGridLayout(central_widget)         # Create a QGridLayout

        grid_layout.addWidget(self.label1, 0, 0)        
        # grid_layout.addWidget(self.check_box, 1, 0)
        grid_layout.addWidget(self.textEdit,2,0)

        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
 
        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        self.act_show = QAction(" Refresh ", self)
        self.act_send = QAction(" Send ", self)
        self.act_get = QAction(" Get ", self)
        self.quit_action = QAction("Exit ", self)
        self.act_send_cancel = QAction(" Stop sending ", self)
        self.act_get_cancel = QAction(" Stop getting ", self)

        self.act_show.triggered.connect(lambda: cbs('SHOW') )
        self.act_send.triggered.connect(lambda: cbs('COPY') )
        self.act_get.triggered.connect(lambda: cbs('PASTE') )
        self.quit_action.triggered.connect(qApp.quit)

        self.act_send_cancel.triggered.connect(lambda: cbs('CANCEL') )
        self.act_get_cancel.triggered.connect(lambda: cbs('CANCEL') )

        self.act_show.setIcon(QIcon("../../media/refresh.png"))
        self.act_send.setIcon(QIcon("../../media/send.png"))
        self.act_get.setIcon(QIcon("../../media/download.png"))
        self.act_get_cancel.setIcon(QIcon("../../media/stop.png"))
        self.act_send_cancel.setIcon(QIcon("../../media/stop.png"))

        tray_menu = QMenu()
        tray_menu.addAction(self.act_show)
        tray_menu.addAction(self.act_send)
        tray_menu.addAction(self.act_send_cancel)
        tray_menu.addAction(self.act_get)
        tray_menu.addAction(self.act_get_cancel)
        tray_menu.addAction(self.quit_action)

        self.set_menu_visibility('INIT')

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        # self.hide()

    def set_menu_visibility(self, state):
        if state == 'INIT':
            self.act_send.setVisible(True)
            self.act_get.setVisible(True)        
            self.act_send_cancel.setVisible(False)
            self.act_get_cancel.setVisible(False)

        if state == 'COPY':
            self.act_send.setVisible(False)
            self.act_get.setVisible(True)        
            self.act_send_cancel.setVisible(True)
            self.act_get_cancel.setVisible(False)
            
        if state == 'PASTE':
            self.act_send.setVisible(True)
            self.act_get.setVisible(False)        
            self.act_send_cancel.setVisible(False)
            self.act_get_cancel.setVisible(True)
       
    def write_to_textEdit(self, text):
        self.textEdit.setPlainText(text)

    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEvent(self, event):
        # if self.check_box.isChecked():
        event.ignore()
        self.hide()

    def tray_notify(self, title, message):
        self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.Information,
                2000
            )

    def pop_a_alert(self, title, message):
        reply = QMessageBox.information(self, title, message,
                    QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes)
        print(reply)
        return reply
 
if __name__ == "__main__":

    import sys
    app = QApplication(sys.argv)
    sys_tray = Window_tray(print)

    sys_tray.pop_a_alert('hello','sds')

    sys.exit(app.exec())
