import sys
import sqlite3
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QMessageBox, QStackedWidget, QFormLayout, QDateEdit, QTableView
from geopy.distance import geodesic
from PyQt5.QtCore import QDate

# Connect to the database
with sqlite3.connect('quit.db') as db:
    c = db.cursor()

c.execute('CREATE TABLE IF NOT EXISTS user (username TEXT NOT NULL, password TEXT NOT NULL)')
db.commit()

c.execute('CREATE TABLE IF NOT EXISTS booking (username TEXT NOT NULL, starting_point TEXT NOT NULL, destination TEXT NOT NULL, distance TEXT NOT NULL,  start_date TEXT NOT NULL, return_date TEXT NOT NULL, cost TEXT NOT NULL )')
db.commit()

class MainWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Login Page")

        # Create layout
        layout = QVBoxLayout()

        # Username
        self.name_label = QLabel("Username")
        self.name_entry = QLineEdit(self)

        # Password
        self.pword_label = QLabel("Password")
        self.pword_entry = QLineEdit(self)
        self.pword_entry.setEchoMode(QLineEdit.Password)

        # Buttons
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.new_user)

        # Add widgets to layout
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_entry)
        layout.addWidget(self.pword_label)
        layout.addWidget(self.pword_entry)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        username = self.name_entry.text()
        password = self.pword_entry.text()

        with sqlite3.connect('quit.db') as db:
            c = db.cursor()
            find_user = 'SELECT * FROM user WHERE username = ? AND password = ?'
            c.execute(find_user, (username, password))
            result = c.fetchall()

        if result:
            QMessageBox.information(self, "Success", "Login successful")
            self.stacked_widget.setCurrentIndex(1)  # Switch to the second window
        else:
            QMessageBox.warning(self, "Error", "Username or password not recognized")

    def new_user(self):
        username = self.name_entry.text()
        password = self.pword_entry.text()

        with sqlite3.connect('quit.db') as db:
            c = db.cursor()
            find_user = 'SELECT * FROM user WHERE username = ?'
            c.execute(find_user, (username,))
            if c.fetchall():
                QMessageBox.warning(self, "Error", "Username taken, please choose another")
            else:
                insert = 'INSERT INTO user(username, password) VALUES(?, ?)'
                c.execute(insert, (username, password))
                db.commit()
                QMessageBox.information(self, "Success", "Account created")


class SecondWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Travel Page")

        # Create layout
        layout = QFormLayout()

         # Name
        self.name_layout = QLabel("Enter your Name")
        self.name_entry = QLineEdit(self)

        # Source
        self.source_label = QLabel("Enter starting point")
        self.source_entry = QLineEdit(self)

        # Destination
        self.destination_label = QLabel("Enter destination")
        self.destination_entry = QLineEdit(self)

        # Cab type
        self.cab_label = QLabel("Enter type of cab")
        self.cab_entry = QLineEdit(self)

        # Rent date
        self.start_date_label = QLabel("Select start date")
        self.start_date_entry = QDateEdit(self)
        self.start_date_entry.setCalendarPopup(True)
        self.start_date_entry.setDate(QDate.currentDate())

        # Return date
        self.return_date_label = QLabel("Select return date")
        self.return_date_entry = QDateEdit(self)
        self.return_date_entry.setCalendarPopup(True)
        self.return_date_entry.setDate(QDate.currentDate())


        # Book button
        self.book_button = QPushButton("Book")
        self.book_button.clicked.connect(self.book)

        # Receipt button
        self.receipt_button = QPushButton("Receipt")
        self.receipt_button.clicked.connect(self.send_data)

        # History button
        self.history_button = QPushButton("History")
        self.history_button.clicked.connect(self.history)        

        # Add widgets to layout
        layout.addRow(self.name_layout,self.name_entry)
        layout.addRow(self.source_label, self.source_entry)
        layout.addRow(self.destination_label, self.destination_entry)
        layout.addRow(self.cab_label, self.cab_entry)
        layout.addRow(self.start_date_label,self.start_date_entry)
        layout.addRow(self.return_date_label,self.return_date_entry)
        layout.addRow(self.book_button)
        layout.addRow(self.receipt_button)
        layout.addRow(self.history_button)

        self.setLayout(layout)

    def book(self):
        source = self.source_entry.text()
        destination = self.destination_entry.text()
        cab = self.cab_entry.text()



        if not source or not destination or not cab:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return


        # Dictionary of cities and their coordinates
        cities = {'Chennai' : (13.0827, 80.2707),
            'Delhi': (28.7041, 77.1025),
            'Mumbai': (19.0760, 72.8777),
            'Kolkata': (22.5726, 88.3639),
            'Bangalore': (12.9716, 77.5946),
            # Add more cities as needed
        }
        
        # Calculate distance using geopy
        try:
            source_coords = cities[source] # Replace with actual coordinates (latitude, longitude) of source
            destination_coords = cities[destination]  # Replace with actual coordinates (latitude, longitude) of destination

            self.distance = geodesic(source_coords, destination_coords).kilometers
            self.distance = round(self.distance, 2)  # Round to 2 decimal places

            if cab == 'mini':
                rate = 50
            elif cab == 'macro':
                rate = 100
            elif cab == 'prime':
                rate = 150
            else:
                QMessageBox.warning(self, "Error", "Invalid cab type")
                return

            self.cost = self.distance * rate
            QMessageBox.information(self, "Success",
                                    f"Your travel distance from {source} to {destination} is {self.distance} km.\n"
                                    f"Your travel cost in a {cab} cab is {int(self.cost)} Rupees.")
            username = self.name_entry.text()
            starting_point = self.source_entry.text()
            destination = self.destination_entry.text()
            kilometers = self.distance
            start_date = self.start_date_entry.text()
            return_date = self.return_date_entry.text()
            amount = self.cost

            with sqlite3.connect('quit.db') as db:
                c = db.cursor()
                insert = 'INSERT INTO booking(username,starting_point,destination,distance,start_date,return_date,cost) VALUES(?, ?, ?, ?, ?, ?, ?)'
                c.execute(insert, (username,starting_point,destination,kilometers,start_date,return_date,amount))
                db.commit()
            
         
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error calculating distance: {str(e)}")

        # data.append(username,starting_point,destination,kilometers,start_date,return_date,amount)
                
    
    def send_data(self):
        username = self.name_entry.text()
        starting_point = self.source_entry.text()
        destination = self.destination_entry.text()
        kilometers = self.distance
        start_date = self.start_date_entry.text()
        retun_date = self.return_date_entry.text()
        amount = self.cost
        if not username or not destination or not starting_point or not kilometers or not start_date or not retun_date or not amount:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return
        
        self.data = [username,starting_point,destination,kilometers,start_date,retun_date,amount]
        
        self.third_window = Thirdwindow(data=self.data)
        self.third_window.show()
        self.close()
        # self.stacked_widget.setCurrentIndex(2)

    def history(self):
        self.stacked_widget.setCurrentIndex(2)

class Thirdwindow(QWidget):
    def __init__(self, data):
        super().__init__()
        # self.stacked_widget = stacked_widget
        self.data = data
        self.initUI(self.data)

    def initUI(self,data):
        self.setWindowTitle("Receipt")
    
        # create layout
        layout = QFormLayout()

        # Name
        self.name_bill_layout = QLabel("Your Name")
        self.name_bill_enter = QLabel(f'{data[0]}')

        # start
        self.start_point_label = QLabel("Starting Point")
        self.start_point_entry = QLabel(f'{data[1]}')

        # destination
        self.destination_label = QLabel("Destination Point")
        self.destination_entry = QLabel(f'{data[2]}')
        # distance
        self.distance_label = QLabel("Distance")
        self.distance_entry = QLabel(f'{data[3]}')
        
        # start date
        self.start_date_label = QLabel("Start Date")
        self.start_date_entry = QLabel(f'{data[4]}')

        # return date
        self.return_date_label = QLabel("Select return date")
        self.return_date_entry = QLabel(f'{data[5]}')

        # amount
        self.amount_label = QLabel("Amount")
        self.amount_cal   = QLabel(f'{data[6]}')

        # back button
        self.back_button = QPushButton("Exit App")
        self.back_button.clicked.connect(QApplication.instance().quit)

        # Add widgets to layout
        layout.addRow(self.name_bill_layout,self.name_bill_enter)
        layout.addRow(self.start_point_label,self.start_point_entry)
        layout.addRow(self.destination_label,self.destination_entry)
        layout.addRow(self.distance_label,self.distance_entry)
        layout.addRow(self.start_date_label,self.start_date_entry)
        layout.addRow(self.return_date_label,self.return_date_entry)
        layout.addRow(self.amount_label,self.amount_cal)
        layout.addRow(self.back_button)

        self.setLayout(layout)

    # def back(self):    
    #     self.close()
    #     # self.stacked_widget.setCurrentIndex(1)
        


class forthwindow(QWidget):
    def __init__(self,stacked_widget):
        super().__init__(stacked_widget)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setWindowTitle('History Table')
        self.setGeometry(100, 100, 600, 400)

        # Set up the database connection
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName('quit.db')

        if not self.db.open():
            print("Unable to open the database")
            return

        # Set up the model
        self.model = QSqlTableModel(self)
        self.model.setTable('booking')
        self.model.select()

        # Set up the view
        self.view = QTableView()
        self.view.setModel(self.model)
        
        # back button
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.back)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def back(self):
        self.stacked_widget.setCurrentIndex(1)



def main():
    app = QApplication(sys.argv)

    stacked_widget = QStackedWidget()
    main_window = MainWindow(stacked_widget)
    second_window = SecondWindow(stacked_widget)
    # third_window = Thirdwindow(stacked_widget)
    forth_window= forthwindow(stacked_widget)

    stacked_widget.addWidget(main_window)
    stacked_widget.addWidget(second_window)
    # stacked_widget.addWidget(third_window)
    stacked_widget.addWidget(forth_window)

    stacked_widget.setFixedHeight(700)
    stacked_widget.setFixedWidth(1000)
    
    stacked_widget.setCurrentIndex(0)  # Set the initial window to the login window
    stacked_widget.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()