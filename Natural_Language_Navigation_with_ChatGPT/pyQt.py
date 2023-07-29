import sys,threading,socket,time
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox, QLineEdit, QTextEdit, QVBoxLayout, QWidget
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PyQt Example')
        self.setGeometry(100, 100, 300, 200)

        # Create a central widget to hold the layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a vertical layout
        layout = QVBoxLayout(central_widget)

        # Create a text input
        self.text_input = QLineEdit()
        layout.addWidget(self.text_input)

        self.send_button = QPushButton('Send!')
        layout.addWidget(self.send_button)
        self.send_button.clicked.connect(self.sendButtonCB)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)  # To prevent user input
        layout.addWidget(self.text_output)

        self.confirm_button = QPushButton('Confirm')
        layout.addWidget(self.confirm_button)
        self.confirm_button.clicked.connect(self.confirmButtonCB)

        self.follow_button = QPushButton('Follow')
        layout.addWidget(self.follow_button)
        self.follow_button.clicked.connect(self.followButtonCB)

        self.guide_button = QPushButton('Guide')
        layout.addWidget(self.guide_button)
        self.guide_button.clicked.connect(self.guideButtonCB)

        self.go_back_button = QPushButton('Go Back')
        layout.addWidget(self.go_back_button)
        self.go_back_button.clicked.connect(self.goBackButtonCB)

        self.tcp_thread = threading.Thread(target=self.receiveMessages)
        # self.tcp_thread.daemon = True
        self.tcp_thread.start()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('127.0.0.1', 12343)
        self.client_socket.connect(server_address)


    def sendButtonCB(self):
        input_text = "{\"request\":\"" + self.text_input.text() + "\"}"
        try:
            self.client_socket.sendall(input_text.encode())
            self.text_output.setPlainText('Message sent: ' + input_text)
        except Exception as e:
            self.text_output.setPlainText('Error: ' + str(e))

    def followButtonCB(self):
        QMessageBox.information(self, 'Message', f'Follow Mode')

    def guideButtonCB(self):
        QMessageBox.information(self, 'Message', f'Guide Mode')
    
    def goBackButtonCB(self):
        QMessageBox.information(self, 'Message', f'Go Back')

    def confirmButtonCB(self):
        input_text ="{\"confirm\":\"" + self.text_output.text() + "\"}"

        try:
            self.client_socket.sendall(input_text.encode())
            self.text_output.setPlainText('Message sent: ' + input_text)
        except Exception as e:
            self.text_output.setPlainText('Error: ' + str(e))

    def receiveMessages(self):
        while True:
            time.sleep(1)
            try:
                data = self.client_socket.recv(1024)
                message = data.decode()
                self.text_output.setPlainText('Received: ' + message)
            except Exception as e:
                self.text_output.setPlainText('Error: ' + str(e))
                

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
