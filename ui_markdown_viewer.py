"""
Окно для просмотра ответа нейросети в формате Markdown.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QTextEdit, QLabel, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import re


class MarkdownViewerDialog(QDialog):
    """Диалог для просмотра Markdown."""
    
    def __init__(self, model_name: str, response: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Ответ: {model_name}")
        self.setMinimumSize(800, 600)
        self.model_name = model_name
        self.response = response
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса."""
        layout = QVBoxLayout()
        
        # Заголовок с названием модели
        header_label = QLabel(f"<h2>Ответ модели: {self.model_name}</h2>")
        layout.addWidget(header_label)
        
        # Текстовое поле с поддержкой Markdown
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        # Конвертируем Markdown в HTML для отображения
        html_content = self.markdown_to_html(self.response)
        self.text_edit.setHtml(html_content)
        
        # Настройки стиля
        self.text_edit.setStyleSheet("""
            QTextEdit {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.6;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.text_edit)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("Копировать")
        copy_button.clicked.connect(self.copy_to_clipboard)
        button_layout.addWidget(copy_button)
        
        button_layout.addStretch()
        
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        button_layout.addWidget(button_box)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def markdown_to_html(self, markdown_text: str) -> str:
        """
        Простая конвертация Markdown в HTML.
        Поддерживает основные элементы: заголовки, жирный/курсив, код, списки, ссылки.
        """
        html = markdown_text
        
        # Экранируем HTML символы
        html = html.replace('&', '&amp;')
        html = html.replace('<', '&lt;')
        html = html.replace('>', '&gt;')
        
        # Заголовки
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Блоки кода (многострочные)
        html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
        
        # Инлайн код
        html = re.sub(r'`([^`]+)`', r'<code style="background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px;">\1</code>', html)
        
        # Жирный текст
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
        
        # Курсив
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
        
        # Ссылки
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
        
        # Нумерованные списки
        lines = html.split('\n')
        in_list = False
        result_lines = []
        for line in lines:
            if re.match(r'^\d+\.\s+', line):
                if not in_list:
                    result_lines.append('<ol>')
                    in_list = True
                content = re.sub(r'^\d+\.\s+', '', line)
                result_lines.append(f'<li>{content}</li>')
            else:
                if in_list:
                    result_lines.append('</ol>')
                    in_list = False
                result_lines.append(line)
        if in_list:
            result_lines.append('</ol>')
        html = '\n'.join(result_lines)
        
        # Маркированные списки
        lines = html.split('\n')
        in_list = False
        result_lines = []
        for line in lines:
            if re.match(r'^[-*+]\s+', line):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                content = re.sub(r'^[-*+]\s+', '', line)
                result_lines.append(f'<li>{content}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        if in_list:
            result_lines.append('</ul>')
        html = '\n'.join(result_lines)
        
        # Горизонтальная линия
        html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)
        html = re.sub(r'^\*\*\*$', '<hr>', html, flags=re.MULTILINE)
        
        # Переносы строк в параграфы
        html = re.sub(r'\n\n+', '</p><p>', html)
        html = '<p>' + html + '</p>'
        
        # Стили для лучшего отображения
        styled_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 11pt;
                    line-height: 1.6;
                    padding: 20px;
                    color: #333;
                }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; border-bottom: 1px solid #bdc3c7; padding-bottom: 8px; }}
                h3 {{ color: #7f8c8d; }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 0.9em;
                }}
                pre {{
                    background-color: #f8f8f8;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 12px;
                    overflow-x: auto;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                ul, ol {{
                    margin-left: 20px;
                    margin-top: 10px;
                    margin-bottom: 10px;
                }}
                li {{
                    margin-bottom: 5px;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                hr {{
                    border: none;
                    border-top: 1px solid #ddd;
                    margin: 20px 0;
                }}
                blockquote {{
                    border-left: 4px solid #ddd;
                    margin: 10px 0;
                    padding-left: 15px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return styled_html
    
    def copy_to_clipboard(self):
        """Копировать текст в буфер обмена."""
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.response)
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Успех", "Текст скопирован в буфер обмена")


