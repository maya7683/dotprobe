
from matplotlib import pyplot as plt
import seaborn as sns

def plot_single_bar_with_dots(data_df, x_col_name, y_col_name, y_col_order,
                              x_label=None, x_ticks=None,
                              figsize=None):

    fig, ax = plt.subplots(nrows=1, ncols=1,
                           sharex=True, sharey=True,
                           figsize=figsize, squeeze=False)
    fig.subplots_adjust(hspace=0.1, wspace=0.2)

    sns.stripplot(data=data_df,
                  x=x_col_name, y=y_col_name, order=y_col_order,
                  orient='h',
                  s=4, jitter=0.2,
                  ax=ax[0,0])

    sns.barplot(data=data_df,
                x=x_col_name, y=y_col_name, order=y_col_order,
                orient='h',
                saturation=0.3,
                estimator=np.mean,
                ci=68, # SEM
                ax=ax[0,0])

    if x_ticks is not None:
        ax[0,0].set_xlim(x_ticks[0], x_ticks[-2])
        ax[0,0].set_xticks(x_ticks)
    if x_label is not None:
        ax[0,0].set_xlabel(x_label)
    else:
        ax[0,0].set_xlabel('', fontsize=6)
    ax[0,0].grid(axis='x', linewidth=0.25)
    plt.xticks(rotation=25)

    fig.set_edgecolor('black')

    return fig, ax

