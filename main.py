import sys
import socket
import threading
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QTextEdit, QListWidget, QSplitter, QMessageBox)
from PyQt5.QtGui import QFont, QColor, QTextCursor, QTextCharFormat
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject
try: 
    import translator as translate_plugin
except Exception:
    pass

class IRCSignals(QObject):
    message_received = pyqtSignal(str, str)  # channel, message
    event_received = pyqtSignal(str)         # event message
    connection_error = pyqtSignal(str)       # error message

class IRCClient:
    def __init__(self):
        self.server = str(sys.argv[1])
        self.port = int(sys.argv[2])
        self.nick = sys.argv[3] if len(sys.argv) > 3 else "Guest" + str(random.randint(1000, 9999)) # input("Nickname > ")# "Guest" + str(random.randint(1000, 9999))
        self.usetranslator = sys.argv[4].lower() in ("true", "yes", "1", "on") if len(sys.argv) > 4 else False
        self.current_channel = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.signals = IRCSignals()
        
    def connect(self):
        try:
            self.sock.connect((self.server, self.port))
            self._send(f"NICK {self.nick}")
            self._send(f"USER {self.nick} 0 * :{self.nick}")
            self.running = True
            return True
        except Exception as e:
            self.signals.connection_error.emit(f"Connection error: {e}")
            return False
    
    def _send(self, message):
        try:
            self.sock.send(f"{message}\r\n".encode('utf-8'))
        except Exception as e:
            self.signals.connection_error.emit(f"Send error: {e}")
    
    def join_channel(self, channel):
        if not channel.startswith("#"):
            channel = "#" + channel
        self._send(f"JOIN {channel}")
        self.current_channel = channel
        self.signals.event_received.emit(f"Joined {channel}")
    
    def receive_messages(self):
        while self.running:
            try:
                data = self.sock.recv(4096).decode('utf-8', errors='ignore')
                if not data:
                    continue

                for line in data.split('\r\n'):
                    line = line.strip()
                    if not line:
                        continue

                    # Обработка PING
                    if line.startswith("PING"):
                        self._send(f"PONG {line.split()[1]}")
                        continue

                    # Вывод сообщений
                    if "PRIVMSG" in line:
                        parts = line.split("PRIVMSG")[1].split(":", 1)
                        channel = parts[0].strip()
                        message = parts[1] if len(parts) > 1 else ""
                        sender = line.split("!")[0][1:]
                        if self.usetranslator:
                            try:
                                traslation = translate_plugin.on_russian(message)
                                
                                self.signals.message_received.emit(channel, f"<{sender}> {translation}")
                            except Exception:
                                self.signals.message_received.emit(channel, f"<{sender}> {message}")
                        else:
                            self.signals.message_received.emit(channel, f"<{sender}> {message}")

                    else:
                        # Обработка других событий (JOIN, PART, QUIT и т.д.)
                        if "JOIN" in line:
                            nick = line.split("!")[0][1:]
                            channel = line.split("JOIN")[1].strip()
                            self.signals.event_received.emit(f"{nick} joined {channel}")
                        elif "PART" in line:
                            nick = line.split("!")[0][1:]
                            channel = line.split("PART")[1].strip()
                            self.signals.event_received.emit(f"{nick} left {channel}")
                        elif "QUIT" in line:
                            nick = line.split("!")[0][1:]
                            self.signals.event_received.emit(f"{nick} quit")
                        elif "NICK" in line:
                            old_nick = line.split("!")[0][1:]
                            new_nick = line.split("NICK")[1].strip()[1:]
                            self.signals.event_received.emit(f"{old_nick} is now known as {new_nick}")

            except Exception as e:
                self.signals.connection_error.emit(f"Receive error: {e}")
                self.running = False
                break
    
    def send_message(self, message):
        if message.startswith("$#"):
            channel = message[2:].strip()
            self.join_channel("#" + channel)
        if message.startswith("$nick "):
            nick = message[6:].strip()
            self._send(f"NICK {nick}")
        elif self.current_channel:
            if self.usetranslator:
                try:
                    message = translate_plugin.on_english(message)
                    self._send(f"PRIVMSG {self.current_channel} :{message}")
                except Exception as e:
                    self.signals.connection_error.emit(f"Send message error: {e}")
            else:
                try:
                    self._send(f"PRIVMSG {self.current_channel} :{message}")
                except Exception as e:
                    self.signals.connection_error.emit(f"Send message error: {e}")
        else:
            self.signals.event_received.emit("Please join a channel first")
    
    def disconnect(self):
        self.running = False
        try:
            self._send("QUIT :Ircium Client > ircium.unionium.org")
            self.sock.close()
        except:
            pass

class CozyIRCClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ircium Client")
        self.setGeometry(100, 100, 900, 600)
        
        # IRC клиент
        self.irc_client = IRCClient()
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный лейаут
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Splitter для разделения каналов и чата
        splitter = QSplitter(Qt.Horizontal)
        
        # Панель каналов/пользователей
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        self.channel_list = QListWidget()
        self.channel_list.setFont(QFont("", 24))
        self.channel_list.itemDoubleClicked.connect(self.join_selected_channel)
        
        # Кнопки под списком каналов
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)
        
        # Создаем кнопки
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        self.settings_button = QPushButton("Settings")
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close)
        
        # Устанавливаем фиксированную высоту для кнопок
        button_height = 30
        self.connect_button.setFixedHeight(button_height)
        self.settings_button.setFixedHeight(button_height)
        self.quit_button.setFixedHeight(button_height)
        
        # Добавляем кнопки в layout
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.quit_button)
        
        # Добавляем виджеты в левую панель
        left_layout.addWidget(self.channel_list)
        left_layout.addWidget(button_widget)
        
        # Основная область чата
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)
        
        # Текстовое поле чата
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 11))
        
        # Панель ввода сообщения
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(5, 5, 5, 5)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Enter message...")
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.setFixedWidth(100)
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        
        # Добавляем виджеты в чат лейаут
        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(input_widget)
        
        # Добавляем виджеты в splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(chat_widget)
        
        main_layout.addWidget(splitter)
        
        # Устанавливаем уютную темную тему
        self.set_cozy_dark_theme()
        
        # Подключаем сигналы IRC клиента
        self.irc_client.signals.message_received.connect(self.add_message)
        self.irc_client.signals.event_received.connect(self.add_event)
        self.irc_client.signals.connection_error.connect(self.show_error)
        
        # Добавляем тестовые сообщения для демонстрации
        self.add_sample_events()
    
    def set_cozy_dark_theme(self):
        cozy_dark_theme = """
        QWidget {
            background-color: #232323;
            color: #e8e8e8;
            border: none;
        }
        QTextEdit, QListWidget {
            background-color: #1e1e1e;
            color: #e8e8e8;
            border: none;
        }
        QLineEdit {
            background-color: #2a2a2a;
            color: #e8e8e8;
            border: 1px solid #3a3a3a;
            border-radius: 3px;
            padding: 5px;
        }
        QPushButton {
            background-color: #3a3a3a;
            color: #e8e8e8;
            border: 1px solid #4a4a4a;
            border-radius: 3px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
        }
        QPushButton:pressed {
            background-color: #2a2a2a;
        }
        QListWidget {
            padding: 5px 5px;
            font-size: 12px;
        }
        QListWidget::item {
            padding: 5px;
        }
        QListWidget::item:hover {
            background-color: #3a3a3a;
        }
        QListWidget::item:selected {
            background-color: #5a4a6d;
        }
        QScrollBar:vertical {
            background: #1e1e1e;
            width: 10px;
        }
        QScrollBar::handle:vertical {
            background: #4a4a4a;
            min-height: 20px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
        }
        """
        self.setStyleSheet(cozy_dark_theme)
    
    def generate_cozy_color(self, nick):
        """Генерирует приглушенный "ламповый" цвет для ника"""
        random.seed(hash(nick))
        # Палитра приглушенных теплых цветов
        color_palette = [
            (255, 145, 110),  # теплый оранжевый
            (255, 180, 130),  # персиковый
            (255, 120, 120),  # розовый
            (220, 180, 220),  # лавандовый
            (180, 220, 220),  # мятный
            (220, 220, 180),  # бежевый
            (255, 210, 150),  # светлый оранжевый
            (200, 230, 200),  # пастельно-зеленый
            (230, 200, 230),  # сиреневый
            (200, 200, 230)   # пастельно-синий
        ]
        r, g, b = random.choice(color_palette)
        return QColor(r, g, b)
    
    def add_message(self, channel, text):
        """Добавляет сообщение в чат"""
        if channel != self.irc_client.current_channel:
            return
            
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Разделяем ник и сообщение
        nick_end = text.find(">")
        if nick_end != -1:
            nick = text[:nick_end+1]
            message = text[nick_end+2:]
            
            nick_color = self.generate_cozy_color(nick[1:-1])  # Убираем < > вокруг ника
            
            # Форматирование для ника
            nick_format = QTextCharFormat()
            nick_format.setForeground(nick_color)
            nick_format.setFontWeight(QFont.Bold)
            
            # Форматирование для сообщения
            msg_format = QTextCharFormat()
            msg_format.setForeground(QColor("#e8e8e8"))
            
            # Вставляем ник и сообщение
            cursor.insertText(nick + " ", nick_format)
            cursor.insertText(message + "\n", msg_format)
        else:
            # Если не удалось распарсить ник, просто выводим сообщение
            format = QTextCharFormat()
            format.setForeground(QColor("#e8e8e8"))
            cursor.insertText(text + "\n", format)
        
        # Прокручиваем вниз
        self.chat_display.ensureCursorVisible()
    
    def add_event(self, text):
        """Добавляет событие в чат"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Форматирование для событий
        format = QTextCharFormat()
        format.setForeground(QColor("#888888"))  # Серый цвет для событий
        format.setFontItalic(True)
        cursor.insertText(f"*** {text}\n", format)
        
        # Прокручиваем вниз
        self.chat_display.ensureCursorVisible()
    
    def show_error(self, error):
        """Показывает сообщение об ошибке"""
        QMessageBox.critical(self, "Error", error)
    
    def toggle_connection(self):
        """Подключается или отключается от сервера"""
        if not self.irc_client.running:
            if self.irc_client.connect():
                self.connect_button.setText("Disconnect")
                # Запускаем поток для получения сообщений
                receive_thread = threading.Thread(target=self.irc_client.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()
                self.add_event("Connected to server")
        else:
            self.irc_client.disconnect()
            self.connect_button.setText("Connect")
            self.add_event("Disconnected from server")
    
    def send_message(self):
        """Отправляет сообщение и добавляет его в чат"""
        message = self.message_input.text().strip()
        if not message:
            return
            
        # Добавляем свое сообщение в чат сразу
        self.add_own_message(message)
        
        # Отправляем сообщение на сервер
        self.irc_client.send_message(message)
        self.message_input.clear()

    def add_own_message(self, message):
        """Добавляет собственное сообщение в чат"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Форматирование для своего сообщения
        nick_format = QTextCharFormat()
        nick_format.setForeground(QColor("#5a4a6d"))  # Фиолетовый цвет для своего ника
        nick_format.setFontWeight(QFont.Bold)
        
        msg_format = QTextCharFormat()
        msg_format.setForeground(QColor("#a8a8a8"))  # Светло-серый для своего текста
        
        # Вставляем ник и сообщение
        cursor.insertText(f"<{self.irc_client.nick}> ", nick_format)
        cursor.insertText(message + "\n", msg_format)
        
        # Прокручиваем вниз
        self.chat_display.ensureCursorVisible()
    
    def join_selected_channel(self):
        """Присоединяется к выбранному каналу"""
        item = self.channel_list.currentItem()
        if item and item.text().startswith("#"):
            self.irc_client.join_channel(item.text())
    
    def add_sample_events(self):
        """Добавляет тестовые сообщения и события"""
        self.add_event("Welcome to Ircium Client!")
        self.add_event("Please connect to a server")
        # Добавляем тестовые каналы
        self.channel_list.addItems(["#main", "#general"])
    
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.irc_client.running:
            self.irc_client.disconnect()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Современный стиль
    
    # Устанавливаем уютную темную палитру для Fusion стиля
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.Window, QColor(35, 35, 35))
    dark_palette.setColor(dark_palette.WindowText, QColor(232, 232, 232))
    dark_palette.setColor(dark_palette.Base, QColor(30, 30, 30))
    dark_palette.setColor(dark_palette.AlternateBase, QColor(42, 42, 42))
    dark_palette.setColor(dark_palette.ToolTipBase, QColor(60, 60, 60))
    dark_palette.setColor(dark_palette.ToolTipText, QColor(232, 232, 232))
    dark_palette.setColor(dark_palette.Text, QColor(232, 232, 232))
    dark_palette.setColor(dark_palette.Button, QColor(58, 58, 58))
    dark_palette.setColor(dark_palette.ButtonText, QColor(232, 232, 232))
    dark_palette.setColor(dark_palette.BrightText, QColor(255, 145, 110))
    dark_palette.setColor(dark_palette.Link, QColor(150, 180, 220))
    dark_palette.setColor(dark_palette.Highlight, QColor(90, 74, 109))
    dark_palette.setColor(dark_palette.HighlightedText, Qt.white)
    app.setPalette(dark_palette)
    
    window = CozyIRCClient()
    window.show()
    sys.exit(app.exec_())
