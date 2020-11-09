
import numpy as np
import pandas as pd

def drop_participants_with_missing_data(df, pdct):

    # Do not change in-place. Return changed df
    df = df.copy()

    expected_n_trials = pdct['expected_n_trials']

    # Identify subjs missing pre or post
    temp_grp = df.groupby(['subject_id'])
    tt_df = temp_grp['task_order'].nunique()
    tt_df = tt_df[tt_df < 2]
    bad_subject_list = list(set(tt_df.reset_index()['subject_id'].to_list()))
    
    # Identify subjs without all trials
    temp_grp = df.groupby(['subject_id', 'task_order'])
    tt_df = temp_grp.aggregate({'hit': np.sum, 'incorrect': np.sum, 'miss': np.sum})
    tt_df['total'] = tt_df['hit'] + tt_df['incorrect'] + tt_df['miss']
    tt_df = tt_df.reset_index()
    bad_subject_df = tt_df[(tt_df['total'] < expected_n_trials) | \
                           (tt_df['subject_id'].isin(bad_subject_list))]
    
    # Drop missing data subjects
    bad_subject_list = list(set(bad_subject_df.reset_index()['subject_id'].to_list()))
    df = df[~df['subject_id'].isin(bad_subject_list)]
    
    return df.reset_index(drop=True).copy() # Copy again because reset index