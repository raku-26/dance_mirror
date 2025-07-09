import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap, QLabel

class YouTubeMirrorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube + 镜子")
        self.setFixedSize(1280, 720)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("请输入 YouTube 链接")
        layout.addWidget(self.url_input)

        self.go_button = QPushButton("加载视频")
        self.go_button.clicked.connect(self.load_video)
        layout.addWidget(self.go_button)

        main_layout = QHBoxLayout()
        layout.addLayout(main_layout)

        # 左边：网页嵌入播放
        self.web_view = QWebEngineView()
        self.web_view.setFixedWidth(640)
        main_layout.addWidget(self.web_view)

        # 右边：摄像头镜像
        self.camera_label = QLabel()
        main_layout.addWidget(self.camera_label)

        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

    def load_video(self):
        url = self.url_input.text()
        if "youtube.com" in url or "youtu.be" in url:
            embed_url = self.get_embed_url(url)
            html = f"""
            <html>
                <body style="margin:0;">
                    <iframe width="640" height="360"
                        src="{embed_url}?autoplay=1"
                        frameborder="0"
                        allowfullscreen>
                    </iframe>
                </body>
            </html>
            """
            self.web_view.setHtml(html)

    def get_embed_url(self, url):
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
        else:
            return url
        return f"https://www.youtube.com/embed/{video_id}"

    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_image).scaled(640, 480))

    def closeEvent(self, event):
        self.cap.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YouTubeMirrorApp()
    window.show()
    sys.exit(app.exec_())