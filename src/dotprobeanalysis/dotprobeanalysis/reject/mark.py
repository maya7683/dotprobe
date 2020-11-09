
import numpy as np
import pandas as pd

# Example params = {
#     'expected_n_trials': 48,
#     'min_rt': 75.0,
#     'max_rt': 550.0,
#     'min_good_trial_prp': 0.85,
#     'rt_outlier_cutoff_minmult': 9.0,
#     'rt_outlier_cutoff_maxmult': 8.0,
#     'max_subj_rtq3q1': 250.0,
#     'max_subj_rtmedian': 550.0,
#     'trial_n_range_min_pre': 1,
#     'trial_n_range_max_pre': 48,
#     'trial_n_range_min_pst': 1,
#     'trial_n_range_max_pst': 48,
# }

def find_trial_rt_cutoffs(df, min_rt, max_rt):
    ok_ser = pd.Series(True, index=df.index, name='ok_rtcutoff')
    if min_rt is not None:
        ok_ser.update(df['rt'] >= min_rt)
    if max_rt is not None:
        ok_ser.update((df['rt'] <= max_rt) & ok_ser)
    return ok_ser

def find_trial_rt_outliers(df, lomult, himult, loclip=8.0, hiclip=8.0):
    # RT > 2Q+(3Q-2Q)*lomult OR RT < 2Q-(2Q-1Q)*himult
    # Only considers trials with ok_trl == True
    def q1(x):
        return x.quantile(0.25)
    def q2(x):
        return x.quantile(0.50)
    def q3(x):
        return x.quantile(0.75)
    ok_ser = pd.Series(True, index=df.index, name='ok_rtoutlier')
    ok_ser.update(ok_ser & df['ok_trl'])
    if (himult is not None) or (lomult is not None):
        t_grp = df[df['ok_trl']].groupby(['subject_id', 'task_order'])
        grp_q2 = t_grp['rt'].transform(q2)
    if himult is not None:
        grp_q3 = t_grp['rt'].transform(q3)
        grp_q3_minus_q2 = (grp_q3 - grp_q2).clip(lower=hiclip)
        grp_cutoff_top = grp_q2 + grp_q3_minus_q2 * himult
        ok_ser.update(ok_ser & (df[df['ok_trl']]['rt'] <= grp_cutoff_top))
    if lomult is not None:
        grp_q1 = t_grp['rt'].transform(q1)
        grp_q2_minus_q1 = (grp_q2 - grp_q1).clip(lower=loclip)
        grp_cutoff_bot = grp_q2 - grp_q2_minus_q1 * lomult
        ok_ser.update(ok_ser & (df[df['ok_trl']]['rt'] >= grp_cutoff_bot))
    return ok_ser

def find_subj_insufficient_ok_trials(df, min_proportion):
    # Assumes no missing trial rows in order to calculate the expected total
    #  number of trials

    ok_ser = pd.Series(True, index=df.index, name='ok_subjntrls')

    if min_proportion is None:
        return ok_ser

    t_grp = df.groupby(['subject_id', 'task_order'])
    alltrial_sums = t_grp['ok_trl'].transform(len)
    goodtrial_sums = t_grp['ok_trl'].transform(np.sum)
    ok_ser.update((goodtrial_sums / alltrial_sums) >= min_proportion)
    
    # Any false value makes the subject false
    t_df = df.join(ok_ser)
    ok_ser.update(t_df.groupby(['subject_id'])['ok_subjntrls'].transform(np.all))

    return ok_ser

def find_subj_long_rt(df, max_median_rt):
    # 

    ok_ser = pd.Series(True, index=df.index, name='ok_subjmedrt')

    if max_median_rt is None:
        return ok_ser

    t_grp = df[df['ok_trl']].groupby(['subject_id', 'task_order'])
    grp_med = t_grp['rt'].transform(np.median)
    ok_ser.update(grp_med <= max_median_rt)

    # Any false value makes the subject false
    t_df = df.join(ok_ser)
    ok_ser.update(t_df.groupby(['subject_id'])['ok_subjmedrt'].transform(np.all))

    return ok_ser

def find_subj_range_rt(df, max_range):
    # Find subjects with 3Q-1Q rt too long in PRE or POST

    def q3_q1(x):
        return x.quantile(0.75) - x.quantile(0.25)
    
    ok_ser = pd.Series(True, index=df.index, name='ok_subjrngrt')

    if max_range is None:
        return ok_ser

    t_grp = df[df['ok_trl']].groupby(['subject_id', 'task_order'])
    grp_rng = t_grp['rt'].transform(q3_q1)
    ok_ser.update(grp_rng <= max_range)

    # Any false value makes the subject false
    t_df = df.join(ok_ser)
    ok_ser.update(t_df.groupby(['subject_id'])['ok_subjrngrt'].transform(np.all))
    
    return ok_ser


def mark_drops_independent(df, pdct):

    # Do not change in-place. Return changed df
    df = df.copy()

    # Init ok subj col
    df['ok_sbj'] = True

    # Init ok trial col
    df['ok_trl'] = True
    df['ok_trl'] = df['ok_trl'] & df['hit']

    # Find RTs outside of specified range
    ok_rtcutoff = find_trial_rt_cutoffs(df, pdct['min_rt'], pdct['max_rt'])
    df['ok_trl'] = df['ok_trl'] & ok_rtcutoff

    # Find outlier RTs within subject and task order
    ok_rtoutlier = find_trial_rt_outliers(df,
                                          pdct['rt_outlier_cutoff_minmult'],
                                          pdct['rt_outlier_cutoff_maxmult'])
    df['ok_trl'] = df['ok_trl'] & ok_rtoutlier
    
    # Find subjects without enough good_trials in PRE or POST
    ok_subjntrls = find_subj_insufficient_ok_trials(df, pdct['min_good_trial_prp'])
    
    # Mark subjects with median rt too long in PRE or POST
    ok_subjmedrt = find_subj_long_rt(df, pdct['max_subj_rtmedian'])

    # Mark subjects with 3Q-1Q rt too long in PRE or POST
    ok_subjrngrt = find_subj_range_rt(df, pdct['max_subj_rtq3q1'])

    df['ok_sbj'] = df['ok_sbj'] & ok_subjntrls & ok_subjmedrt & ok_subjrngrt

    return df









