import pandas as pd

def select_tasks(data_df, task_id_list):
    if not isinstance(task_id_list, (tuple, list)):
        task_id_list = [task_id_list]
    return data_df[data_df['task_id'].isin(task_id_list)].reset_index(drop=True).copy()