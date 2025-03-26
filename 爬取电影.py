import requests
from bs4 import BeautifulSoup
import time
import random
import csv
import os
import re
from kdl import Auth, Client
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 多个 User-Agent 列表
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
]

# 请替换为你真实的 secret_id 和 secret_key
secret_id = "onqw9eidumf0f0br6sss"
secret_key = "p3mrxo0a31mv26bx6ntq4tj166d0fv0a"

# 你的用户名、密码和白名单
username = "d2851303825"
password = "s2q3c6de"
whitelist_ip = ["27.156.254.55"]

# 初始化认证和客户端
auth = Auth(secret_id, secret_key)
client = Client(auth, timeout=(10, 15), max_retries=3)


def setup_proxy_and_headers(proxy):
    """设置代理和请求头"""
    proxy_dict = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
    # 随机选择一个 User-Agent
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }
    return proxy_dict, headers


def get_proxy_from_sdk():
    max_retries = 30  # 增加重试次数
    retry_delay = 5
    for i in range(max_retries):
        try:
            # 设置 IP 白名单
            client.set_ip_whitelist(whitelist_ip)
            logging.info(f"成功设置 IP 白名单: {whitelist_ip}")

            # 获取 1 个私密代理 IP，格式为文本
            ips = client.get_dps(1, sign_type='hmacsha1', format='text')
            logging.info("获取到的私密代理 IP：")
            logging.info(ips)

            # 检查获取的私密代理 IP 是否有效
            is_valid = client.check_dps_valid(ips)
            logging.info("私密代理 IP 有效性检查结果：")
            logging.info(is_valid)

            if is_valid:
                time.sleep(1)
                return ips
            else:
                logging.warning("获取的代理 IP 无效")
        except Exception as e:
            if "[KdlException] code: -1" in str(e):
                logging.warning(f"白名单正在修改，等待 {retry_delay} 秒后重试（第 {i + 1} 次）")
                time.sleep(retry_delay)
            elif "[KdlException] code: -120" in str(e):
                logging.warning("接口调用频率超出限制，等待 1 秒后重试")
                time.sleep(1)
            else:
                logging.error(f"操作过程中出现错误: {e}")
    logging.error("多次重试后仍无法获取代理 IP，将继续尝试下一次请求时获取")
    return None


def save_image(img_url, title, proxy_dict, headers):
    """保存图片到指定目录"""
    save_dir = r'C:\Users\Administrator\Desktop\电影图片'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    try:
        logging.info(f"开始请求图片: {img_url}")
        response = requests.get(img_url, headers=headers, proxies=proxy_dict, timeout=60)
        response.raise_for_status()
        logging.info(f"成功获取图片: {img_url}")
        # 获取图片的文件扩展名
        file_extension = img_url.split('.')[-1]
        # 确保文件扩展名合法，若不合法则使用默认扩展名
        if not file_extension.isalpha() or len(file_extension) > 5:
            file_extension = 'jpg'
        file_name = os.path.join(save_dir, f"{title}.{file_extension}")
        with open(file_name, 'wb') as f:
            f.write(response.content)
        logging.info(f"成功保存图片: {file_name}")
    except requests.exceptions.RequestException as e:
        logging.error(f"请求图片 {img_url} 时出错: {e}")
    except Exception as e:
        logging.error(f"保存图片 {img_url} 时出现未知错误: {e}")


def get_movie_info(movie_url):
    max_retries = 15  # 增加重试次数
    retries = 0
    while retries < max_retries:
        proxy = get_proxy_from_sdk()
        if not proxy:
            logging.warning("无法获取代理 IP，等待一段时间后重试...")
            time.sleep(10)
            retries += 1
            continue
        proxy_dict, headers = setup_proxy_and_headers(proxy)
        try:
            response = requests.get(movie_url, headers=headers, proxies=proxy_dict, timeout=15)
            response.raise_for_status()
            logging.info(f"成功使用代理 IP {proxy} 访问 {movie_url}。")
            soup = BeautifulSoup(response.text, 'lxml')

            # 提取电影 ID
            movie_id = movie_url.split('/')[-2]

            # 提取电影名字
            title_span = soup.find('span', property='v:itemreviewed')
            title = title_span.text if title_span else ''

            # 提取电影图片链接
            img = soup.find('img', rel='v:image')
            if img:
                img_url = img['src']
                save_image(img_url, title, proxy_dict, headers)
            else:
                img_url = ''

            genres = [genre.text for genre in soup.find_all('span', property='v:genre')]
            info_div = soup.find('div', id='info')
            if info_div is None:
                logging.warning(f"未找到电影 {movie_url} 的基础信息。")
                info = ''
            else:
                info = info_div.text.strip().replace('\n', ' ')

            # 提取上映年份
            year_span = soup.find('span', class_='year')
            if year_span:
                year = year_span.text.strip('()')
            else:
                year = ''

            # 提取电影时长
            duration_match = re.search(r'片长: *(\d+)分钟', info)
            if duration_match:
                duration = duration_match.group(1)
            else:
                duration = ''

            summary_span = soup.find('span', property='v:summary')
            summary = summary_span.text.strip() if summary_span else ''

            casts = [cast.text for cast in soup.find_all('a', rel='v:starring')[:10]]

            rating_strong = soup.find('strong', property='v:average')
            rating = rating_strong.text if rating_strong else ''

            # 提取评价人数
            rating_num = soup.find('span', property='v:votes')
            rating_num = rating_num.text if rating_num else ''

            hot_reviews = []
            review_url = movie_url + 'comments?status=P'
            logging.info(f"开始尝试获取电影 {movie_url} 的热评信息...")
            review_response = requests.get(review_url, headers=headers, proxies=proxy_dict, timeout=15)
            review_response.raise_for_status()
            review_soup = BeautifulSoup(review_response.text, 'lxml')
            review_divs = review_soup.find_all('div', class_='comment-item')
            for review_div in review_divs[:5]:
                review_span = review_div.find('span', class_='short')
                review_text = review_span.text if review_span else ''
                hot_reviews.append(review_text)

            return {
                '电影ID': movie_id,
                '电影名称': title,
                '图片链接': img_url,
                '类型': ', '.join(genres),
                '基础信息': info,
                '上映年份': year,
                '时长': duration,
                '简介': summary,
                '主演': ', '.join(casts),
                '评分': rating,
                '评价人数': rating_num,
                '热评': ', '.join(hot_reviews)
            }
        except requests.exceptions.ProxyError as e:
            logging.warning(f"使用代理 IP {proxy} 访问 {movie_url} 时发生代理错误: {e}，重试中...")
            retries += 1
        except requests.exceptions.Timeout:
            logging.warning(f"访问 {movie_url} 时请求超时，重试中...")
            retries += 1
        except Exception as e:
            logging.error(f"访问 {movie_url} 时发生错误: {e}，重试中...")
            retries += 1
    logging.error(f"多次重试后仍无法访问 {movie_url}，跳过该电影。")
    return None


def get_crawled_movies(csv_file):
    """获取已爬取的电影名称"""
    if not os.path.exists(csv_file):
        logging.info(f"文件 {csv_file} 不存在，返回空集合。")
        return set()
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if '电影名称' in fieldnames:
            crawled = {row['电影名称'] for row in reader}
            logging.info(f"成功获取 {len(crawled)} 部已爬取的电影名称。")
            return crawled
        else:
            logging.info(f"文件 {csv_file} 中没有 '电影名称' 列，返回空集合。")
            return set()


def batch_crawl_movies():
    # 获取当前用户的桌面路径
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    # 构建完整的文件路径
    csv_file = os.path.join(desktop_path, '电影.csv')

    file_exists = os.path.isfile(csv_file)
    fieldnames = ['电影ID', '电影名称', '图片链接', '类型', '基础信息', '上映年份', '时长', '简介', '主演', '评分',
                  '评价人数', '热评']
    crawled_movies = get_crawled_movies(csv_file)
    if len(crawled_movies) == 199:
        logging.info("已检测到 199 部已爬取的电影，将跳过这些电影。")
    with open(csv_file, 'a', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        crawled_count = len(crawled_movies)
        page_start = 0
        while crawled_count < 250:
            movie_links = []
            proxy = get_proxy_from_sdk()
            if not proxy:
                logging.warning("无法获取代理 IP，等待一段时间后重试...")
                time.sleep(10)
                continue
            proxy_dict, headers = setup_proxy_and_headers(proxy)
            url = f'https://movie.douban.com/top250?start={page_start}'
            logging.info(f"开始处理页面 {url}...")
            try:
                response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=15)
                response.raise_for_status()
                logging.info(f"成功使用代理 IP {proxy} 访问 {url}。")
                soup = BeautifulSoup(response.text, 'lxml')
                items = soup.find_all('div', class_='item')
                for item in items:
                    movie_link = item.find('a')['href']
                    movie_links.append(movie_link)
                for movie_link in movie_links:
                    if crawled_count >= 250:
                        break
                    movie_info = get_movie_info(movie_link)
                    if movie_info:
                        if movie_info['电影名称'] not in crawled_movies:
                            crawled_count += 1
                            crawled_movies.add(movie_info['电影名称'])
                            logging.info(f"成功获取电影 {movie_info['电影名称']} 的信息。")
                            writer.writerow(movie_info)
                        else:
                            logging.info(f"电影 {movie_info['电影名称']} 已爬取，跳过。")
                    else:
                        logging.info(f"未能获取电影 {movie_link} 的信息，跳过。")
                page_start += 25  # 每处理完一页，更新起始位置
            except requests.exceptions.ProxyError as e:
                logging.warning(f"处理页面 {url} 时发生代理异常: {e}，等待一段时间后重试...")
                time.sleep(10)
            except requests.exceptions.Timeout:
                logging.warning(f"处理页面 {url} 时请求超时，等待一段时间后重试...")
                time.sleep(10)
            except Exception as e:
                logging.error(f"处理页面 {url} 时发生异常: {e}，等待一段时间后重试...")
                time.sleep(10)


if __name__ == "__main__":
    logging.info(f"开始批量爬取电影数据，共爬取 250 部电影。")
    batch_crawl_movies()
