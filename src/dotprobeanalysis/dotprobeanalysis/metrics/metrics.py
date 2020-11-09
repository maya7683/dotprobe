
import pandas as pd
import numpy as np

def _get_rt_distdiff(df):
    from scipy.stats import percentileofscore
    e_rts = df[df['condition']==EMOT_LIST[EMOT_IDX]]['rt'].values
    n_rts = df[df['condition']==EMOT_LIST[NEUT_IDX]]['rt'].values
    if (not e_rts.size) or (not n_rts.size):
        return np.nan
    e_idxs, n_idxs = np.meshgrid(np.arange(e_rts.size), np.arange(n_rts.size))
    e_idxs = e_idxs.flatten()
    n_idxs = n_idxs.flatten()
    en_diffs = e_rts[e_idxs]-n_rts[n_idxs]
    return 2.0 * (0.01*percentileofscore(en_diffs, 0.0, kind='mean') - 0.5)

def _get_rt_meandiff(df):
    e_rts = df[df['condition']==EMOT_LIST[EMOT_IDX]]['rt'].values
    n_rts = df[df['condition']==EMOT_LIST[NEUT_IDX]]['rt'].values
    if (not e_rts.size) or (not n_rts.size):
        return np.nan
    return np.mean(n_rts) - np.mean(e_rts)

def _get_rt_mediandiff(df):
    e_rts = df[df['condition']==EMOT_LIST[EMOT_IDX]]['rt'].values
    n_rts = df[df['condition']==EMOT_LIST[NEUT_IDX]]['rt'].values
    if (not e_rts.size) or (not n_rts.size):
        return np.nan
    return np.median(n_rts) - np.median(e_rts)

def taskeffect_rt_difference(data_df, diff_type):
    # Note not looking at good or bad trials or subjs
    #  Do that before calling

    if diff_type == 'distribution_diff':
        diff_func = _get_rt_distdiff
    elif diff_type == 'mean_diff':
        diff_func = _get_rt_meandiff
    elif diff_type == 'median_diff':
        diff_func = _get_rt_mediandiff
    else:
        raise ValueError('diff_type not recognized')

    temp_df = data_df.copy()
    temp_df = temp_df[temp_df['hit']]

    temp_grp = temp_df.groupby(['subject_id', 'task_order'])
    dist_diffs = temp_grp.apply(diff_func)

    return (dist_diffs.reset_index()
                      .rename(columns={0:'plotval'})
                      .pivot(index='subject_id', columns='task_order', values='plotval'))
