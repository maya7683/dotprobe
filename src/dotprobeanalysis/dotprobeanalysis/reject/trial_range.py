import numpy as np
import pandas as pd

def drop_trials_outside_range(df, pre_range, pst_range):
    # 
    if pre_range:
        pre_rng = list(pre_range)
        if pre_rng[0] is None:
            pre_rng[0] = 1
        if pre_rng[1] is None:
            pre_rng[1] = df[df['task_order']==ORDR_LIST[PRE_IDX]]['trial_n'].max()
    else:
        pre_rng = [1, df[df['task_order']==ORDR_LIST[PRE_IDX]]['trial_n'].max()]
    if pst_range:
        pst_rng = list(pst_range)
        if pst_rng[0] is None:
            pst_rng[0] = 1
        if pst_rng[1] is None:
            pst_rng[1] = df[df['task_order']==ORDR_LIST[PST_IDX]]['trial_n'].max()
    else:
        pst_rng = [1, df[df['task_order']==ORDR_LIST[PST_IDX]]['trial_n'].max()]
    # Do not change in-place. Return changed df
    df = df.copy()
    df = df[~((df['task_order']==ORDR_LIST[PRE_IDX]) & (df['trial_n'] < pre_rng[0]))]
    df = df[~((df['task_order']==ORDR_LIST[PRE_IDX]) & (df['trial_n'] > pre_rng[1]))]
    df = df[~((df['task_order']==ORDR_LIST[PST_IDX]) & (df['trial_n'] < pst_rng[0]))]
    df = df[~((df['task_order']==ORDR_LIST[PST_IDX]) & (df['trial_n'] > pst_rng[1]))]
    df['n_trials_order'] = 0
    df.loc[df['task_order']==ORDR_LIST[PRE_IDX],'n_trials_order'] = 1 + pre_rng[1] - pre_rng[0]
    df.loc[df['task_order']==ORDR_LIST[PST_IDX],'n_trials_order'] = 1 + pst_rng[1] - pst_rng[0]
    return df