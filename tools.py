import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.tools import tool
import sqlite3

data = np.load("./netflix_data.npz", allow_pickle=True)

DB_NAME = "cart.db"

P = data["P"]
Q = data["Q"]
bu = data["bu"]
bm = data["bm"]
mu = data["mu"]
movie_titles = data["movie_titles"]
movie_years = data["movie_years"]

n = 10

def search_movie(query, movie_titles=movie_titles, movie_years=movie_years):
    query = query.lower()
    for index, movie in enumerate(movie_titles):
        if query in movie.lower():
            year = movie_years[index]
            return (index, movie, year)
    return (-1, "No Movie Found", "No Year Found")

def find_similar_movies(movie_index, Q, top_n=n):
    target_vector = Q[movie_index]
    cosine_sim = cosine_similarity([target_vector], Q).flatten()
    sorted_array = np.argsort(cosine_sim)[::-1]
    top_indices = sorted_array[1:top_n + 1]
    result_list = []
    for index in top_indices:
        result_list.append(movie_titles[index])
    return "\n".join(result_list)

def top_movies(bm, movie_titles, movie_years, n=n):
    sorted_index = np.argsort(bm)
    last_n = sorted_index[-n:][::-1]
    lines = []
    for i in last_n:
        lines.append(f"\nMovie Name: {movie_titles[i]} ({movie_years[i]})")

    return "\n".join(lines)

def get_db_connection():
    return sqlite3.connect(DB_NAME, timeout=30.0, check_same_thread=False)

def init_db():
    with get_db_connection() as connection_obj:
        cursor_obj = connection_obj.cursor()
        table_creation_query = """
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            movie_index INTEGER NOT NULL,
            movie_name TEXT NOT NULL,
            movie_year INTEGER NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, movie_index)
        );
        """
        cursor_obj.execute(table_creation_query)
        connection_obj.commit()
    print("Table is ready")

def add_to_cart(session_id: str, movie_index: int, movie_name: str, movie_year: int):
    with get_db_connection() as connection_obj:
        cursor_obj = connection_obj.cursor()
        query = """
        INSERT OR IGNORE INTO cart (
            session_id,
            movie_index,
            movie_name,
            movie_year
        ) VALUES (?, ?, ?, ?);
        """
        data = (session_id, movie_index, movie_name, movie_year)
        cursor_obj.execute(query, data)
        
        if cursor_obj.rowcount == 0:
            msg = f"{movie_name} is already in your cart!"
        else:
            msg = f"{movie_name} added successfully"
        connection_obj.commit()
        return msg

def get_cart(session_id: str):
    with get_db_connection() as connection_obj:
        cursor_obj = connection_obj.cursor()
        query = """
        SELECT * FROM cart WHERE session_id = ?;
        """
        cursor_obj.execute(query, (session_id,))
        rows = cursor_obj.fetchall()
        # print(f"{session_id} session id returened")
        return rows

def clear_cart(session_id: str):
    with get_db_connection() as connection_obj:
        cursor_obj = connection_obj.cursor()
        query = """
        DELETE FROM cart WHERE session_id = ?;
        """
        cursor_obj.execute(query, (session_id,))
        connection_obj.commit()
        # return f"Checked out successfully!"

@tool
def get_popular_movies() -> str:
    """Get a list of popular highly-rated movies. 
    Call this when the user asks for movie recommendations 
    without mentioning a specific movie they like."""
    
    n = 10
    ans = top_movies(bm=bm, movie_titles=movie_titles, movie_years=movie_years, n=n)

    return f"Here are the top {n} movies" + ans

@tool
def add_movie_to_cart(movie_name: str, session_id: str) -> str:
    """Add a movie to the user's shopping cart.
    
    Args:
        movie_name: The name of the movie to add.
        session_id: The user's session ID.
    """
    result = search_movie(query=movie_name)
    if result[0] == -1:
        return f"Sorry, I couldn't find a movie matching '{movie_name}'."
    ans = add_to_cart(session_id=session_id, movie_index=result[0], movie_name=result[1], movie_year=result[2])
    return ans

@tool
def get_similar_movies(movie_name: str) -> str:
    """Find movies similar to a given movie.
    Call this when the user says they like a specific movie 
    and want similar recommendations.
    
    Args:
        movie_name: The name of the movie to find similar movies for.
    """
    result = search_movie(query=movie_name)
    if result[0] == -1:
        return f"Sorry, I couldn't find a movie matching '{movie_name}'."
    ans = find_similar_movies(movie_index=result[0], Q=Q, top_n=n)
    return f"Find this interesting movies related to {movie_name}: " + ans

@tool
def view_cart(session_id: str) -> str:
    """View all movies in the user's cart.
    
    Args:
        session_id: The user's session ID.
    """
    result = get_cart(session_id=session_id)
    if len(result) == 0:
        return f"The cart for the {session_id} is empty."
    lines = [f"Your cart (session: {session_id}) contains:"]
    for item in result:
        lines.append(f"- {item[3]} ({item[4]})")
    return "\n".join(lines)

@tool
def checkout(session_id: str) -> str:
    """Checkout and purchase all movies in the cart.
    
    Args:
        session_id: The user's session ID.
    """
    result = get_cart(session_id=session_id)
    if len(result) == 0:
        return f"The cart for the {session_id} is empty."
    clear_cart(session_id=session_id)
    return f"User ID: {session_id} has checked out successfully."

