
from itertools import islice
from matplotlib import pyplot as plt
import seaborn as sns
import warnings

def plot_all_participant_rts(data_df):

    subjs_per_row = 100
    y_limits = (50.0, 1050.0)

    # Ensure data_df is not modified
    temp_df = data_df.copy()

    # Use only hit trials
    temp_df = temp_df[temp_df['hit']]

    # Get list of subj_ids sorted by median rt (before drops)
    subj_ids = list(temp_df['subject_id'].unique())
    temp_grp = temp_df.groupby(['subject_id'])
    sorted_sids = temp_grp['rt'].apply(np.median).sort_values(ascending=False).index.to_list()

    # Split by plotting row
    subj_ids_rows = [sorted_sids[i:i + subjs_per_row] for i in range(0, len(sorted_sids), subjs_per_row)]
    n_rows = len(subj_ids_rows)

    fig, ax = plt.subplots(nrows=n_rows, ncols=1,
                           sharex=True, sharey=True,
                           figsize=(18,n_rows*5), squeeze=False)
    fig.subplots_adjust(hspace=0.1, wspace=0.2)

    row_n = 0
    for row_n in range(n_rows):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            dirty_df = temp_df[~(temp_df['ok_sbj']) | ~(temp_df['ok_trl'])]
            sns.stripplot(data=dirty_df[temp_df['subject_id'].isin(subj_ids_rows[row_n])],
                          x='subject_id', y='rt', order=subj_ids_rows[row_n],
                          jitter=0.25, color='gray', s=3,
                          ax=ax[row_n,0])
            clean_df = temp_df[(temp_df['ok_sbj']) & (temp_df['ok_trl'])]
            sns.stripplot(data=clean_df[temp_df['subject_id'].isin(subj_ids_rows[row_n])],
                          x='subject_id', y='rt', order=subj_ids_rows[row_n],
                          jitter=0.25, color='red', s=3,
                          ax=ax[row_n,0])
            ax[row_n,0].xaxis.label.set_visible(False)
            ax[row_n,0].xaxis.set_ticklabels([])
            ax[row_n,0].set_yticks(np.arange(np.ceil(y_limits[0]/100.0)*100.0,
                                             y_limits[1], 100.0))
            ax[row_n,0].set_xticks(np.arange(0.5, subjs_per_row+1.5, 1.0))
            ax[row_n,0].grid(axis='both', linewidth=0.25)
    
    ax[-1,0].set_ylim(y_limits[0], y_limits[1])
    ax[-1,0].set_xlim(-1.0, subjs_per_row)


    ax[0,0].set_title('Participant RTs - red means included in analysis')


