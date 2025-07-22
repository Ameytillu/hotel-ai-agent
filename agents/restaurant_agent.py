import pandas as pd

restaurant_df = pd.read_csv("data/restaurant.csv")

def get_restaurant_info():
    return restaurant_df.to_dict(orient='records')