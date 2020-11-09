from datetime import datetime
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm.auto import tqdm

def _logpath_to_dataframe(log_path):

  subj_id, task_id, datenum, timenum, uniq_id = log_path.stem.split('-')
  task_order = task_id.split('_')[-1]
  task_id = '_'.join(task_id.split('_')[:-1])

  # open and read file contents
  df = pd.read_csv(log_path, sep='\t')
  df['subject_id'] = subj_id
  df['task_order'] = task_order
  df['task_id'] = task_id
  df['uid'] = uniq_id
  df['date'] = datetime.strptime(datenum+timenum, '%Y%m%d%H%M%S')

  df['task_order'] = df['task_order'].astype('category')
  df['Dot Side'] = df['Dot Side'].astype('category')
  df['Block'] = df['Block'].astype('category')
  df['Condition'] = df['Condition'].astype('category')
  df['Response'] = df['Response'].astype('category')
  df['Accuracy'] = df['Accuracy'].astype('category')
  df['Left Stim'] = df['Left Stim'].astype('string')
  df['Right Stim'] = df['Right Stim'].astype('string')
  df['Trial Number'] = df['Trial Number'].astype(np.int16)
  df['subject_id'] = df['subject_id'].astype('string')
  df['task_id'] = df['task_id'].astype('string')
  df['uid'] = df['uid'].astype('string')

  df['emo_rating'] = np.nan
  df['neu_rating'] = np.nan

  try:
    summary_path = log_path.parent.joinpath(log_path.stem + '-Summary.txt')
    if task_order == "PRE":
      summary_glob = subj_id + '-' + task_id + '_POST*-Summary.txt'
      summary_path = list(log_path.parent.glob(summary_glob))[0]

    summary_df = pd.read_csv(summary_path, sep='\t')
    df['emo_rating'] = summary_df['EmotionRating'][0].replace('R','')
    df['neu_rating'] = summary_df['NeutralRating'][0].replace('R','')
  except (IndexError, FileNotFoundError):
    print(summary_path.name)
  
  df['hit'] = df['Accuracy'] == 'rm_hit'
  df['miss'] = df['Accuracy'] == 'rm_miss'
  df['incorrect'] = df['Accuracy'] == 'rm_incorrect'

  col_rename_dict = {
    'task_id':'task_id',
    'subject_id':'subject_id',
    'task_order':'task_order',
    'date':'date',
    'emo_rating':'emo_rating',
    'neu_rating':'neu_rating',
    'Block':'block_type',
    'Trial Number':'trial_n',
    'Condition':'condition',
    'Dot Side':'dot_side',
    'Left Stim':'left_stim',
    'Right Stim':'right_stim',
    'Response':'response',
    'Accuracy':'accuracy',
    'RT':'rt',
    'uid':'uid',
    'hit':'hit',
    'miss':'miss',
    'incorrect:':'incorrect'
  }

  ordered_cols = [
    'task_id',
    'subject_id',
    'task_order',
    'date',
    'emo_rating',
    'neu_rating',
    'Block',
    'Trial Number',
    'Condition',
    'Dot Side',
    'Left Stim',
    'Right Stim',
    'Response',
    'Accuracy',
    'RT',
    'uid',
    'hit',
    'miss',
    'incorrect'
  ]

  df = df[ordered_cols]

  df = df.rename(columns=col_rename_dict)

  return df
  

def get_raw_data(data_path, use_existing_file=False):
  if use_existing_file:
    print('Using file')
    all_df = pd.read_pickle(data_path.joinpath('_alldata.pkl.gz'))
  else:
    log_paths = [x for x in data_path.glob("*.txt") if not "Summary" in x.stem]
    log_paths = [x for x in log_paths if not "_PRAC-" in x.stem]
    all_df = pd.DataFrame()
    for log_path in tqdm(log_paths):
      try:
        this_df = _logpath_to_dataframe(log_path)
      except KeyboardInterrupt:
        raise
      except Exception as e:
        print('{}\n\t{}\n--------'.format(log_path, e))
        raise
      all_df = all_df.append(this_df)
    all_df.to_pickle(data_path.joinpath('_alldata.pkl.gz'))
  
  return all_df