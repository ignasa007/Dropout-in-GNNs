import argparse
import os
import pickle

import numpy as np
from scipy.stats import wilcoxon
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def main(args):

    args.dataset = args.dataset.split('_')[0]

    with open(f'./results/signal-propagation/{args.vs}/{args.dataset}.pkl', 'rb') as f:
        pairs = pickle.load(f)

    Ps = np.arange(0.0, 1.0, 0.1)
    data = np.array([list(zip(*pairs[P]))[1] for P in Ps])
    corr = wilcoxon(np.expand_dims(data, 0) - np.expand_dims(data, 1), alternative='greater', zero_method='zsplit', axis=2)

    Ps = list(map(lambda x: round(x, 1), Ps))
    fig, ax = plt.subplots(1, 1, figsize=(5.2, 4.8))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.1)

    im = ax.imshow(corr.statistic, cmap='coolwarm')
    cbar = fig.colorbar(im, cax=cax, orientation='vertical')
    cbar.formatter.set_powerlimits((0, 0))
    ax.scatter(*np.where(corr.pvalue<0.05), c='green', s=50)

    ax.set_xticks(np.arange(len(Ps))); ax.set_xticklabels(Ps)
    ax.set_yticks(np.arange(len(Ps))); ax.set_yticklabels(Ps)
    ax.set_title(args.dataset, fontsize=16)
    ax.set_xlabel(r'$p_1$', fontsize=14)
    ax.set_ylabel(r'$p_2$', fontsize=14)
    fig.tight_layout()

    fn = f'assets/signal-propagation/{args.vs}/rank-correlation/{args.dataset}.png'
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    plt.savefig(fn)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, required=True, choices=['Proteins', 'MUTAG', 'PTC_MR'])
    parser.add_argument('--vs', type=str, required=True, choices=['Total Resistance', 'Commute Time'])
    args = parser.parse_args()
    
    main(args)