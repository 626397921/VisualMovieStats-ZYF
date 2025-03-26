document.addEventListener('DOMContentLoaded', function () {
    const mainContent = document.querySelector('.main-content');
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const target = this.getAttribute('data-target');
            if (target === "movie-list") {
                // 直接使用AJAX获取电影列表数据
                const xhr = new XMLHttpRequest();
                xhr.open('GET', `/${target}`, true);
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            const response = JSON.parse(xhr.responseText);
                            if (!response.error) {
                                const movies = response.movies;
                                // 清空主内容区域
                                mainContent.innerHTML = '';
                                // 创建统计卡片区域
                                const statsCards = document.createElement('div');
                                statsCards.classList.add('stats-cards');
                                const statsKeys = ['total_movies', 'highest_rating', 'genre_count','most_released_year','max_duration'];
                                statsKeys.forEach(key => {
                                    const card = document.createElement('div');
                                    card.classList.add('stats-card');
                                    const cardContent = document.createElement('div');
                                    cardContent.classList.add('card-content');
                                    const cardText = document.createElement('div');
                                    cardText.classList.add('card-text');
                                    const p = document.createElement('p');
                                    p.textContent = response[key];
                                    const subP = document.createElement('p');
                                    subP.textContent = {
                                        'total_movies': '电影总数',
                                        'highest_rating': '最高电影评分',
                                        'genre_count': '电影种类数',
                                       'most_released_year': '最多电影上映年份',
                                       'max_duration': '最大时长'
                                    }[key];
                                    cardText.appendChild(p);
                                    cardText.appendChild(subP);
                                    cardContent.appendChild(cardText);
                                    card.appendChild(cardContent);
                                    statsCards.appendChild(card);
                                });
                                mainContent.appendChild(statsCards);
                                // 创建电影表格
                                const table = document.createElement('table');
                                table.classList.add('movie-table');
                                const thead = document.createElement('thead');
                                const headerRow = document.createElement('tr');
                                const headers = ['编号', '电影名', '发行时间', '评分', '评价人数', '主演', '类型', '时长'];
                                headers.forEach(header => {
                                    const th = document.createElement('th');
                                    th.textContent = header;
                                    headerRow.appendChild(th);
                                });
                                thead.appendChild(headerRow);
                                table.appendChild(thead);
                                const tbody = document.createElement('tbody');
                                movies.forEach((movie, index) => {
                                    const row = document.createElement('tr');
                                    const cells = [
                                        index + 1,
                                        movie['电影名称'],
                                        movie['上映年份'],
                                        movie['评分'],
                                        movie['评价人数'],
                                        movie['主演'],
                                        movie['类型'],
                                        movie['时长']
                                    ];
                                    cells.forEach(cell => {
                                        const td = document.createElement('td');
                                        td.textContent = cell;
                                        row.appendChild(td);
                                    });
                                    tbody.appendChild(row);
                                });
                                table.appendChild(tbody);
                                mainContent.appendChild(table);
                            } else {
                                mainContent.textContent = '获取电影列表数据失败';
                            }
                        } else {
                            mainContent.textContent = 'AJAX 请求失败: 状态码:'+ xhr.status;
                        }
                    }
                };
                xhr.onerror = function () {
                    mainContent.textContent = '加载页面时发生错误';
                };
                xhr.send();
            } else {
                // 对于其他页面，仍使用原有的加载方式
                const xhr = new XMLHttpRequest();
                xhr.open('GET', `/${target}`, true);
                xhr.onreadystatechange = function () {
                    if (xhr.readyState === 4) {
                        if (xhr.status === 200) {
                            mainContent.innerHTML = xhr.responseText;
                        } else {
                            console.log('AJAX 请求失败:', target, '状态码:', xhr.status);
                        }
                    }
                };
                xhr.onerror = function () {
                    console.log('加载页面时发生错误:', target);
                };
                xhr.send();
            }
        });
    });
});