# Netflix Bellkor with LLM

This is a simple implementation of the Bellkor algorithm. The twist is that we are using an LLM to generate the answers for user questions like "Which movie should I watch?" or "Recommend related movies to 'The Godfather'" etc. The LLM will generate the answers based on the data that we have.

<div align="center">
    <img src="https://github.com/ripslinger17/Netflix-Bellkor-With-LLM/blob/main/assets/demo.gif" width="600" alt="App Demo">
</div>

Why this project is unique? Because we only have UserID, MovieID, Ratings, and Timestamps. We do not have any other information about the movies or the users. It was a sparse matrix representation of which we only had around ~1M ratings available but the total possible combinations were ~8B combinations. I have used the original Bellkor algorithm for finding the similar movies to recommend to the user.

I have followed this [paper](https://www2.seas.gwu.edu/~simhaweb/champalg/cf/papers/KorenBellKor2009.pdf) and this [paper](https://www2.seas.gwu.edu/~simhaweb/champalg/cf/papers/BellkorNetflix2008.pdf) for the implementation. I only limited myself to the baseline model with matrix factorization. The formula I used is:

$$\boxed{\hat{r_{um}} = \mu + b_{u} + b_{m} + P_{u}^{T} \cdot Q_{m}}$$

with error as:

$$\boxed{e = r - \hat{r}}$$

Here $\mu$ is the global average rating, $b_u$ is the user bias, $b_m$ is the movie bias, $P_u$ is the user latent factor vector, and $Q_m$ is the movie latent factor vector.

Here $e$ is the error between the actual rating $r$ and the predicted rating $\hat{r}$.

Trained on the original Netflix dataset which is available [here](https://www.kaggle.com/datasets/netflix-inc/netflix-prize-data). I converted the data into a numpy compressed data archive (`.npz`). You can create your own `.npz` file. I used kaggle for the data processing and training part.
## Model Performance
**Netflix's Cinematch RMSE was *0.95***

| Metric | Score (at 10 epochs) | Score (at 20 epochs) |
|--------|-------|-------|
| Training RMSE | 0.92 | 0.87 |
| Probe RMSE | 1.002 | 0.94 |

I beat the original Cinematch RMSE. 🤪

## Features

* **Conversational Interface:** Built with Streamlit, allowing users to chat naturally to get movie recommendations.
* **Smart Recommendations:** Uses Cosine Similarity on the latent movie factors ($Q$ matrix) to find genuinely similar movies, rather than relying on standard metadata tags.
* **LLM Tool Calling:** Uses LangChain and Ollama (`ministral-3:8b`) as an intelligent agent. The LLM determines user intent and calls specific Python functions (Tools) to fetch data.
* **Movie Cart System:** Users can add movies to a virtual "cart" and check out. Session data is stored locally using SQLite.
> *Note: You might wonder why I have a cart system instead of wishlist? In 2007 at the time Netflix used to primarily sent physical DVDs to homes by post. So the cart system is a nod to that era, where users would "rent" movies by adding them to their cart and checking out. It's a fun throwback to how Netflix operated before streaming became dominant.*
* **Top Movies Baseline:** Utilizes the learned movie biases ($b_m$) to recommend generally popular, highly-rated movies when the user has a "cold start."
* **Misc:** Choosen *20 latent factors*. Trained for *20 epochs* with *gamma of 0.0005* and *lambda of 0.01*.

## Tech Stack

* **Frontend:** Streamlit
* **Backend:** FastAPI
* **AI/LLM:** Ollama (`ministral-3:8b`), LangChain
* **Data Processing:** NumPy, Scikit-learn (for Cosine Similarity)
* **Database:** SQLite3

<div align="center">
    <img src="https://github.com/ripslinger17/Netflix-Bellkor-With-LLM/blob/main/assets/architecture.svg" width="600" alt="Architecture Diagram">
</div>

## Prerequisites

Before running the project, make sure your environment is set up:

1. **Clone the repository:**
```bash
   git clone https://github.com/ripslinger17/Netflix-Bellkor-With-LLM
   cd Netflix-Bellkor-With-LLM
```

2. **Install Python dependencies:**
Make sure you have Python 3.9+ installed, then run:
```bash
pip install -r requirements.txt

```


3. **Install Ollama Python Library:**
```bash
pip install ollama

```


4. **Download an Agent-Capable LLM:**
You need a local model capable of handling tool calling and agentic use cases. I have used `mistral-3:8b` for this project. Once you have the main Ollama application installed on your system, pull the model:
```bash
ollama pull mistral-3:8b

```


*(Note: Ensure your `netflix_data.npz` file is placed in the root directory before moving on to the next steps!)*

## How to Run

You will need three separate terminal windows to get all the components communicating with each other.

**Terminal 1: Start the Ollama Server**

```bash
ollama serve

```

**Terminal 2: Start the FastAPI Backend**

```bash
uvicorn main:app --reload

```

*The API will start at `http://localhost:8000`.*

**Terminal 3: Start the Streamlit Frontend**

```bash
streamlit run app.py

```

*Streamlit will automatically open your web browser to `http://localhost:8501`.*

### Testing with Postman

If you prefer to test the backend API independently of the Streamlit UI, you can use Postman to verify the endpoints and AI outputs. Postman documentation and the collection are included in this repository to help you get started easily.

## Example Chat Prompts

Once the app is running, try asking the assistant things like:

* *"Recommend me some movies."* (Triggers popular movies via $b_m$)
* *"I liked The Godfather. Recommend similar movies."* (Triggers vector similarity via $Q$ matrix)
* *"Add The Matrix to my cart."* (Interacts with SQLite DB)
* *"What's in my cart?"*
* *"Checkout."*

## How It Works Under the Hood

1. **User Prompt:** The user types a message in Streamlit.
2. **FastAPI & Agent:** The request is sent to the FastAPI backend, which routes it to the LangChain agent.
3. **Tool Selection:** The `ministral-3:8b` LLM analyzes the prompt and decides which tool to use (e.g., `get_similar_movies`, `add_movie_to_cart`).
4. **Data Retrieval:** - If recommending similar movies, the tool extracts the target movie's vector from the $Q$ matrix and computes cosine similarity against all other movie vectors to find the top $n$ matches.
* If managing the cart, it queries the SQLite `cart.db`.


5. **Response Generation:** The tool results are fed back into the LLM, which formats a human-friendly response and sends it back to the Streamlit UI.

Happy coding.