# route-scout
A tool for helping climbers find their perfect route.
Check it out [here!](https://route-scout.herokuapp.com)

#### -- Project Status: [Active]

## Intro/Objective
As an avid climber, this project was born from passion. Whenever I'd make outdoors trips, I'd want to maximize my time by pre-identifying a few bouldering routes I'd like to commit to for the day. This often came with scouring guide books and Mountain Project, an online listing of thousands of climbing routes across the globe, to find routes that interested me and were nearby one another. I wanted there to be an easy to use and centralized source that I could use to search for recommendations. So began the creation of Route Scout.

### Methods Used
* Natural Language Processing
* Recommendation
* Predictive Modeling
* Database Development
* Web Scraping
* Data visualization
* Interactive Application Development
* Application Deployment

### Technologies
* Python, jupyter
* Pandas, Numpy
* SKLearn
* Nltk, Stemming
* Postgres, SQL
* Dash, Flask
* Plotly
* Heroku

## Project Description
* Data  
   * Data was all pulled from Mountain Project using their api and some additional web scraping
   * Postgres and psycopg2, a python sql plugin, were used to facilitate the development of the database
   * In total, 4035 bouldering routes were pulled, covering the entirety of Southern California
* Overview of functionality
   * A user filters routes based on location and difficulty
   * A user enters a description of a climbing route in plain english
   * A backend model then ranks the filtered routes on their similarity to the description
   * Location and descriptive information is neatly output to help user facilitate planning their climbs
* Backend Model
   * All descriptions are standardized - lower case, punctuation and stop words removed, stemming applied
   * Descriptions are then vectorized by Term Frequency-Inverse Document Frequency to give greater merit to obscure words 
   * Descriptions are then ranked by cosine similarity with the input description to identify the closest matches

## Running the app locally

1. Clone this repo.
2. Make sure Docker daemon is running on your machine. 
3. ```Test```
4. run "python app.py" in your terminal

## For more detail and discussion:
* [Blog Post](https://pjourgensen.github.io/routescout.html)

