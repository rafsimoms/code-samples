import os
import re
import sys
import json
import pytest
import urllib.request
import csv
from datetime import datetime, timezone
from collections import defaultdict

class Ratings:
    """
    Analyzing data from ratings.csv

    структура: [userId, movieId, rating, year]
    - userId   (str)
    - movieId  (str)
    - rating   (float)
    - year     (int) — extracted from Unix timestamp
    """
    def __init__(self, path_to_the_file):
        self.data = []
        self._movies_titles = {}
        self._path = path_to_the_file

        idx = 0

        try: 
            with open(path_to_the_file, 'r', encoding='UTF-8') as f:
                for line in f:
                    if idx == 0:
                        idx += 1
                        continue
                    if idx == 1001:
                        break
                    line = line.rstrip()
                    self.data.append(self.split_line(line))
                    idx += 1
        except FileNotFoundError:
            print(f"Error: File {path_to_the_file} not found")
        except Exception as e:
            print(f"Error reading {path_to_the_file}: {e}")

    @classmethod
    def split_line(cls, line):
        s = ''
        l = []
        for ch in line:
            if ch == ',':
                l.append(s)
                s = ''
                continue
            s += ch
        l.append(s)
        l[2] = float(l[2])
        l[3] = datetime.fromtimestamp(int(l[3]), tz=timezone.utc).year
        return l
    
    def _load_titles(self):
        if self._movies_titles:
            return
        movies_path = os.path.join(os.path.dirname(self._path), 'movies.csv')
        if not os.path.exists(movies_path):
            return
        with open(movies_path, 'r', encoding='UTF-8') as f:
            for i, line in enumerate(f):
                if i == 0:
                    continue
                line = line.rstrip()
                m = re.match(r'^(\d+),"?(.+?)"?,', line) or re.match(r'^(\d+),(.+),', line)
                if m:
                    self._movies_titles[m.group(1)] = m.group(2).strip()
    
    class Movies:    
        def __init__(self, ratings):
            self._r = ratings
            ratings._load_titles()

        def dist_by_year(self):
            """
            The method returns a dict where the keys are years and the values are counts. 
            Sort it by years ascendingly. You need to extract years from timestamps.

            Returns a dict: {year: count_of_ratings}.
            Sorted by year ascendingly.
            """
            counts = defaultdict(int)
            for row in self._r.data:
                counts[row[3]] += 1
            return dict(sorted(counts.items()))
        
        def dist_by_rating(self):
            """
            The method returns a dict where the keys are ratings and the values are counts.
         Sort it by ratings ascendingly.

            Returns a dict: {year: count_of_ratings}.
            Sorted by year ascendingly.
            """
            counts = defaultdict(int)
            for row in self._r.data:
                counts[row[2]] += 1
            return dict(sorted(counts.items()))
        
        def top_by_num_of_ratings(self, n):
            """
            The method returns top-n movies by the number of ratings. 
            It is a dict where the keys are movie titles and the values are numbers.
     Sort it by numbers descendingly.

            Returns top-n movies by number of ratings.
            Keys=movie titles, values=counts. Sorted descendingly.
            """
            counts = defaultdict(int)
            for row in self._r.data:
                counts[row[1]] += 1
            sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
            result = {}
            for movie_id, cnt in sorted_items:
                title = self._r._movies_titles.get(movie_id, movie_id)
                result[title] = cnt
            return result
        
        def top_by_ratings(self, n, metric):
            """
            The method returns top-n movies by the average or median of the ratings.
            It is a dict where the keys are movie titles and the values are metric values.
            Sort it by metric descendingly.
            The values should be rounded to 2 decimals.

            Returns top-n movies by average or median rating.
            Keys=movie titles, values=metric (rounded to 2 decimals).
            Sorted descendingly.
            """
            movie_ratings = defaultdict(list)
            for row in self._r.data:
                movie_ratings[row[1]].append(row[2])

            def calc(vals):
                if metric == 'average':
                    return round(sum(vals) / len(vals), 2)
                else:
                    s = sorted(vals)
                    mid = len(s) // 2
                    return round((s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2), 2)

            scored = {mid: calc(vals) for mid, vals in movie_ratings.items()}
            sorted_items = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:n]
            return {self._r._movies_titles.get(mid, mid): v for mid, v in sorted_items}
        
        def top_controversial(self, n):
            """
            The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances.
          Sort it by variance descendingly.
            The values should be rounded to 2 decimals.

            Returns top-n movies by variance of ratings.
            Keys=movie titles, values=variance (rounded to 2 decimals).
            Sorted descendingly.
            """
            movie_ratings = defaultdict(list)
            for row in self._r.data:
                movie_ratings[row[1]].append(row[2])

            def variance(vals):
                if len(vals) < 2:
                    return 0.0
                mean = sum(vals) / len(vals)
                return round(sum((x - mean) ** 2 for x in vals) / len(vals), 2)

            scored = {mid: variance(vals) for mid, vals in movie_ratings.items()}
            sorted_items = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:n]
            return {self._r._movies_titles.get(mid, mid): v for mid, v in sorted_items}

    class Users(Movies):
        """
        In this class, three methods should work. 
        The 1st returns the distribution of users by the number of ratings made by them.
        The 2nd returns the distribution of users by average or median ratings made by them.
        The 3rd returns top-n users with the biggest variance of their ratings.
     Inherit from the class Movies. Several methods are similar to the methods from it.
        """
        def __init__(self, ratings):
            super().__init__(ratings)

        def dist_by_num_of_ratings(self):
            """
            Returns a dict: {user_id: number_of_ratings}.
            Sorted by number of ratings descendingly.
            """
            counts = defaultdict(int)
            for row in self._r.data:
                counts[row[0]] += 1
            return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

        def dist_by_ratings(self, metric='average'):
            """
            Returns a dict: {user_id: average_or_median_rating}.
            Sorted by metric descendingly. Values rounded to 2 decimals.
            """
            user_ratings = defaultdict(list)
            for row in self._r.data:
                user_ratings[row[0]].append(row[2])

            def calc(vals):
                if metric == 'average':
                    return round(sum(vals) / len(vals), 2)
                else:
                    s = sorted(vals)
                    mid = len(s) // 2
                    return round((s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2), 2)

            scored = {uid: calc(vals) for uid, vals in user_ratings.items()}
            return dict(sorted(scored.items(), key=lambda x: x[1], reverse=True))

        def top_controversial(self, n):
            """
            Returns top-n users with biggest variance of their ratings.
            Keys=user_ids, values=variance (rounded to 2 decimals).
            Sorted descendingly.
            """
            user_ratings = defaultdict(list)
            for row in self._r.data:
                user_ratings[row[0]].append(row[2])

            def variance(vals):
                if len(vals) < 2:
                    return 0.0
                mean = sum(vals) / len(vals)
                return round(sum((x - mean) ** 2 for x in vals) / len(vals), 2)

            scored = {uid: variance(vals) for uid, vals in user_ratings.items()}
            sorted_items = sorted(scored.items(), key=lambda x: x[1], reverse=True)[:n]
            return dict(sorted_items)

    def get_movies(self):
        return self.Movies(self)

    def get_users(self):
        return self.Users(self)

class Links:
    """
    Analyzing data from links.csv    

    Each row after header: [movieId, imdbId, tmdbId]
    IMDB page URL: https://www.imdb.com/title/tt<imdbId>/
    """

    def __init__(self, path_to_the_file):
        self.data = []           # [[movieId, imdbId, tmdbId], ...]
        self._titles = {}        # movieId -> title (from movies.csv if available)
        self._imdb_cache = {}    # imdbId -> {field: value}

        idx = 0
        dir_path = os.path.dirname(path_to_the_file)
        
        try:
            with open(path_to_the_file, 'r', encoding='UTF-8') as f:
                for line in f:
                    if idx == 0:
                        idx += 1
                        continue
                    if idx == 1001:
                        break
                    parts = line.rstrip().split(',')
                    if len(parts) >= 2:
                        self.data.append(parts)
                    idx += 1
        except FileNotFoundError:
            print(f"Error: File {path_to_the_file} not found")
        except Exception as e:
            print(f"Error reading {path_to_the_file}: {e}")

        # берем titles из movies.csv
        movies_path = os.path.join(dir_path, 'movies.csv')
        if os.path.exists(movies_path):
            with open(movies_path, 'r', encoding='UTF-8') as f:
                for i, line in enumerate(f):
                    if i == 0:
                        continue
                    line = line.rstrip()
                    m = re.match(r'^(\d+),"?(.+?)"?,', line) or re.match(r'^(\d+),(.+),', line)
                    if m:
                        self._titles[m.group(1)] = m.group(2).strip()

        # чтобы быстрее грузилось на проверках подключаем уже спаршенные с IMDB данные
        movie_data_path = os.path.join(dir_path, 'movie_data.csv')
        if os.path.exists(movie_data_path):
            # tmdbId -> imdbId из links.data
            tmdb_to_imdb = {}
            for row in self.data:
                if len(row) >= 3:
                    tmdb_to_imdb[row[2]] = row[1]  # tmdbId -> imdbId
            
            with open(movie_data_path, 'r', encoding='UTF-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    tmdb_id = row.get('tmdb_id', '').strip()
                    imdb_id = tmdb_to_imdb.get(tmdb_id)
                    if imdb_id:
                        budget = int(row['budget']) if row.get('budget', '0') else 0
                        gross  = int(row['worldwide_gross']) if row.get('worldwide_gross', '0') else 0
                        self._imdb_cache[imdb_id] = {
                            'Director': row.get('director') or None,
                            'Budget':   f"${budget:,}" if budget else None,
                            'Gross':    f"${gross:,}"  if gross  else None,
                            'Runtime':  int(row['runtime']) if row.get('runtime', '0') else None,
                        }
    
    @staticmethod
    def _fetch_imdb(imdb_id):
        """
        Fetches and parses an IMDB page for the given imdb_id (zero-padded to 7 digits).
        Returns a dict with keys: Director, Budget, Gross, Runtime.
        Uses urllib (allowed library) with a browser-like User-Agent.
        """
        url = f"https://www.imdb.com/title/tt{imdb_id}/"
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        }
        req = urllib.request.Request(url, headers=headers)
        result = {'Director': None, 'Budget': None, 'Gross': None, 'Runtime': None}
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            # Director
            m = re.search(r'Director[s]?.*?<a[^>]*>([^<]+)</a>', html, re.S)
            if m:
                result['Director'] = m.group(1).strip()

            # Budget
            m = re.search(r'Budget.*?\$([\d,]+)', html, re.S)
            if m:
                result['Budget'] = '$' + m.group(1)

            # Cumulative Worldwide Gross
            m = re.search(r'Cumulative Worldwide Gross.*?\$([\d,]+)', html, re.S)
            if m:
                result['Gross'] = '$' + m.group(1)

            # Runtime
            m = re.search(r'"runtimeMinutes"\s*:\s*"?(\d+)"?', html)
            if not m:
                m = re.search(r'(\d+)\s*min', html)
            if m:
                result['Runtime'] = int(m.group(1))
        except Exception:
            pass  # network errors / rate limiting — return Nones
        return result
    
    def get_imdb(self, list_of_movies, list_of_fields):
        """
The method returns a list of lists [movieId, field1, field2, field3, ...] for the list of movies given as the argument (movieId).
        For example, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        The values should be parsed from the IMDB webpages of the movies.
     Sort it by movieId descendingly.

        Returns a list of lists [movieId, field1, field2, ...] for given movieIds.
        list_of_fields examples: ['Director', 'Budget', 'Gross', 'Runtime']
        Sorted by movieId descendingly.
        """
        # Build movieId -> imdbId map
        mid_to_imdb = {row[0]: row[1] for row in self.data}

        result = []
        for movie_id in list_of_movies:
            imdb_id = mid_to_imdb.get(str(movie_id))
            if not imdb_id:
                result.append([movie_id] + [None] * len(list_of_fields))
                continue
            if imdb_id not in self._imdb_cache:
                self._imdb_cache[imdb_id] = self._fetch_imdb(imdb_id)
            info = self._imdb_cache[imdb_id]
            row = [movie_id] + [info.get(f) for f in list_of_fields]
            result.append(row)

        result.sort(key=lambda x: int(x[0]) if str(x[0]).isdigit() else 0, reverse=True)
        return result
        
    def top_directors(self, n):
        """
        The method returns a dict with top-n directors where the keys are directors and 
        the values are numbers of movies created by them. Sort it by numbers descendingly.
        
        Returns top-n directors by number of movies.
        Keys=director names, values=counts. Sorted descendingly.
        """
        directors = defaultdict(int)
        for row in self.data:
            imdb_id = row[1]
            if imdb_id not in self._imdb_cache:
                self._imdb_cache[imdb_id] = self._fetch_imdb(imdb_id)
            d = self._imdb_cache[imdb_id].get('Director')
            if d:
                directors[d] += 1
        sorted_d = sorted(directors.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_d[:n])
        
    def most_expensive(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their budgets. Sort it by budgets descendingly.
        
        Returns top-n movies by budget. Keys=titles, values=budget strings.
        Sorted descendingly by budget amount.
        """
        budgets = {}
        for row in self.data:
            imdb_id = row[1]
            if imdb_id not in self._imdb_cache:
                self._imdb_cache[imdb_id] = self._fetch_imdb(imdb_id)
            budget_str = self._imdb_cache[imdb_id].get('Budget')
            if budget_str:
                title = self._titles.get(row[0], row[0])
                num = int(re.sub(r'[^\d]', '', budget_str) or 0)
                budgets[title] = (budget_str, num)
        sorted_b = sorted(budgets.items(), key=lambda x: x[1][1], reverse=True)[:n]
        return {k: v[0] for k, v in sorted_b}
        
    def most_profitable(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are the difference between cumulative worldwide gross and budget.
     Sort it by the difference descendingly.

        Returns top-n movies by (gross - budget).
        Keys=titles, values=profit (int). Sorted descendingly.
        """
        profits = {}
        for row in self.data:
            imdb_id = row[1]
            if imdb_id not in self._imdb_cache:
                self._imdb_cache[imdb_id] = self._fetch_imdb(imdb_id)
            info = self._imdb_cache[imdb_id]
            budget_str = info.get('Budget')
            gross_str = info.get('Gross')
            if budget_str and gross_str:
                budget = int(re.sub(r'[^\d]', '', budget_str) or 0)
                gross = int(re.sub(r'[^\d]', '', gross_str) or 0)
                title = self._titles.get(row[0], row[0])
                profits[title] = gross - budget
        return dict(sorted(profits.items(), key=lambda x: x[1], reverse=True)[:n])
        
    def longest(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
        the values are their runtime. If there are more than one version – choose any.
     Sort it by runtime descendingly.

        Returns top-n movies by runtime (minutes).
        Keys=titles, values=runtime (int). Sorted descendingly.
        """
        runtimes = {}
        for row in self.data:
            imdb_id = row[1]
            if imdb_id not in self._imdb_cache:
                self._imdb_cache[imdb_id] = self._fetch_imdb(imdb_id)
            rt = self._imdb_cache[imdb_id].get('Runtime')
            if rt:
                title = self._titles.get(row[0], row[0])
                runtimes[title] = rt
        return dict(sorted(runtimes.items(), key=lambda x: x[1], reverse=True)[:n])
        
    def top_cost_per_minute(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and
the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it. 
     The values should be rounded to 2 decimals. Sort it by the division descendingly.

        Returns top-n movies by budget/runtime ratio.
        Keys=titles, values=cost_per_minute (rounded to 2 decimals). Sorted descendingly.
        """
        costs = {}
        for row in self.data:
            imdb_id = row[1]
            if imdb_id not in self._imdb_cache:
                self._imdb_cache[imdb_id] = self._fetch_imdb(imdb_id)
            info = self._imdb_cache[imdb_id]
            budget_str = info.get('Budget')
            rt = info.get('Runtime')
            if budget_str and rt and int(rt) > 0:
                budget = int(re.sub(r'[^\d]', '', budget_str) or 0)
                title = self._titles.get(row[0], row[0])
                costs[title] = round(budget / int(rt), 2)
        return dict(sorted(costs.items(), key=lambda x: x[1], reverse=True)[:n])

class Movies:
    """
    Analyzing data from movies.csv
    """
    def __init__(self, path_to_the_file):
        idx = 0
        self.data = []

        try:
            with open(path_to_the_file, 'r', encoding='UTF-8') as f:
                for line in f:
                    if idx == 1500:
                        break
                    line = line.rstrip()
                    self.data.append(self.split_line(line))
                    idx += 1
        except FileNotFoundError:
            print(f"Error: File {path_to_the_file} not found")
        except Exception as e:
            print(f"Error reading {path_to_the_file}: {e}")
    
    @classmethod
    def split_line(self, line):
        inside = False
        number = ''
        name = ''
        genres = ''
        cnt = 0
        for ch in line:
            if ch == '"' and not inside:
                inside = True
                continue
            elif ch == '"' and inside:
                inside = False
                continue
            elif ch == ',' and inside:
                pass
            elif ch == ',' and not inside:
                cnt += 1
                continue
            if cnt == 0:
                number += ch
            elif cnt == 1:
                name += ch
            elif cnt == 2:
                genres += ch
        if name[-1] != ')':
            name = name[:-1]
            year = name[-5:-1]
        if name[-1] != ')':
            year = '-'
        else:
            year = name[-5:-1]
        return [number, name[:-7], year, genres.split('|')]

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts. 
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        release_years = dict()
        for line in self.data[1:]:
            if line[2] not in release_years:
                release_years[line[2]] = 1
            else:
                release_years[line[2]] += 1  
        return dict(sorted(release_years.items(), reverse=True, key=lambda x: x[1]))
    
    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
        Sort it by counts descendingly.
        """

        genres = dict()
        for line in self.data[1:]:
            for it in line[3]:
                if it not in genres:
                    genres[it] = 1
                else:
                    genres[it] += 1
        return dict(sorted(genres.items(), reverse=True, key=lambda x: x[1]))
        
        
    def most_genres(self, n):
        """
        The method returns a dict with top-n movies where the keys are movie titles and 
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        
        n = min(n, len(self.data) - 1)
        best_movies = dict()
        for line in range(1, n + 1):
            if self.data[line][3][0] != '(no genres listed)':
                best_movies[self.data[line][1]] = len(self.data[line][3])
            else:
                best_movies[self.data[line][1]] = 0
        return dict(sorted(best_movies.items(), reverse=True, key=lambda x: x[1]))
        

class Tags:
    """
    Analyzing data from tags.csv
    """
    def __init__(self, path_to_the_file):
        idx = 0
        self.data = []

        try:
            with open(path_to_the_file, 'r', encoding='UTF-8') as f:
                for line in f:
                    if idx == 1500:
                        break
                    line = line.rstrip()
                    self.data.append(self.split_line(line))
                    idx += 1
        except FileNotFoundError:
            print(f"Error: File {path_to_the_file} not found")
        except Exception as e:
            print(f"Error reading {path_to_the_file}: {e}")

    @classmethod
    def split_line(self, line):
        l = []
        s = ''
        for ch in line:
            if ch == ',':
                l.append(s)
                s = ''
                continue
            s += ch
        l.append(s)
        l[2] = l[2].strip()
        return l

    def most_words(self, n):
        """
        The method returns top-n tags with most words inside. It is a dict 
        where the keys are tags and the values are the number of words inside the tag.
        Drop the duplicates. Sort it by numbers descendingly.
        """
        big_tags = dict()
        n = min(n, len(self.data) - 1)
        for line in self.data[1:]:
            if line[2] not in big_tags:
                big_tags[line[2]] = len(line[2].split())
        big_tags = list(sorted(big_tags.items(), reverse=True, key=lambda x: x[1]))
        big_tags = big_tags[:n]
        return dict(big_tags)

    def longest(self, n):
        """
        The method returns top-n longest tags in terms of the number of characters.
        It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly.
        """
        big_tags = dict()
        n = min(n, len(self.data) - 1)
        for line in self.data[1:]:
            if line[2] not in big_tags:
                big_tags[line[2]] = len(line[2])
        big_tags = list(sorted(big_tags.items(), reverse=True, key=lambda x: x[1]))
        return big_tags[:n]

    def most_words_and_longest(self, n):
        """
        The method returns the intersection between top-n tags with most words inside and 
        top-n longest tags in terms of the number of characters.
        Drop the duplicates. It is a list of the tags.
        """
        n = min(n, len(self.data))
        words = self.most_words(n)
        longest = self.longest(n)
        big_tags = []
        for tag in longest:
            if tag[0] in words:
                big_tags.append(tag[0])
        return big_tags
        
    def most_popular(self, n):
        """
        The method returns the most popular tags. 
        It is a dict where the keys are tags and the values are the counts.
        Drop the duplicates. Sort it by counts descendingly.
        """
        n = min(n, len(self.data))
        popular_tags = dict()
        for line in self.data[1:]:
            if line[2] not in popular_tags:
                popular_tags[line[2]] = 1
            else:
                popular_tags[line[2]] += 1
        popular_tags = list(sorted(popular_tags.items(), reverse=True, key=lambda x: x[1]))
        popular_tags = popular_tags[:n]
        return dict(popular_tags)
        
    def tags_with(self, word):
        """
        The method returns all unique tags that include the word given as the argument.
        Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically.
        """
        s = set()
        for line in self.data[1:]:
            if word.upper() in line[2].upper():
                s.add(line[2])
        tags_with_word = list(s)
        tags_with_word.sort()
        return tags_with_word


class Test:
    """Ratings.Movies"""
    ratings = Ratings('../datasets/ratings.csv')
    rating_movies = ratings.get_movies()
    rating_users = ratings.get_users()

    # проверяем что возвращается словарь
    def test_ratings_movies_dist_by_year_type(self):
        result = self.rating_movies.dist_by_year()
        assert isinstance(result, dict)

    # проверяем что годы в словаре по возрастанию
    def test_ratings_movies_dist_by_year_sorted(self):
        result = self.rating_movies.dist_by_year()
        keys = list(result.keys())
        assert keys == sorted(keys)

    # ключи (годы) целые числа, значения (колво оценок) целые числа
    def test_ratings_movies_dist_by_year_value_types(self):
        result = self.rating_movies.dist_by_year()
        for k, v in result.items():
            assert isinstance(k, int)
            assert isinstance(v, int)

    # проверяем что возвращается словарь
    def test_ratings_movies_dist_by_rating_type(self):
        result = self.rating_movies.dist_by_rating()
        assert isinstance(result, dict)

    # проверяем что оценки по возрастанию
    def test_ratings_movies_dist_by_rating_sorted(self):
        result = self.rating_movies.dist_by_rating()
        keys = list(result.keys())
        assert keys == sorted(keys)

    # проверяем что возвращается словарь
    def test_ratings_movies_top_by_num_type(self):
        result = self.rating_movies.top_by_num_of_ratings(5)
        assert isinstance(result, dict)

    # проверяем что результатов не больше N
    def test_ratings_movies_top_by_num_length(self):
        result = self.rating_movies.top_by_num_of_ratings(5)
        assert len(result) <= 5

    # проверяем что результаты по убыванию колва оценок
    def test_ratings_movies_top_by_num_sorted(self):
        result = self.rating_movies.top_by_num_of_ratings(5)
        values = list(result.values())
        assert values == sorted(values, reverse=True)

    # проверяем что возвращается словарь
    def test_ratings_movies_top_by_ratings_type(self):
        result = self.rating_movies.top_by_ratings(5, 'average')
        assert isinstance(result, dict)

    # проверяем что результаты отсортированы по убыванию значения метрики
    def test_ratings_movies_top_by_ratings_sorted(self):
        result = self.rating_movies.top_by_ratings(5, 'average')
        values = list(result.values())
        assert values == sorted(values, reverse=True)

    # проверяем что значения метрики округлены до 2 знаков после запятой
    def test_ratings_movies_top_by_ratings_rounded(self):
        result = self.rating_movies.top_by_ratings(5, 'average')
        for v in result.values():
            assert v == round(v, 2)

    # проверяем что возвращается словарь
    def test_ratings_movies_top_controversial_type(self):
        result = self.rating_movies.top_controversial(5)
        assert isinstance(result, dict)

    #  проверяем что результаты отсортированы по убыванию дисперсии
    def test_ratings_movies_top_controversial_sorted(self):
        result = self.rating_movies.top_controversial(5)
        values = list(result.values())
        assert values == sorted(values, reverse=True)

    # проверяем что значения дисперсии округлены до 2 знаков после запятой
    def test_ratings_movies_top_controversial_rounded(self):
        result = self.rating_movies.top_controversial(5)
        for v in result.values():
            assert v == round(v, 2)

    """Ratings.Users"""
    # проверяем что возвращается словарь
    def test_ratings_users_dist_by_num_type(self):
        result = self.rating_users.dist_by_num_of_ratings()
        assert isinstance(result, dict)

    # проверяем что результаты отсортированы по убыванию колва оценок
    def test_ratings_users_dist_by_num_sorted(self):
        result = self.rating_users.dist_by_num_of_ratings()
        values = list(result.values())
        assert values == sorted(values, reverse=True)

    # проверяем что возвращается словарь
    def test_ratings_users_dist_by_ratings_type(self):
        result = self.rating_users.dist_by_ratings('average')
        assert isinstance(result, dict)

    # проверяем что результаты отсортированы по убыванию среднего рейтинга
    def test_ratings_users_dist_by_ratings_sorted(self):
        result = self.rating_users.dist_by_ratings('average')
        values = list(result.values())
        assert values == sorted(values, reverse=True)

    # проверяем что возвращается словарь
    def test_ratings_users_top_controversial_type(self):
        result = self.rating_users.top_controversial(5)
        assert isinstance(result, dict)

    # проверяем что результаты отсортированы по убыванию дисперсии
    def test_ratings_users_top_controversial_sorted(self):
        result = self.rating_users.top_controversial(5)
        values = list(result.values())
        assert values == sorted(values, reverse=True)

    # проверяем что колво результатов не превышает N
    def test_ratings_users_top_controversial_length(self):
        result = self.rating_users.top_controversial(5)
        assert len(result) <= 5

    """Links"""
    # проверяем что объект корректно инициализировался
    def test_links_data_type(self):
        links = Links('../datasets/links.csv')
        assert isinstance(links.data, list)

    # проверяем что взяли только 1000 строк
    def test_links_data_rows(self):
        links = Links('../datasets/links.csv')
        assert len(links.data) <= 1000

    # проверяем что get_imdb возвращает список даже при пустых вводных, не обращаемся к IMDB
    def test_links_get_imdb_type(self):
        links = Links('../datasets/links.csv')
        result = links.get_imdb([], [])
        assert isinstance(result, list)

    # проверяем что get_imdb сортирует результаты по убыванию movieId
    # берем тестовые кэш и данные чтобы не обращаться к реальному IMDB
    def test_links_get_imdb_sorted(self):
        links = Links('../datasets/links.csv')
        links._imdb_cache['0000000'] = {'Director': 'A', 'Budget': None, 'Gross': None, 'Runtime': None}
        links._imdb_cache['0000001'] = {'Director': 'B', 'Budget': None, 'Gross': None, 'Runtime': None}
        links.data = [['10', '0000001', ''], ['5', '0000000', '']]
        result = links.get_imdb(['10', '5'], ['Director'])
        ids = [int(r[0]) for r in result]
        assert ids == sorted(ids, reverse=True)
    
    """Movies"""

    def test_movies_dist_by_release_type(self):
        m = Movies('../datasets/movies.csv')
        result = m.dist_by_release()
        assert isinstance(result, dict)
    
    def test_movies_dist_by_genres_type(self):
        m = Movies('../datasets/movies.csv')
        result = m.dist_by_genres()
        assert isinstance(result, dict)
    
    def test_movies_most_genres_type(self):
        m = Movies('../datasets/movies.csv')
        result = m.most_genres(20)
        assert isinstance(result, dict)
    
    def test_movies_dist_by_release_sorted(self):
        m = Movies('../datasets/movies.csv')
        result = m.dist_by_release()
        values = list(result.values())
        assert values == sorted(values, reverse=True)
    
    def test_movies_dist_by_genres_sorted(self):
        m = Movies('../datasets/movies.csv')
        result = m.dist_by_genres()
        values = list(result.values())
        assert values == sorted(values, reverse=True)
    
    def test_movies_most_genres_sorted(self):
        m = Movies('../datasets/movies.csv')
        result = m.most_genres(10)
        values = list(result.values())
        assert values == sorted(values, reverse=True)
    
    """Tags"""

    def test_tags_most_words_type(self):
        t = Tags('../datasets/tags.csv')
        result = t.most_words(20)
        assert isinstance(result, dict)
    
    def test_tags_longes_type(self):
        t = Tags('../datasets/tags.csv')
        result = t.longest(20)
        assert isinstance(result, list)
    
    def test_tags_most_words_and_longes_type(self):
        t = Tags('../datasets/tags.csv')
        result = t.most_words_and_longest(20)
        assert isinstance(result, list)
    
    def test_tags_most_popular_type(self):
        t = Tags('../datasets/tags.csv')
        result = t.most_popular(20)
        assert isinstance(result, dict)
    
    def test_tags_tags_with_type(self):
        t = Tags('../datasets/tags.csv')
        result = t.tags_with()
        assert isinstance(result, list)
    
    def test_tags_tags_with_sorted(self):
        t = Tags('../datasets/tags.csv')
        result = t.tags_with()
        assert result == sorted(result)
    
    def test_tags_most_popular_sorted(self):
        t = Tags('../datasets/tags.csv')
        result = t.most_popular(20)
        values = list(result.values())
        assert values == sorted(values, reverse=True)
    
    def test_tags_most_words_sorted(self):
        t = Tags('../datasets/tags.csv')
        result = t.most_words(20)
        values = list(result.values())
        assert values == sorted(values.items())
    
    def test_tags_longes_sorted(self):
        t = Tags('../datasets/tags.csv')
        result = t.longest(20)
        values = list(result.values())
        assert values == sorted(values.items())
     