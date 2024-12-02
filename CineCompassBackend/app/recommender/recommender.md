# Movie Recommender System

## Data Collection
- Gets popular movies from TMDB
- For each movie store:
  - Basic info and extra details
- All this data goes into a pandas DataFrame

## Text Processing
- Take all movie info and combines it into one big text string per movie
- Uses TF-IDF to turn text strings into numbers
- This creates a unique "fingerprint" for each movie

## Rating System
- Takes in user ratings as pairs of movie IDs and ratings (1-5 points)
- Uses these ratings to figure out what kinds of movies you like, by creating a profile
- Higher ratings get weighted more heavily in the comparison

## Making Recommendations
- Creates preference profile based on rated movies
- Compares profile to all other movies
- Finds similar movies you not rated yet
- Returns top 10 matches with:
  - Movie title
  - How similar it is to the taste
  - Genres
  - Cast
  - Director