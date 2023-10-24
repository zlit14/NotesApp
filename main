import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QListWidget,\
    QAction, QListWidgetItem, QLineEdit, QMessageBox, QFontDialog, QComboBox

class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_db()
        self.load_notes()

    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Заметки')

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout
        layout = QVBoxLayout(central_widget)

        # Create a QLineEdit for the note title
        self.title_edit = QLineEdit()
        layout.addWidget(self.title_edit)

        # Create a QTextEdit for note content
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)


        # Create a Save button
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_note)
        layout.addWidget(save_button)

        # Create a ListWidget for listing notes
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        self.list_widget.itemClicked.connect(self.load_selected_note)

        # Create a File menu
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # Create actions for File menu
        new_action = QAction('New', self)
        new_action.triggered.connect(self.new_note)
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.load_notes)
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)

        # Create an Edit button
        edit_button = QPushButton('Edit')
        edit_button.clicked.connect(self.edit_note)
        layout.addWidget(edit_button)

        # Create a Delete button
        delete_button = QPushButton('Delete')
        delete_button.clicked.connect(self.delete_note)
        layout.addWidget(delete_button)

        format_toolbar = self.addToolBar('Format')
        bold_button = QPushButton('Bold')
        bold_button.clicked.connect(self.toggle_bold)
        italic_button = QPushButton('Italic')
        italic_button.clicked.connect(self.toggle_italic)
        font_size_button = QPushButton('Font Size')
        font_size_button.clicked.connect(self.change_font_size)

        format_toolbar.addWidget(bold_button)
        format_toolbar.addWidget(italic_button)
        format_toolbar.addWidget(font_size_button)

    def add_note_to_list(self, note_id, title, content, color, checked, last_edit_time, font_size, bold, italic):
        pass
    def load_notes(self):
        self.list_widget.clear()
        self.cursor.execute(
            "SELECT id, title, content, color, checked, last_edit_time, font_size, bold, italic FROM notes WHERE title LIKE ?",
            (f"%{self.search_query}%",))
        notes = self.cursor.fetchall()
        for note in notes:
            self.add_note_to_list(note[0], note[1], note[2], note[3], note[4], note[5], note[6], note[7], note[8])

    def toggle_bold(self):
        cursor = self.text_edit.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontWeight(94 if fmt.fontWeight() == 50 else 50)
        cursor.setCharFormat(fmt)

    def toggle_italic(self):
        cursor = self.text_edit.textCursor()
        fmt = cursor.charFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        cursor.setCharFormat(fmt)

    def change_font_size(self):
        cursor = self.text_edit.textCursor()
        fmt = cursor.charFormat()
        ok, font = QFontDialog.getFont(fmt)
        if ok:
            cursor.setCharFormat(fmt)
            cursor.select(QTextCursor.Document)
            cursor.setCharFormat(fmt)
            self.text_edit.setTextCursor(cursor)


    def edit_note(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            note_id = current_item.note_id
            new_content = self.text_edit.toPlainText()
            self.cursor.execute("UPDATE notes SET content = ? WHERE id = ?", (new_content, note_id))
            self.conn.commit()
            self.load_notes()


    def init_db(self):
        self.conn = sqlite3.connect('notes.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT
            )
        ''')
        self.conn.commit()

    def save_note(self):
        title = 'Sample Title'  # You can implement title input
        content = self.text_edit.toPlainText()
        self.cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        self.conn.commit()
        self.load_notes()

    def new_note(self):
        self.text_edit.clear()

    def load_notes(self):
        self.list_widget.clear()
        self.cursor.execute("SELECT id, title FROM notes")
        notes = self.cursor.fetchall()
        for note in notes:
            item = QListWidgetItem(note[1])
            item.note_id = note[0]
            self.list_widget.addItem(item)

    def load_selected_note(self, item):
        note_id = item.note_id
        self.cursor.execute("SELECT content FROM notes WHERE id=?", (note_id,))
        content = self.cursor.fetchone()[0]
        self.text_edit.setPlainText(content)

    def save_note(self):
        title = self.title_edit.text()
        content = self.text_edit.toPlainText()
        if title and content:
            self.cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
            self.conn.commit()
            self.load_notes()
            self.title_edit.clear()
            self.text_edit.clear()
        else:
            QMessageBox.warning(self, 'Invalid Input', 'Title and content cannot be empty.')

    def delete_note(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            note_id = current_item.note_id
            confirmation = QMessageBox.question(self, 'Удалить заметку', 'Вы точно хотите удалить эту заметку?',
                                               QMessageBox.Yes | QMessageBox.No)
            if confirmation == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                self.conn.commit()
                self.load_notes()
                self.text_edit.clear()

if __name__ == '__main__':
    stylesheet = """
    QMainWindow {
        background-color: #000000;
    }

    QTextEdit {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #cccccc;
    }

    QPushButton {
        background-color: #67ff9a;
        color: #000000;
        border: 1px solid #67ff9a;
        padding: 5px 15px;
        font-family: 'Bahnschrift SemiBold Condensed';
        font-size: 15px;
        border-radius: 10px 5%;
    }

    QPushButton:hover {
        background-color: #2980b9;
        border: 1px solid #2980b9;
    }

    QListWidget {
        background-color: #000000;
        color: #ffffff;
        border: 1px solid #cccccc;
        alternate-background-color: #f0f0f0;
    }

    QListWidget::item {
        background-color: transparent;
    }

    QListWidget::item:selected {
        background-color: #67ff9a;
        color: #ffffff;
    }

    QLineEdit {
        background-color: #000000;
        border: 1px solid #cccccc;
    }

    QCheckBox {
        spacing: 5px;
    }

    """
    app = QApplication(sys.argv)
    window = NotesApp()
    app.setStyleSheet(stylesheet)
    window.show()
    sys.exit(app.exec_())

