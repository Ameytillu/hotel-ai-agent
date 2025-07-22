import pandas as pd

policy_df = pd.read_csv("data/hotel_policies.csv")

def get_policy_answer(keyword):
    for _, row in policy_df.iterrows():
        if keyword.lower() in row['question'].lower():
            return row['answer']
    return "Sorry, I couldn’t find any policy related to that."