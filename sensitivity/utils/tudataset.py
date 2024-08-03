import pickle

import torch
from torch.func import jacrev

from model import Model as Base


class Model(Base):
    
    def forward(self, edge_index, mask, x):
    
        for mp_layer in self.message_passing:
            x = mp_layer(x, edge_index)
    
        return x


def get_jacobian_norms(molecule, dir_name, n_samples, use_trained):

    with open(f'{dir_name}/config.pkl', 'rb') as f:
        config = pickle.load(f)

    model = Model(config)
    if use_trained:
        state_dict = torch.load(f'{dir_name}/ckpt-400.pt')
        model.load_state_dict(state_dict)
    model.train()

    jacobians = torch.zeros((molecule.num_nodes, config.gnn_layer_sizes[-1], molecule.num_nodes, config.input_dim))
    n_samples = n_samples if config.drop_p > 0. else 1
    for _ in range(n_samples):
        jacobians += jacrev(model, argnums=2)(molecule.edge_index, None, molecule.x)
    jacobians /= n_samples
    jacobian_norms = jacobians.transpose(1, 2).flatten(start_dim=2).norm(dim=2, p=1)

    return jacobian_norms