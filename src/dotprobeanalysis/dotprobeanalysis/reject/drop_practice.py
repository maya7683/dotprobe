import pandas as pd

def drop_practice_trials(data_df):
    return data_df[data_df['block_type'] == 'Main'].reset_index(drop=True).copy()