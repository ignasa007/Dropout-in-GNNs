from argparse import Namespace
from typing import Union

from torch import Tensor, BoolTensor
from torch.nn import Module, ModuleList
from torch_geometric.typing import Adj

from model.gnn import get_activation, get_layer
from model.ffn import get_head
from dropout import get_dropout


class Model(Module):

    def __init__(self, input_dim: int, output_dim: int, args: Namespace):
        
        super(Model, self).__init__()
        
        drop_strategy = get_dropout(args.dropout)(args.drop_p)
        gnn_layer = get_layer(args.gnn)
        gnn_layer_sizes = [input_dim] + args.gnn_layer_sizes
        self.message_passing = ModuleList()
        for in_channels, out_channels in zip(gnn_layer_sizes[:-1], gnn_layer_sizes[1:]):
            self.message_passing.append(gnn_layer(
                in_channels=in_channels,
                out_channels=out_channels,
                drop_strategy=drop_strategy,
                activation=get_activation(args.gnn_activation)(),
                add_self_loops=args.add_self_loops,
                normalize=args.normalize,
            ))

        ffn_head = get_head(args.task)
        ffn_layer_sizes = args.gnn_layer_sizes[-1:] + args.ffn_layer_sizes + [output_dim]
        self.readout = ffn_head(
            layer_sizes=ffn_layer_sizes,
            activation=get_activation(args.ffn_activation)(),
        )

    def forward(
        self,
        x: Tensor,
        edge_index: Adj,
        mask: Union[Tensor, BoolTensor, None] = None,
    ):

        for mp_layer in self.message_passing:
            x = mp_layer(x, edge_index)
               
        out = self.readout(x, mask)

        return out