import sqlite3
import pandas as pd
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)


def init_db():
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                电影名称 TEXT,
                图片链接 TEXT,
                类型 TEXT,
                基础信息 TEXT,
                上映年份 INTEGER,
                时长 INTEGER,
                简介 TEXT,
                主演 TEXT,
                评分 REAL,
                评价人数 INTEGER,
                热评 TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logging.debug('数据库初始化成功')
    except Exception as e:
        logging.error(f'数据库初始化出错: {e}')


def insert_data_to_db():
    try:
        df = pd.read_csv('data/movies.csv', encoding='gbk')
        conn = sqlite3.connect('movies.db')
        df.to_sql('movies', conn, if_exists='append', index=False)
        conn.close()
        logging.debug('数据插入数据库成功')
    except FileNotFoundError:
        logging.error('错误: 未找到电影数据集文件！')
    except Exception as e:
        logging.error(f'插入数据到数据库时出错: {e}')


def get_movie_list(page, per_page):
    offset = (page - 1) * per_page
    try:
        # 连接数据库并设置编码为 utf - 8
        conn = sqlite3.connect('movies.db')
        conn.text_factory = str
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM movies')
        total_movies = cursor.fetchone()[0]
        cursor.execute('SELECT MAX(评分) FROM movies')
        highest_rating = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(DISTINCT 类型) FROM movies')
        genre_count = cursor.fetchone()[0]
        cursor.execute('SELECT 上映年份 FROM movies GROUP BY 上映年份 ORDER BY COUNT(*) DESC LIMIT 1')
        result = cursor.fetchone()
        most_released_year = result[0] if result else None
        cursor.execute('SELECT MAX(时长) FROM movies')
        max_duration = cursor.fetchone()[0]

        cursor.execute('SELECT * FROM movies LIMIT? OFFSET?', (per_page, offset))
        movies = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        movies = [dict(zip(columns, row)) for row in movies]

        # 数据类型转换
        for movie in movies:
            movie['评分'] = float(movie['评分']) if movie['评分'] else 0
            movie['上映年份'] = int(movie['上映年份']) if movie['上映年份'] else 0
            movie['时长'] = int(movie['时长']) if movie['时长'] else 0
            movie['评价人数'] = int(movie['评价人数']) if movie['评价人数'] else 0

        conn.close()
        total_pages = (total_movies + per_page - 1) // per_page
        print(f"总电影数: {total_movies}, 每页显示数量: {per_page}, 总页数: {total_pages}")
        logging.debug(f'成功查询第 {page} 页的电影列表数据')
        return total_movies, highest_rating, genre_count, most_released_year, max_duration, movies, total_pages
    except Exception as e:
        logging.error(f'查询电影列表数据时出错: {e}')
        return None


def get_yearly_movie_count():
    try:
        conn = sqlite3.connect('movies.db')
        cursor = conn.cursor()
        query = 'SELECT 上映年份, COUNT(*) FROM movies GROUP BY 上映年份'
        print("执行的查询语句：", query)
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        if not result:
            print("查询结果为空，可能数据库中没有相关数据。")
            return {}
        yearly_movie_count = {str(year): count for year, count in result}
        logging.debug('成功获取各年份上映电影数量')
        return yearly_movie_count
    except Exception as e:
        print(f"查询各年份上映电影数量时出错，错误信息：{e}")
        logging.error(f'查询各年份上映电影数量时出错: {e}')
        return None