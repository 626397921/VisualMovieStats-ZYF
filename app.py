import os
from flask import Flask, render_template, request, jsonify
from database import init_db, insert_data_to_db, get_movie_list, get_yearly_movie_count
import logging
app = Flask(__name__)
# 可在这里修改每页显示的数据数量
PER_PAGE = 7


# 首页路由
@app.route('/')
def index():
    return render_template('index.html')


# 新增homepage路由
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/movie-list')
def movie_list():
    page = request.args.get('page', 1, type=int)
    logging.debug(f"Received page number: {page}")
    result = get_movie_list(page, PER_PAGE)
    if result:
        total_movies, highest_rating, genre_count, most_released_year, max_duration, movies, total_pages = result
        logging.debug(f"Total movies: {total_movies}, Total pages: {total_pages}")
        return jsonify({
            'total_movies': total_movies,
            'highest_rating': highest_rating,
            'genre_count': genre_count,
            'most_released_year': most_released_year,
            'max_duration': max_duration,
            'movies': movies,
            'total_pages': total_pages
        })
    else:
        logging.error("Failed to get movie list data")
        return jsonify({"error": "获取电影列表数据失败"}), 500

# 各年份上映电影数量页面路由
@app.route('/movie-release-count-by-year')
def movie_release_count_by_year():
    try:
        return render_template('movie-release-count-by-year.html')
    except Exception as e:
        print(f"渲染movie-release-count-by-year.html时出错: {e}")
        return "渲染页面时出错", 500


# 各年份上映电影数量数据接口
@app.route('/api/yearly-movie-count')
def api_yearly_movie_count():
    try:
        # 这里需要调用获取数据的函数，假设为 get_yearly_movie_count
        yearly_movie_count = get_yearly_movie_count()
        return jsonify(yearly_movie_count)
    except Exception as e:
        print(f"获取各年份上映电影数量时出错: {e}")
        return jsonify({"error": "获取数据失败"}), 500


# 电影类型占比页面路由
@app.route('/genre-ratio')
def genre_ratio():
    try:
        return render_template('genre-ratio.html')
    except Exception as e:
        print(f"渲染genre-ratio.html时出错: {e}")
        return "渲染页面时出错", 500


# 电影评分抽样页面路由
@app.route('/rating-sample')
def rating_sample():
    try:
        return render_template('rating-sample.html')
    except Exception as e:
        print(f"渲染rating-sample.html时出错: {e}")
        return "渲染页面时出错", 500


# 电影榜单TOP10页面路由
@app.route('/top-10-list')
def top_10_list():
    try:
        return render_template('top-10-list.html')
    except Exception as e:
        print(f"渲染top-10-list.html时出错: {e}")
        return "渲染页面时出错", 500


# 电影评价人数TOP20页面路由
@app.route('/top-20-reviewers')
def top_20_reviewers():
    try:
        return render_template('top-20-reviewers.html')
    except Exception as e:
        print(f"渲染top-20-reviewers.html时出错: {e}")
        return "渲染页面时出错", 500


if __name__ == '__main__':
    if not os.path.exists('movies.db'):
        init_db()
        insert_data_to_db()
    app.run(debug=True)