import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample Book Dataset
data = {
    'title': ['Dune', 'Neuromancer', 'The Hobbit', 'Foundation', 'Harry Potter'],
    'features': [
        'Sci-Fi Frank Herbert space politics desert empire',
        'Sci-Fi William Gibson cyberpunk AI hackers future',
        'Fantasy J.R.R. Tolkien magic adventure ring middle-earth',
        'Sci-Fi Isaac Asimov galactic empire mathematics psychology',
        'Fantasy J.K. Rowling magic wizard school adventure'
    ]
}

df = pd.DataFrame(data)

# 1. Convert text into TF-IDF numerical vectors
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['features'])

# 2. Compute similarity matrix
similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

def recommend_books(book_title, top_n=2):
    idx = df[df['title'].str.lower() == book_title.lower()].index[0]
    scores = list(enumerate(similarity[idx]))
    # Sort books based on similarity score (excluding the book itself)
    sorted_books = sorted(scores, key=lambda x: x[1], reverse=True)[1:top_n+1]
    
    return [df.iloc[i[0]]['title'] for i in sorted_books]

# Example run:
print("Books similar to Dune:", recommend_books("Dune"))
# Output: ['Foundation', 'Neuromancer']