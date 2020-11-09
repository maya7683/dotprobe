
import pandas as pd
from random import sample

from ..reject import drop_practice_trials

def full_preprocess(data_file_path, task_id_list, param_dict,
                    select_subj_subset=None, quiet=False):

    data_file_path = Path(data_file_path).resolve(strict=True)
    if not quiet:
        print('Reading data from [{}]'.format(data_file_path))
    data_df = pd.read_pickle(data_file_path)

    # Drop practice
    if not quiet:
        print('Dropping practice trials')
    data_df = drop_practice_trials(data_df)

    # Drop participants with missing data
    if not quiet:
        print('Dropping participants with missing data')
    data_df = drop_participants_with_missing_data(data_df, param_dict)

    # Keep only task_id_list
    if not isinstance(task_id_list, list):
        task_id_list = [task_id_list]
    if not quiet:
        print('Selecting TASK_ID(s): {}'.format(task_id_list))
    data_df = data_df[data_df['task_id'].isin(task_id_list)].reset_index(drop=True).copy()

    # Drop unused columns
    if not quiet:
        print('Dropping unused columns')
    data_df = data_df.drop(columns=[
        'task_id',
        'accuracy', 'uid', 'response',
        'left_stim', 'right_stim', 'dot_side',
        'block_type', 'emo_rating', 'neu_rating',
        'date']).copy()
    
    subj_list = list(data_df['subject_id'].unique())
    if select_subj_subset:
        if not quiet:
            print('Selecting random subset of {} subjects'.format(select_subj_subset))
        sub_subjs = sample(subj_list, select_subj_subset)
        data_df = data_df[data_df['subject_id'].isin(sub_subjs)].reset_index(drop=True).copy()
    subj_list = list(data_df['subject_id'].unique())

    # Drop trials outside desired range
    if not quiet:
        print('Dropping trials outside specified range: PRE[{}-{}], PST[{}-{}]'.format(
            param_dict['trial_n_range_min_pre'], param_dict['trial_n_range_max_pre'],
            param_dict['trial_n_range_min_pst'], param_dict['trial_n_range_max_pst']))
    data_df = drop_trials_outside_range(data_df,
        (param_dict['trial_n_range_min_pre'], param_dict['trial_n_range_max_pre']),
        (param_dict['trial_n_range_min_pst'], param_dict['trial_n_range_max_pst']))

    # Mark participants and trials to drop
    if not quiet:
        print('Marking trials and participants to drop based on preprocessing params')
    data_df = mark_drops_independent(data_df, param_dict)

    if not quiet:
        print('-'*80)
        print('Before drop')
        print('\tTotal participants: {:3d}'.format(len(subj_list)))
        print('\tTotal trials:       {:5d}'.format(len(data_df.index)))

        n_subj_after_drop = len(data_df[data_df['ok_sbj']]['subject_id'].unique())
        n_trls_after_drop = len(data_df[(data_df['ok_sbj']) & (data_df['ok_trl'])].index)
        print('After drop')
        print('\tTotal participants: {:3d}'.format(n_subj_after_drop))
        print('\tTotal trials:       {:5d}'.format(n_trls_after_drop))

    return data_df.copy()

