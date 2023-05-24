import flask
from flask import Flask
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pyttsx3
import datetime
import speech_recognition as sr
import random
import webbrowser

df2 = pd.read_csv('model/tmdb.csv')

tfidf = TfidfVectorizer(stop_words='english', analyzer='word')

# TF-IDF matrix by fitting and transforming the data
tfidf_matrix = tfidf.fit_transform(df2['soup'])
# print(tfidf_matrix.shape)

# cosine similarity matrix
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
# print(cosine_sim.shape)

df2 = df2.reset_index()
indices = pd.Series(df2.index, index=df2['title']).drop_duplicates()

# create array with all movie titles
all_titles = [df2['title'][i] for i in range(len(df2['title']))]


def get_recommendations(title):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    # print similarity scores
    # print("\n movieId      score")
    # for i in sim_scores:
    #     print(i)
    movie_indices = [i[0] for i in sim_scores]

    return_df = pd.DataFrame(columns=['Title', 'Homepage'])
    return_df['Title'] = df2['title'].iloc[movie_indices]
    return_df['Homepage'] = df2['homepage'].iloc[movie_indices]
    return_df['ReleaseDate'] = df2['release_date'].iloc[movie_indices]
    return return_df


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
print(voices[0].id)
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        # print(e)
        print("Say that again Please....")
        return "None"
    return query


def wishme():
    d = 'Sir I am always here to help you', f'tell me how can I help you Sir', f'What can I do for you sir'
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning sir!")
    elif 12 <= hour < 18:
        speak("Good Afternoon sir!")
    else:
        speak("Good Evening sir!")
    speak("Sir I am Jarvis.")
    speak(random.choice(d))


while True:
    wishme()
    query = takecommand()

    if query is not None:
        break

app = Flask(__name__, template_folder='templates')


@app.route("/")
def hello():
    result_final = get_recommendations(query)
    names = []
    homepage = []
    releaseDate = []
    for i in range(len(result_final)):
        names.append(result_final.iloc[i][0])
        releaseDate.append(result_final.iloc[i][2])
        if len(str(result_final.iloc[i][1])) > 3:
            homepage.append(result_final.iloc[i][1])
        else:
            homepage.append("#")

    return flask.render_template('home.html', movie_names=names, movie_homepage=homepage,
                                 search_name=query,
                                 movie_releaseDate=releaseDate)


webbrowser.open('http://127.0.0.1:5000')

app.run()
