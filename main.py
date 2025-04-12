import pickle
import numpy as np
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
cosine_sim = None
userhistory_df = None
destinations_df = None

origins = [
  "http://localhost:5173"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

with open("cosine_sim.pkl", "rb") as f:
  cosine_sim = pickle.load(f)

users_df = pd.read_pickle("users_df.pkl")
userhistory_df = pd.read_pickle("userhistory_df.pkl")
destinations_df = pd.read_pickle("destinations_df.pkl")
destinations_with_pictures_df = pd.read_pickle("destinations_with_pictures_df.pkl")


def get_all_users(users_df):
  all_users = []
  for i in range(len(users_df)):
    all_users.append(users_df.iloc[i][[
      'UserID', 'Name', 'Email', 'Preferences', 'Gender'
    ]].to_dict())
  return all_users


def get_all_destinations(destinations_with_pictures_df):
  all_destinations = []
  for i in range(len(destinations_with_pictures_df)):
    all_destinations.append(destinations_with_pictures_df.iloc[i][[
      'DestinationID', 'Name', 'State', 'Type', 'Popularity', 'BestTimeToVisit', 'ImageURL'
    ]].to_dict())
  return all_destinations


def get_visited_places(user_id, userhistory_df, destinations_df):
  # Get the destinations the user has visited
  visited_destination_ids = userhistory_df[userhistory_df['UserID'] == user_id]['DestinationID'].values
  
  visited_destinations = []
  for _id in visited_destination_ids:
    # Append detailed information for each recommendation
    visited_destinations.append(destinations_df.iloc[_id][[
      'DestinationID', 'Name', 'State', 'Type', 'Popularity', 'BestTimeToVisit', 'ImageURL'
    ]].to_dict())
  
  return visited_destinations


def recommend_destinations(user_id, userhistory_df, destinations_df, cosine_sim):
  """
  Recommends top 5 destinations for a given user based on similarity scores.
  Args:
  - user_id: ID of the user.
  - userhistory_df: User history DataFrame containing 'UserID' and 'DestinationID'.
  - destinations_df: Destinations DataFrame containing destination details.
  - cosine_sim: Cosine similarity matrix for destinations.
  Returns:
  - DataFrame with recommended destinations and their details.
  """

  # Get the destinations the user has visited
  visited_destinations = userhistory_df[userhistory_df['UserID'] == user_id]['DestinationID'].values
  print(f'visited destinations: {visited_destinations}')
  print(f'visited destinations: {visited_destinations - 1}')
  
  # Calculate similarity scores for visited destinations
  similar_scores = np.sum(cosine_sim[visited_destinations - 1], axis=0)
  print(f'similar scores: {similar_scores}')
  
  # Recommend the top destinations the user hasn't visited yet
  recommended_destinations_ids = np.argsort(similar_scores)[::-1]
  print(f'top destinations the user has not visited: {recommended_destinations_ids}')
  
  recommendations = []
  for _id in recommended_destinations_ids:
    if destinations_df.iloc[_id]['DestinationID'] not in visited_destinations:
      # Append detailed information for each recommendation
      recommendations.append(destinations_df.iloc[_id][[
        'DestinationID', 'Name', 'State', 'Type', 'Popularity', 'BestTimeToVisit', 'ImageURL'
      ]].to_dict())

    if len(recommendations) >= 5:
      break
  
  # # Convert recommendations to a DataFrame
  # return pd.DataFrame(recommendations)
  return recommendations


@app.get("/")
async def root():
  return {"message": "Travel Recommendation API is running!"}


@app.get("/get_all_users")
def get_all_users_api():
  result = get_all_users(users_df)
  return {"users": result}


@app.get("/get_all_destinations")
def get_all_destinations_api():
  result = get_all_destinations(destinations_with_pictures_df)
  return {"destinations": result}


@app.get("/get_visited_places/{user_id}")
def get_visited_places_api(user_id: int):
  result = get_visited_places(user_id, userhistory_df, destinations_with_pictures_df)
  return {"user_id": user_id, "visited_places": result}


@app.get("/recommendations/{user_id}")
def recommend(user_id: int):
  result = recommend_destinations(user_id, userhistory_df, destinations_with_pictures_df, cosine_sim)
  return {"user_id": user_id, "recommendations": result}
