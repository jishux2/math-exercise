from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtGui import QTextCursor, QFont, QDesktopServices
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QTabWidget
from PySide6.QtCore import Qt

class PreviewWindow(QWidget):
    def __init__(self, markdown_text: str, parent=None):
        super().__init__(parent, Qt.Window)  # 添加 Qt.Window 标志
        self.setWindowTitle("AI点评预览")
        
        layout = QVBoxLayout()
        tab_widget = QTabWidget()
        
        # 纯文本编辑器
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(markdown_text)
        self.editor.setReadOnly(True)
        font = QFont("Consolas", 11)
        self.editor.setFont(font)
        
        # Web预览
        self.webview = QWebEngineView()
        html_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 800px;
                    margin: 0 auto;
                }
                pre {
                    background-color: #f6f8fa;
                    padding: 16px;
                    border-radius: 6px;
                }
                code {
                    font-family: Consolas, "Liberation Mono", Menlo, Courier, monospace;
                }
            </style>
        </head>
        <body>
            <div id="content"></div>
            <script>
                document.getElementById('content').innerHTML = marked.parse(`%s`);
            </script>
        </body>
        </html>
        '''
        
        escaped_text = markdown_text.replace('`', '\\`')
        html_content = html_template % escaped_text
        
        web_page = CustomWebEnginePage(self.webview)
        self.webview.setPage(web_page)
        self.webview.setHtml(html_content)
        
        # 添加标签页
        tab_widget.addTab(self.webview, 'Rich Text')
        tab_widget.addTab(self.editor, 'Plain Text')
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        self.resize(850, 700)

class CustomWebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, typ, is_main_frame):
        if typ == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, typ, is_main_frame)