import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

data = np.load("./netflix_data.npz", allow_pickle=True)

P = data["P"]
Q = data["Q"]
bu = data["bu"]
bm = data["bm"]
mu = data["mu"]
movie_titles = data["movie_titles"]
movie_years = data["movie_years"]

sorted_index = np.argsort(bm)
last_ten = sorted_index[-10:]
top_ten_movies = bm[last_ten]


def search_movie(query, movie_titles, movie_years):
    query = query.lower()
    for index, movie in enumerate(movie_titles):
        movie = movie.lower()
        if query in movie:
            year = movie_years[index]
            return (index, movie, year)
    return (-1, "No Movie Found")

def find_similar_movies(movie_index, Q, movie_titles, movie_years, top_n=10):
    target_vector = Q[movie_index]
    cosine_sim = cosine_similarity([target_vector], Q).flatten()
    sorted_array = np.argsort(cosine_sim)
    top_indices = sorted_array[-(top_n + 1):-1]
    top_indices = top_indices[::-1]
    return sorted_array[-top_n:-1]
