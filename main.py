import sys
import sqlite3
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTextEdit, QPushButton, QListWidget, \
    QAction, QListWidgetItem, QLineEdit, QMessageBox, QFontDialog, QComboBox
from PyQt5.QtWidgets import QFileDialog


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

        # Create a Save/Edit button
        self.save_edit_button = QPushButton('Save/Edit')
        self.save_edit_button.clicked.connect(self.save_or_edit_note)
        layout.addWidget(self.save_edit_button)

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

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск")
        layout.addWidget(self.search_edit)
        self.search_edit.textChanged.connect(self.search_notes)

        # Create an Export button
        export_button = QPushButton('Export')
        export_button.clicked.connect(self.export_notes)
        layout.addWidget(export_button)

    def search_notes(self):
        search_query = self.search_edit.text()
        if search_query:
            self.list_widget.clear()
            self.cursor.execute("SELECT id, title FROM notes WHERE title LIKE ? OR content LIKE ?",
                                (f"%{search_query}%", f"%{search_query}%"))
            notes = self.cursor.fetchall()
            for note in notes:
                item = QListWidgetItem(note[1])
                item.note_id = note[0]
                self.list_widget.addItem(item)
        else:
            self.load_notes()

    def save_or_edit_note(self):
        if self.current_note_id is not None:
            # Если есть текущая заметка, то спрашиваем, хочет ли пользователь её редактировать
            response = QMessageBox.question(self, 'Редактировать заметку', 'Хотите редактировать текущую заметку?',
                                            QMessageBox.Yes | QMessageBox.No)

            if response == QMessageBox.Yes:
                # Открываем редактирование текущей заметки
                self.edit_note()
            else:
                # Если пользователь не хочет редактировать, то сохраняем новую заметку
                self.save_note()
                self.current_note_id = None
                self.title_edit.clear()
                self.text_edit.clear()
        else:
            # Если нет текущей заметки, просто сохраняем новую заметку
            self.save_note()

    def add_note_to_list(self, note_id, title, content, is_favorite):
        item = QListWidgetItem(title)
        item.note_id = note_id
        item.is_favorite = is_favorite

    def load_notes(self):
        self.list_widget.clear()
        self.cursor.execute("SELECT id, title, content, is_favorite FROM notes")
        notes = self.cursor.fetchall()
        for note in notes:
            self.add_note_to_list(note[0], note[1], note[2], note[3])

    def mark_favorite(self, state):
        current_item = self.list_widget.currentItem()
        if current_item:
            note_id = current_item.note_id
            is_favorite = state == 2  # 2 represents Checked state in QCheckBox
            self.cursor.execute("UPDATE notes SET is_favorite = ? WHERE id = ?", (is_favorite, note_id))
            self.conn.commit()
            self.load_notes()

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
        pass

    def edit_note(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            note_id = current_item.note_id
            new_content = self.text_edit.toHtml()  # Получаем и сохраняем форматированный текст
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
                content TEXT,
                is_favorite INTEGER
            )
        ''')
        self.conn.commit()

    def save_note(self):
        title = self.title_edit.text()
        content = self.text_edit.toHtml()  # Получаем и сохраняем форматированный текст
        if title and content:
            self.cursor.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
            self.conn.commit()
            self.load_notes()
            self.title_edit.clear()
            self.text_edit.clear()
        else:
            QMessageBox.warning(self, 'Invalid Input', 'Title and content cannot be empty.')

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
        self.current_note_id = note_id  # Устанавливаем текущую заметку
        self.cursor.execute("SELECT title, content FROM notes WHERE id=?", (note_id,))
        title, content = self.cursor.fetchone()
        self.title_edit.setText(title)
        self.text_edit.setHtml(content)  # Устанавливаем форматированный текст

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

    def toggle_save_edit_mode(self):
        if self.edit_mode:
            self.edit_note()
            self.save_edit_button.setText('Save/Edit')
            self.edit_mode = False
        else:
            self.current_note_id = None  # Сбрасываем текущую заметку при создании новой
            self.title_edit.clear()
            self.text_edit.clear()
            self.save_edit_button.setText('Save')
            self.edit_mode = True

    def export_notes(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # Добавляем опцию для выбора формата файла

        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setNameFilter("JSON Files (*.json);;Text Files (*.txt);;All Files (*)")
        file_dialog.setWindowTitle("Экспорт заметок в файл")

        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]
            selected_filter = file_dialog.selectedNameFilter()

            notes_data = []
            self.cursor.execute("SELECT title, content FROM notes")
            notes = self.cursor.fetchall()
            for note in notes:
                title, content = note
                notes_data.append({"title": title, "content": content})

            try:
                if selected_filter == "JSON Files (*.json)":
                    with open(file_name, 'w', encoding='utf-8') as file:
                        json.dump(notes_data, file, ensure_ascii=False, indent=4)
                    QMessageBox.information(self, 'Экспорт завершен', 'Заметки успешно экспортированы в JSON файл.')
                elif selected_filter == "Text Files (*.txt)":
                    with open(file_name, 'w', encoding='utf-8') as file:
                        for note in notes_data:
                            file.write(f"Title: {note['title']}\n\n{note['content']}\n\n\n")
                    QMessageBox.information(self, 'Экспорт завершен',
                                            'Заметки успешно экспортированы в текстовый файл.')
            except Exception as e:
                QMessageBox.critical(self, 'Ошибка при экспорте', f'Произошла ошибка при экспорте заметок: {str(e)}')


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
        border: 1px solid #ffffff;
        color: #ffffff;
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
