# -*- coding: utf-8 -*-
"""显示每部电影的词云"""

import pandas as pd
import jieba
from wordcloud import WordCloud
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel


# 读取电影热评数据
def read_movie_comments(file_path, movie_name):
    try:
        data = pd.read_csv(file_path, encoding='gbk')
        # 筛选出特定电影的热评
        filtered_data = data[data['电影名称'] == movie_name]
        return filtered_data['热评']
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在")
        return None


# 对热评内容进行分词
def cut_comments(comments):
    all_words = []
    for comment in comments:
        words = jieba.lcut(comment)
        all_words.extend(words)
    return all_words


# 生成词云
def generate_wordcloud(words):
    text = " ".join(words)
    wordcloud = WordCloud(font_path='simhei.ttf', background_color='white', width=800, height=400).generate(text)
    image = wordcloud.to_image()
    # 将 PIL 的 Image 对象转换为 QImage
    qimage = QImage(image.tobytes(), image.width, image.height, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


class MovieWordCloudWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        file_path = 'C:/Users/onfz2/WorkSpace/pythonProject/Test/data/movies.csv'  # 替换为你的数据文件路径
        movie_name = "霸王别姬"  # 替换为具体的电影名称
        comments = read_movie_comments(file_path, movie_name)
        if comments is not None:
            words = cut_comments(comments)
            pixmap = generate_wordcloud(words)

            label = QLabel()
            label.setPixmap(pixmap)
            layout.addWidget(label)

        self.setWindowTitle("电影热评词云展示")
        self.show()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = MovieWordCloudWindow()
#     sys.exit(app.exec_())
