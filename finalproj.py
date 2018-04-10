import requests
import json
from bs4 import BeautifulSoup
import sys
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go
#QUESTIONS:
#1. How to write test cases
#2. Check to see if table okay (list parts)
#3. Joing the table and the data processing for plotly (is okay that i use some part classes)
#4. Does my project add up to enough points
#5. IMDB sometime does not let me do anymore scraping what should i do when this happens? I am afraid to delete my cache because i think if i do the website wont let me collect anymore data
#6. Plotly charts how do i add a title

#------------------LIST OF THINGS TO DO:
#1. Assign theater objects Ids in the class (do this by when inserting theters have own counter )
#2. Instead of grabbing data from movies using name grab it using IDs
num = 0
DBNAME = 'Imdb.sql'
#cache just the html for the sites
CACHE_FNAME = 'cache_theaters.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

CACHE = 'cache_movies.json'
try:
    cache = open(CACHE, 'r')
    contents = cache.read()
    CACHE_DICTION_MOVIES = json.loads(contents)
    cache.close()
except:
    CACHE_DICTION_MOVIES = {}
def params_unique_combination(baseurl):
      return baseurl
def cache_theaters(baseurl):
    unique_ident = params_unique_combination(baseurl)
    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]
    else:
        resp = requests.get(baseurl)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]
def cache_movies(baseurl):
    unique_ident = params_unique_combination(baseurl)
    if unique_ident in CACHE_DICTION_MOVIES:
        return CACHE_DICTION_MOVIES[unique_ident]
    else:
        resp = requests.get(baseurl)
        CACHE_DICTION_MOVIES[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION_MOVIES)
        fw = open(CACHE,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION_MOVIES[unique_ident]
#defined classes
class Theater():
    def __init__(self, name, url,street_address,city,state,zip,list_movies):
        self.theater_name = name
        self.theater_url = url
        self.list_movies = list_movies

        self.street_address = street_address
        self.city = city
        self.state = state
        self.zip = zip
    def __str__(self):
        return "{}: {}, {} {}, {}".format(self.theater_name,self.street_address,self.city,self.state,self.zip)
class Movie():
    def __init__(self, name, year, time, url, rating, genre, descrip, directors, num_directors, stars, num_stars, more_details_url, gross = "No Gross", weekend="No Opening Weekend Usa", budget="No Budget", cumulative = "No Cumulative Worldwide Gross"):
        self.movie_name = name
        self.movie_year = year
        self.movie_time = time
        self.movie_url = url
        self.movie_rating = rating
        self.movie_genre = str(genre)
        self.movie_descrip = descrip
        self.movie_directors = str(directors)
        self.movie_number_of_directors = num_directors
        self.movie_stars = str(stars)
        self.movie_number_of_stars = num_stars
        self.movie_more_details_url = more_details_url
        self.movie_gross_usa = gross
        self.movie_opening_weekend_usa = weekend
        self.movie_budget = budget
        self.movie_worldwide_gross = cumulative
    def __str__(self):
        return '''{}({})\n\tRating: {} \n\tMinutes: {} \n\tGenre: {} \n\tDirected by: {} \n\tStars: {}\n\tDescription:\n\t\t {}\n\tMONEY:\n\t\t Budget: {}\n\t\t Gross Profit in the USA: {}\n\t\t Opening Weekend in the USA: {}\n\t\t Cumulative Worldwide Gross: {}'''.format(self.movie_name,self.movie_year,self.movie_rating,self.movie_time,self.movie_genre,self.movie_directors,self.movie_stars,self.movie_descrip,self.movie_budget,self.movie_gross_usa,self.movie_opening_weekend_usa, self.movie_worldwide_gross)
#QUESTIONS:
#1. list_movietheaters: ask about not cachining the list of movies because they update everyday
#caching
#can cache list_movietheaters
#movie theaters within 5,10,20,and 30 miles away

def list_movietheaters(zip_code):
    zip_code = zip_code
    baseurl = "http://www.imdb.com"
    url = "http://www.imdb.com/showtimes/location/US/{}".format(zip_code)
    #page_text = requests.get(url).text
    page_text= cache_theaters(url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    content = page_soup.find_all("span", itemprop = "name")
    #print(content)
    #content = page_soup.find_all("h5", class_ = "li_group")
    list_theaters = []
    num = 0
    for x in content:
        theater_name = x.text
        theater_link = x.find("a")['href']
        full_url = baseurl + theater_link
        #uncomment and comment page_text for most recent movie list
        # page_text= requests.get(full_url).text
        page_text = cache_theaters(full_url)
        page_soup = BeautifulSoup(page_text, 'html.parser')
        content =  page_soup.find_all("div", class_= "info")
        movies = []
        for y in content:
            mov = y.find('h3').text.strip()
            list_mov= mov.split("(")
            movie_name = list_mov[0]
            movies.append(movie_name)
        #content = page_soup.find_all(class_= "article listo st")
        #content = page_soup.find_all("div", itemtype= "http://schema.org/PostalAddress")
        street_address= page_soup.find("span",itemprop="streetAddress").text
        city = page_soup.find(itemprop="addressLocality").text
        state = page_soup.find(itemprop="addressRegion").text
        zip = page_soup.find(itemprop="postalCode").text
        class_theaters = Theater(name = theater_name,url =full_url,street_address = street_address,city= city,state= state,zip=zip,list_movies = movies)
        list_theaters.append(class_theaters)
    # for x in list_theaters:
    #     movie_information(x)
    insert_Theaters(list_theaters,zip_code)
    return list_theaters

# content =  page_soup.find_all("div", class_= "info")
# for y in content:
#     movie_name = y.find('h3').text.strip()
#     print(movie_name)
#     movies.append(movie_name)

#this function takes in a theater class object
def movie_information(theater_class_object):
    baseurl = "http://www.imdb.com"
    url = theater_class_object.theater_url
    #page_text = requests.get(url).text
    page_text = cache_theaters(url)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    #content= page_soup.find_all("div",class_="description")
    #print(content)
    content =  page_soup.find_all("div", class_= "info")
    #content = page_soup.find_all("div",class_="list_item even",itemtype="http://schema.org/Movie")
    movies =[]
    for y in content:
        #movie_name = y.find("span",itemprop= "name").text.strip()
        mov = y.find('h3').text.strip()
        list_mov= mov.split("(")
        movie_name = list_mov[0]
        try:
            movie_year = list_mov[1][:-1]
        except:
            movie_year = "No Movie Year"
        try:
            time = y.find("time",itemprop = "duration").text.strip().split()[0]
        except:
            time = "No Time"
        try:
            rating_info = y.find("span", itemprop = "contentRating")
            rating = rating_info.find("img")["title"].strip()
        except:
            rating = "No Rating"
        movie_url = y.find('a')['href']
        full_url = baseurl + movie_url
        page_text = cache_movies(full_url)
        page_soup = BeautifulSoup(page_text, 'html.parser')
        c = page_soup.find_all("td", class_= "overview-top")
        for x in c:
            g = x.find_all("span", itemprop = "genre")
            genre = []
            for s in g:
                genre.append(s.text.strip())
            descrip = x.find("div", class_="outline", itemprop = "description").text.strip()
            d = x.find_all("span", itemprop= "director")
            director = []
            for f in d:
                dir = f.find("a").text.strip()
                director.append(dir)
            number_of_directors = len(director)
            a = x.find_all("span", itemprop = "actors")
            stars= []
            for actor in a:
                act = actor.find("a").text
                stars.append(act)
            number_of_stars = len(stars)

            link = x.find_all("h4",itemprop ="name")
            #print(link)
            for l in link:
                link = l.find("a")['href']
            movie_url = baseurl + link
            page_text = cache_movies(movie_url)
            page_soup = BeautifulSoup(page_text, 'html.parser')
            # info = page_soup.find_all("div",class_="article",id="titleDetails")
            # for z in info:
            detail_info = page_soup.find_all("div",class_= "txt-block")
            #print(detail_info)
            gross = "No Gross"
            weekend = "No Opening Weekend Usa"
            budget = "No Budget"
            cumulative = "No Cumulative Worldwide Gross"
            for detail in detail_info:
                try:
                    d = detail.find("h4",class_= "inline").text.strip()
                    if d == "Gross USA:":
                        gross = detail.text.strip()
                        gross = gross.split()[:3]
                        #print(gross)
                        gross= " ".join(gross)[:-1].split()[-1][1:]
                        #print(gross)
                    # else:
                    #     gross = "No Gross USA"
                        #print(gross)
                    if d == "Opening Weekend USA:":
                        weekend = detail.text.strip()
                        weekend = weekend.split()[:4]
                        weekend =" ".join(weekend)[:-1].split()[-1][1:]
                        #print(weekend)
                    # else:
                    #     weekend = "No Opening Weekend USA"
                        #print(weekend)
                    if d == "Budget:":
                        budget = detail.text.strip()
                        budget = budget.split(":")[1].split("(")[0][1:]
                        #print(budget)
                    # else:
                    #     budget = "No Budget"
                        #print(budget)
                    if d == "Cumulative Worldwide Gross:":
                        cumulative = detail.text.strip()
                        cumulative= cumulative.split()[:4]
                        cumulative=" ".join(cumulative)[:-1].split()[-1][1:]
                except:
                    #print("except")
                    continue

            mov_object = Movie(name = movie_name, year = movie_year, time = time ,url = full_url, rating = rating, genre = genre, descrip = descrip, directors = director, num_directors = number_of_directors, stars = stars, num_stars = number_of_stars, more_details_url= movie_url, gross = gross, weekend= weekend, budget = budget, cumulative = cumulative)
            movies.append(mov_object)
            # print(movie_name)
            # print(movie_year)
            # print(time)
            # print(full_url)
            # print(descrip)
            # print(director)
            # print(number_of_directors)
            # print(stars)
            # print(number_of_stars)
            # print(movie_url)
            # print(gross)
            # print(weekend)
            # print(budget)
    # print(movies)
    insert_Movies(movies,theater_class_object)
    return movies
# movies = list_movietheaters("48104")
# mov = movie_information(movies[0])
# for x in mov:
#     print(x.movie_budget,x.movie_gross_usa,x.movie_opening_weekend_usa)
# for x in mov:
#     print(x.movie_name)

#making the database:
def init_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    statement = '''
        DROP TABLE IF EXISTS 'Movies';
    '''
    cur.execute(statement)
    statement = '''
        DROP TABLE IF EXISTS 'Theaters';
    '''
    cur.execute(statement)
    conn.commit()
    #left out these three from the table:
    #self.movie_url = url
    #self.movie_descrip = descrip
    #self.movie_more_details_url = more_details_url
    statement = '''
        CREATE TABLE 'Movies' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'ReleaseYear' INTEGER,
            'Minutes' INTEGER,
            'Rating' TEXT,
            'Genre' TEXT NOT NULL,
            'Directors' TEXT NOT NULL,
            'NumberOfDirectors' INTEGER NOT NULL,
            'Stars' TEXT NOT NULL,
            'NumberOfStars' INTEGER NOT NULL,
            'Budget' INTEGER,
            'GrossProfitUSA' INTEGER,
            'OpeningWeekendUSA' INTEGER,
            'CumulativeWorldwideGross' INTEGER
        );
    '''
    cur.execute(statement)
    conn.commit()
    #self.theater_url = url
    statement = '''
        CREATE TABLE 'Theaters' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'EnteredZipCode' TEXT NOT NULL,
            'Name' TEXT NOT NULL,
            'StreetAddress' TEXT,
            'City' TEXT,
            'State' TEXT,
            'ZipCode' TEXT,
            'MoviesPlaying' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

def insert_Theaters(List_Theater_Objects,zip):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for x in List_Theater_Objects:
        Name = x.theater_name
        EnteredZipCode = zip
        StreetAddress = x.street_address
        City = x.city
        State = x.state
        ZipCode= x.zip
        MoviesPlaying = None
        insert = (None, EnteredZipCode, Name, StreetAddress,City, State,ZipCode,MoviesPlaying)
        statement = 'INSERT INTO Theaters VALUES (?,?,?,?,?,?,?,?)'
        cur.execute(statement, insert)
        conn.commit()
    conn.close()

    #update_movies_playing(List_Theater_Objects)

def insert_Movies(List_Movie_Objects,theater_class_object):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    movies_in_sql = []
    for x in List_Movie_Objects:
        Name = x.movie_name
        if Name in movies_in_sql:
            continue
        else:
            movies_in_sql.append(Name)
        ReleaseYear = x.movie_year
        if ReleaseYear == "No Movie Year":
            ReleaseYear = None
        Minutes = x.movie_time
        if Minutes == "No Time":
            Minutes = None
        Rating = x.movie_rating
        if Rating == "No Rating":
            Rating = None
        Genre = x.movie_genre
        Directors = x.movie_directors
        NumberOfDirectors = x.movie_number_of_directors
        Stars = x.movie_stars
        NumberOfStars = x.movie_number_of_stars
        Budget = x.movie_budget
        if Budget == "No Budget":
            Budget = None
        GrossProfitUSA = x.movie_gross_usa
        if GrossProfitUSA == "No Gross":
             GrossProfitUSA = None
        OpeningWeekendUSA = x.movie_opening_weekend_usa
        if OpeningWeekendUSA == "No Opening Weekend Usa":
            OpeningWeekendUSA = None
        CumulativeWorldwideGross = x.movie_worldwide_gross
        if CumulativeWorldwideGross == "No Cumulative Worldwide Gross":
            CumulativeWorldwideGross = None
        insert = (None,Name,ReleaseYear,Minutes,Rating,Genre,Directors,NumberOfDirectors,Stars,NumberOfStars,Budget,GrossProfitUSA,OpeningWeekendUSA,CumulativeWorldwideGross)
        statement = 'INSERT INTO Movies '
        statement += 'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        cur.execute(statement, insert)
        conn.commit()
    conn.close()
    update_movies_playing(theater_class_object)

#get the list of movies from theaters
def update_movies_playing(theater_object):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    MoviesPlaying= ""
    M = []
    MoviesShowing =  theater_object.list_movies
    theater_name = theater_object.theater_name
    for x in MoviesShowing:
        statement = '''
            SELECT Movies.Id
            FROM Movies
            WHERE Movies.Name = "{}"
        '''.format(x)
        cur.execute(statement)
        for y in cur:
            id_ = str(y[0]) + ','
            MoviesPlaying = MoviesPlaying + id_
            #MoviesPlaying = MoviesPlaying + str(id_) + ","
        #MoviesPlaying.append(str(id_))
    M.append(MoviesPlaying[:-1])
    update = (M)
    statement = '''
        UPDATE Theaters
        SET MoviesPlaying=?
        WHERE Name = '{}'
    '''.format(theater_name)
    cur.execute(statement,update)
    conn.commit()
    conn.close()
#init_db(DBNAME)
# movies = list_movietheaters("48104")
# mov = movie_information(movies[0])

#plotly graphs:

#Type: Grouped Bar Chart
#Shows:movie budget compared to cumulative worldwide gross for movies playing at a selected theater
def budget_and_cumulativegross(theater_object):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    try:
        theater_streetaddress = theater_object.street_address
        theater_name = theater_object.theater_name
        title = 'Movie Budget Compared to Cumulative Worldwide Gross for Movies Playing at {}'.format(theater_name)
        budget = []
        worldwide_gross = []
        MoviesShowing = []
        statement = '''
            SELECT MoviesPlaying
            FROM Theaters
            WHERE Name = "{}" AND StreetAddress = "{}"
            LIMIT 1
        '''.format(theater_name,theater_streetaddress)
        cur.execute(statement)
        for x in cur:
            movie_ids=x[0]
        movie_ids=movie_ids.split(',')
        print(movie_ids)
        for x in movie_ids:
            statement = '''
                SELECT Budget,CumulativeWorldwideGross,Name
                FROM Movies
                WHERE Id = {}
            '''.format(x)
            cur.execute(statement)
            for y in cur:
                if y[0] == None and y[1]== None:
                    continue
                elif y[0] == None or y[1]== None:
                    continue
                else:
                    budget.append(y[0])
                    worldwide_gross.append(y[1])
                    MoviesShowing.append(y[2])
        trace1 = go.Bar(
            x = MoviesShowing,
            y = budget,
            name = 'Budget'
        )
        trace2 = go.Bar(
            x = MoviesShowing,
            y = worldwide_gross,
            name = 'Cumulative Worldwide Gross'
        )
        data = [trace1,trace2]
        layout = go.Layout(
            title = title,
            barmode = 'group',
            yaxis=dict(title='Dollars'),
            xaxis=dict(title='Movies Playing')
        )
        fig = go.Figure(data = data, layout= layout)
        py.plot(fig, filename = 'Movie Budget Compared to Cumulative Worldwide Gross for Movies Playing')
    except:
        print("Data not available to make this chart")



# movies = list_movietheaters("48104")
# mov = movie_information(movies[0])
# here =budget_and_cumulativegross(movies[0])

#Type: Bar Chart
#Shows: movie length in minutes for movies playing
def minutes_of_movies(theater_object):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    try:
        theater_streetaddress = theater_object.street_address
        theater_name = theater_object.theater_name
        title = 'Movie Length (in Minutes) for Movies Playing at {}'.format(theater_name)
        MoviesShowing = []
        minutes = []
        statement = '''
            SELECT MoviesPlaying
            FROM Theaters
            WHERE Name = "{}" AND StreetAddress = "{}"
            LIMIT 1
        '''.format(theater_name,theater_streetaddress)
        cur.execute(statement)
        for x in cur:
            movie_ids=x[0]
        movie_ids=movie_ids.split(',')
        for x in movie_ids:
            statement = '''
                SELECT Minutes,Name
                FROM Movies
                WHERE Id = {}
            '''.format(x)
            cur.execute(statement)
            for y in cur:
                if y[0] == None:
                    continue
                else:
                    minutes.append(y[0])
                    MoviesShowing.append(y[1])
        data = [go.Bar(x=MoviesShowing,y= minutes)]
        layout = go.Layout(
            title = title,
            yaxis=dict(title='Length of Movie (Minutes)'),
            xaxis = dict(title = "Movies Playing")
        )
        fig = go.Figure(data = data, layout= layout)
        py.plot(fig, filename='Movie Time (Minutes)')
    except:
        print("Data not avaliable to make this chart")
# movies = list_movietheaters("48104")
# mov = movie_information(movies[0])
# here =minutes_of_movies(movies[0])

#Type: Pie Chart
#Shows: a selected movies' percentage revenue that came from the U.S compared to the percentage that came from the rest of ther world.
def gross_usa_vs_cumulativegross(movie_object):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    try:
        movie = movie_object.movie_name
        title = "{}Movie: Revenue From U.S Compared to Revenue From the Rest of the World".format(movie)
        statement = '''
            SELECT GrossProfitUSA,CumulativeWorldwideGross
            FROM Movies
            WHERE Name = "{}"
        '''.format(movie)
        cur.execute(statement)
        for y in cur:
            if y[0] == None and y[1]== None:
                continue
            elif y[0] == None or y[1]== None:
                continue
            else:
                #percent_us = y[1].split(',')/int(y[0].split(',').join()) #U.S percentage
                world = y[1].split(',')
                usa = y[0].split(',')
                percent_us= int("".join(usa))/int("".join(world))
                percent_world = 1 - percent_us
        fig = {
            'data': [{'labels': ["% Revenue From the United States", "% Revenue From the Rest of the World"],
                      'values':  [percent_us, percent_world],
                      'type': 'pie'}],
            'layout': {'title': title}
             }
        py.plot(fig)
    except:
        print("Data not avaliable to make this chart")
# init_db(DBNAME)
# movies = list_movietheaters("48104")
# mov = movie_information(movies[0])
# here =gross_usa_vs_cumulativegross(mov[3])
#Type: Scatter Plot
#Shows: movie length (in minutes) compared to movie budget for movies playing
def time_budget(theater_object):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    try:
        theater_streetaddress = theater_object.street_address
        theater_name = theater_object.theater_name
        title = 'Length of Movie (minutes) Compared to Movie Budget for Movies Playing at {}'.format(theater_name)
        budget = []
        minutes = []
        MoviesShowing = []
        statement = '''
            SELECT MoviesPlaying
            FROM Theaters
            WHERE Name = "{}" AND StreetAddress = "{}"
            LIMIT 1
        '''.format(theater_name,theater_streetaddress)
        cur.execute(statement)
        for x in cur:
            movie_ids=x[0]
        movie_ids=movie_ids.split(',')
        for x in movie_ids:
            statement = '''
                SELECT Budget,Minutes,Name
                FROM Movies
                WHERE Id = {}
            '''.format(x)
            cur.execute(statement)
            for y in cur:
                if y[0] == None and y[1]== None:
                    continue
                elif y[0] == None or y[1]== None:
                    continue
                else:
                    budget.append(y[0])
                    minutes.append(y[1])
                    MoviesShowing.append(y[2])
        trace1 = go.Scatter(
            x = MoviesShowing,
            y = budget,
            name = 'Budget'
        )
        trace2 = go.Scatter(
            x = MoviesShowing,
            y = minutes,
            name = 'Time (minutes)',
            yaxis='y2'
        )
        data = [trace1,trace2]
        layout = go.Layout(
            title = title,
            yaxis=dict(
                title='Dollars'
            ),
            yaxis2=dict(
                title='Length of Movie (Minutes)',
                titlefont=dict(color='rgb(148, 103, 189)'),
                tickfont=dict(color='rgb(148, 103, 189)'),
                overlaying='y',
                side='right'
            ),
            xaxis=dict(title='Movies Playing')
        )
        fig = go.Figure(data = data, layout= layout)
        py.plot(fig, filename = 'Length of Movie Compared to Movie Budget')
    except:
        print("Data not avaliable to make this chart")
# init_db(DBNAME)
# movies = list_movietheaters("48104")
# mov = movie_information(movies[0])
# here =time_budget(movies[0])
#Type: Grouped Bar Chart
#Shows: Gross Profit Compared to Gross Profit During Opening Weekend in the USA for Movies Playing
def OpeningWeekendUSA_compared_GrossUSA(theater_object):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    try:
        theater_streetaddress = theater_object.street_address
        theater_name = theater_object.theater_name
        title = 'Gross Profit Compared to Gross Profit During Opening Weekend in the USA for Movies Playing at {}'.format(theater_name)
        openingweekend = []
        gross = []
        MoviesShowing = []
        statement = '''
            SELECT MoviesPlaying
            FROM Theaters
            WHERE Name = "{}" AND StreetAddress = "{}"
            LIMIT 1
        '''.format(theater_name,theater_streetaddress)
        cur.execute(statement)
        for x in cur:
            movie_ids=x[0]
        movie_ids=movie_ids.split(',')
        for x in movie_ids:
            statement = '''
                SELECT GrossProfitUSA,OpeningWeekendUSA,Name
                FROM Movies
                WHERE Id = {}
            '''.format(x)
            cur.execute(statement)
            for y in cur:
                if y[0] == None and y[1]== None:
                    continue
                elif y[0] == None or y[1]== None:
                    continue
                else:
                    gross.append(y[0])
                    openingweekend.append(y[1])
                    MoviesShowing.append(y[2])
        trace1 = go.Bar(
            x = MoviesShowing,
            y = openingweekend,
            name = 'Opening Weekend USA'
        )
        trace2 = go.Bar(
            x = MoviesShowing,
            y = gross,
            name = 'Gross Profit USA'
        )
        data = [trace1,trace2]
        layout = go.Layout(
            title = title,
            barmode = 'group',
            yaxis=dict(title='Dollars'),
            xaxis=dict(title='Movies Playing')
        )
        fig = go.Figure(data = data, layout= layout)
        py.plot(fig, filename = 'Gross Profit USA Compared to Opening Weekend USA')
    except:
        print("Data not avaliable to make this chart")
# init_db(DBNAME)
# movies = list_movietheaters("48104")
# mov = movie_information(movies[0])
# here =OpeningWeekendUSA_compared_GrossUSA(movies[0])

# r=list_movietheaters("60022")
# i=movie_information(r[0])
# gross_usa_vs_cumulativegross(i[2])


#zip #
# theater #

# movie info #

#interactive part
def interactive():
    print('Enter "help" at any point to see a list of valid commands')
    response = input('Please type in the zipcode command (or "exit" to quit): ')
    while response != 'exit':
        split_response = response.split()
        if split_response[0]== "zip" and len(split_response[1]) == 5:
            try:
                int(split_response[1])
                result = list_movietheaters(split_response[1])
                if len(result) == 0:
                    print("No theaters near the zip code entered.")
                    response = input('Please type in a valid command (or "help" for more options): ')
                    if response == "exit":
                        print("Goodbye!")
                    continue
                print("List of Theaters near {}: ".format(split_response[1]))
                num = 0
                dic_theaters = {}
                length = len(result)
                for t in result:
                    num += 1
                    string = t.__str__()
                    dic_theaters[num] = t
                    if length > 10:
                        if num == 11:
                            more_theaters = input("Would you like to see more theater options (type: 'yes' or 'no')?: ")
                            if more_theaters.lower() == 'yes':
                                print("{}. {}".format(num,string))
                                continue
                            else:
                                break
                    print("{}. {}".format(num,string))
            except:
                response = input('Please type in a valid command (or "help" for more options): ')
                if response == "exit":
                    print("Goodbye!")
                continue
        elif split_response[0] == "theater":
            try:
                if int(split_response[1]) not in dic_theaters.keys():
                    response = input('Please type in a valid command (or "help" for more options): ')
                    if response == "exit":
                        print("Goodbye!")
                    continue
                else:
                    for x in dic_theaters:
                        if int(split_response[1]) == x:
                            obj = dic_theaters[x]
                    results = movie_information(obj)
                    if len(results) == 0:
                        print("No movies showing for the theater you selected.")
                        response = input('Please type in a valid command (or "help" for more options): ')
                        if response == "exit":
                            print("Goodbye!")
                        continue
                    dic_movies_playing = {}
                    num = 0
                    print("List of Movies Playing at {}: ".format(obj.theater_name))
                    for x in results:
                        num += 1
                        string = x.movie_name
                        dic_movies_playing[num]= x
                        print("{}. {}".format(num, string))
                graph = input('Would you like to see a graph of movie budget compared to cumulative worldwide gross ("yes or "no")?: ')
                graph2 = input('Would you like to see a graph of movie time ("yes or "no")?: ')
                graph3 = input('Would you like to see a graph of movie budget compared to movie length ("yes or "no")?:')
                graph5 = input('Would you like to see a graph of Gross Profit USA compared Opening Weekend USA ("yes or "no")?:')

                if graph.lower() == "yes":
                    budget_and_cumulativegross(obj)
                if graph2.lower() == "yes":
                    minutes_of_movies(obj)
                if graph3.lower() == "yes":
                    time_budget(obj)
                if graph5.lower() == "yes":
                    OpeningWeekendUSA_compared_GrossUSA(obj)
            except:
                response = input('Please type in a valid command (or "help" for more options): ')
                if response == "exit":
                    print("Goodbye!")
                continue
                #graph = input('Would you like to see a graph of movie budget compared to cumulative worldwide gross("yes or "no" )?: ')
        elif split_response[0] == "movie" and split_response[1] == "info":
            try:
                if int(split_response[2]) not in dic_movies_playing.keys():
                    response = input('Please type in a valid command (or "help" for more options): ')
                    if response == "exit":
                        print("Goodbye!")
                    continue
                for x in dic_movies_playing:
                    if x == int(split_response[2]):
                        movie_obj = dic_movies_playing[x]
                        print(movie_obj)
                graph4 = input('Would you like to see a graph that compares revenue from the U.S versus the rest of the world ("yes" or "no")?: ')
                if graph4.lower() == "yes":
                    gross_usa_vs_cumulativegross(movie_obj)
            except:
                response = input('Please type in a valid command (or "help" for more options): ')
                if response == "exit":
                    print("Goodbye!")
                continue
        elif "help" == response:
            print("\tzip <zipcode>")
            print("\t\t available anytime")
            print("\t\tlists all theaters between 5 and 30 miles away from the zipcode entered")
            print("\t\tvalid inputs: a 5 digit zip code")
            print("\ttheater <result_number>")
            print("\t\tavailable only if there is an active result set (a list of theaters near a zipcode specified)")
            print("\t\tlists all movies showing at the theater selected")
            print("\t\tvalid inputs: an integer 1-len (result_set_size)")
            print("\tmovie info <result_number>")
            print("\t\tavailable only if there is an active result set (a list of movies showing at a specified theater)")
            print("\t\tshows further information about the movie selected")
            print("\t\tvalid inputs: an integer 1-len (result_set_size)")
            print("\texit")
            print("\t\texits the program")
            print("\thelp")
            print("\t\tlists available commands (these instructions)")
        else:
            response = input('Please type in a valid command (or "help" for more options): ')
            if response == "exit":
                print("Goodbye!")
            continue
        response = input('Please type in a command (or "exit" to quit): ')
        if response == "exit":
            print("Goodbye!")
        continue


        # try:
        #     if response != "help":
        #         response = int(response)
        # except:
        #     response = input('Please type in a valid command (or "help" for more options): ')
        #     if response == "exit":
        #         print("Goodbye!")
        #     continue
        # if len(str(response)) == 5:
        #     result = list_movietheaters(response)
        #     print("List of Theaters near {}: ".format(response))
        #     num = 0
        #     dic_theaters = {}
        #     length = len(result)
        #     for t in result:
        #         num += 1
        #         string = t.__str__()
        #         dic_theaters[num] = t
        #         if length > 10:
        #             if num == 11:
        #                 more_theaters = input("Would you like to see more theater options (type: 'yes' or 'no')?: ")
        #                 if more_theaters.lower() == 'yes':
        #                     print("{}. {}".format(num,string))
        #                     continue
        #                 else:
        #                     break
        #         print("{}. {}".format(num,string))
        # elif len(str(response)) < 5:
        #     if response not in dic_theaters.keys():
        #         response = input('Please type in a valid command (or "help" for more options): ')
        #         if response == "exit":
        #             print("Goodbye!")
        #         continue
        #     else:
        #         for x in dic_theaters:
        #             if response == x:
        #                 obj = dic_theaters[x]
        #         results = movie_information(obj)
        #         dic_movies_playing = {}
        #         num = 0
        #         print("List of Movies Playing at {}: ".format(obj.theater_name))
        #         for x in results:
        #             num += 1
        #             string = x.movie_name
        #             dic_movies_playing[num]= x
        #             print("{}. {}".format(num, string))
        #     if int(response) not in dic_movies_playing.keys():
        #         response = input('Please type in a valid command (or "help" for more options): ')
        #         if response == "exit":
        #             print("Goodbye!")
        #         continue
        #     for x in dic_movies_playing:
        #         if x == int(response):
        #             movie_obj = dic_movies_playing[x]
        #             print(movie_obj)








            # response = input('Type in a number to see more information about a movie (or help for more options): ')
            # try:
            #     int(response)
            # except:
            #     if response == "exit":
            #         print("Goodbye!")
            #         continue
            #     else:
            #         response = input('Please type in a valid command (or "help" for more options): ')
            #         if response == "exit":
            #             print("Goodbye!")
            #         continue
                #response = input('Please type in a zipcode (or exit to escape): ')

#commands:
#zip <type zip code>
#theater <type number>
#movie <type number>


# if response == "exit":
#     print("Goodbye!")
#     continue
# elif response == "help":
#     continue
# elif len(str(response)) == 5:
#     continue
# elif type(response) == type(""):
#     try:
#         response = int(response)
#     except:
#         response input('Please enter a valid command (or "help" for more options): ')
#         continue


        # try:
        #     response = int(response)
        # except:
        #     response = input('Please enter a valid zipcode (or exit to escape): ')
        #     if response == "exit":
        #         print("Goodbye!")
        #     continue
        # if response == 'help':
            # response = input('Enter a command: ')
            # continue
            # pass
        # if


#table 1: theaters
#table 2: movies
#theaters column movies contain a string ('1,2,3,4,5,6,7,')
#theaters playing this list of movies
#str.split(',') get movie info for all those
#movies tables do need any information on what movies are playing
#movies can delete everytime it runs keep the theater cache
#print theaters near zipcode
#then they pick a theater number and tells the movies
#they can pick a movie number and it tells the movies
#pie chart showing the ratings for the movie
#release month (how long specific movies are in theaters) --> time line graph (or you can do gross sales ---> distribution of gross sales per movie per theater)
#-------------------------------------------------------

#table 1:movies
#join on movie titles or movie directors
#table 2: theaters and zip codes column for list of movies
#theaters table: id, zip code, address, movies list
#just keep adding them to the database
#can just use the cache data


#tables all the movie information
#join on the movies playing at that theater

#movie theaters id
#table 1: theaters, autoincriment unique id
#cant multiple theaters show the same movie
#movies: column with theater id
#movie id as a foreign key in the theater table
#beautiful soup documentation


#interactive part
if __name__ == '__main__':
    # movies = list_movietheaters("48104")
    # mov = movie_information(movies[0])
    init_db(DBNAME)
    interactive()
    #result=list_movietheaters("60022")
    #b = budget_and_cumulativegross(result[0])
    #print(b)

    # user = input("Enter a zipcode in the United States: ")
    # while user != "exit":
