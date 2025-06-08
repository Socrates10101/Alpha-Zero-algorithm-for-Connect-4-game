#  ================ AlphaZero algorithm for 3D Connect 4 game =================== #
# Name:             ResNet3D.py
# Description:      ResNet architecture adapted for 3D Connect 4 (4x4x4 board)
# Authors:          AI Assistant
# Date:             2025
# License:          BSD 3-Clause License
# ============================================================================ #

# ================================= PREAMBLE ================================= #
# Packages
import torch
import torch.utils
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim
import torch.utils.data
import time
import math
from collections import OrderedDict
import torch.utils.data
import numpy as np
import config3d
import random

# ================================= CLASS : basic ResNet Block ================================= #

#no bias in conv
def conv3x3(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride, padding=1, bias=False)


class BasicBlock3D(nn.Module):
    expansion = 1
    def __init__(self, inplanes, planes, stride=1, downsample=None):
        super(BasicBlock3D, self).__init__()

        m = OrderedDict()
        m['conv1'] = conv3x3(inplanes, planes, stride)
        m['bn1'] = nn.BatchNorm2d(planes)
        m['relu1'] = nn.ReLU(inplace=True)
        m['conv2'] = conv3x3(planes, planes)
        m['bn2'] = nn.BatchNorm2d(planes)
        self.group1 = nn.Sequential(m)

        self.relu = nn.Sequential(nn.ReLU(inplace=True))
        self.downsample = downsample

    def forward(self, x):
        if self.downsample is not None:
            residual = self.downsample(x)
        else:
            residual = x

        out = self.group1(x) + residual
        out = self.relu(out)

        return out

# ================================= CLASS : ResNet3D + two heads ================================= #

class ResNet3D(nn.Module):
    def __init__(self, block, layers):

        self.input_dim = config3d.SIZE * config3d.SIZE  # 4*4 = 16 per layer
        self.output_dim = config3d.OUTPUT_SIZE  # 16 possible moves
        self.inplanes = config3d.convsize
        self.convsize = config3d.convsize
        super(ResNet3D, self).__init__()

        torch.set_num_threads(1)

        # For 3D Connect 4, we have 3 channels (player1, player2, current_player) 
        # each representing a 4x4 layer projection of the 3D board
        # We'll use multiple 4x4 layers to represent the 3D structure
        
        # Since we have a 4x4x4 board, we can represent it as 12 channels of 4x4
        # 4 channels for player1 (one per z-level), 4 for player2, 4 for current player
        self.input_channels = 12  # 4*3
        
        # Convolutional entry - adapted for 4x4 input
        m = OrderedDict()
        # For 4x4 input, we use 3x3 kernel with padding to maintain size
        m['conv1'] = nn.Conv2d(self.input_channels, self.convsize, kernel_size=3, stride=1, padding=1, bias=False)
        m['bn1'] = nn.BatchNorm2d(self.convsize)
        m['relu1'] = nn.ReLU(inplace=True)

        self.group1 = nn.Sequential(m)

        # ResNet tower
        self.layer1 = self._make_layer(block, self.convsize, layers[0])

        # Policy head - outputs 16 moves (4x4 columns)
        pol_filters = config3d.polfilters
        self.policy_entrance = nn.Conv2d(self.convsize, config3d.polfilters, kernel_size=1, stride=1, padding=0, bias=False)
        self.bnpolicy = nn.BatchNorm2d(config3d.polfilters)
        self.relu_pol = nn.ReLU(inplace=True)

        # After conv, we have pol_filters * 4 * 4 = pol_filters * 16
        policy_flat_size = pol_filters * 16
        
        if config3d.usehiddenpol:
            self.hidden_dense_pol = nn.Linear(policy_flat_size, config3d.hiddensize)
            self.relu_hidden_pol = nn.ReLU(inplace=True)
            self.fcpol1 = nn.Linear(config3d.hiddensize, 16)  # 16 moves for 3D
        else:
            self.fcpol2 = nn.Linear(policy_flat_size, 16)  # 16 moves for 3D

        self.softmaxpol = nn.Softmax(dim=1)

        # Value head
        val_filters = config3d.valfilters
        self.value_entrance = nn.Conv2d(self.convsize, config3d.valfilters, kernel_size=1, stride=1, padding=0, bias=False)
        self.bnvalue = nn.BatchNorm2d(config3d.valfilters)
        self.relu_val = nn.ReLU(inplace=True)

        # Value head dense layers
        value_flat_size = val_filters * 16  # val_filters * 4 * 4
        self.hidden_dense_value = nn.Linear(value_flat_size, config3d.hiddensize)
        self.relu_hidden_val = nn.ReLU(inplace=True)
        self.fcval = nn.Linear(config3d.hiddensize, 1)
        self.qval = nn.Tanh()

        # Initialize weights
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                n = m.kernel_size[0] * m.kernel_size[1] * m.out_channels
                m.weight.data.normal_(0, math.sqrt(2. / (5*n)))
            elif isinstance(m, nn.BatchNorm2d):
                m.weight.data.fill_(1)
                m.bias.data.zero_()

    def _make_layer(self, block, planes, blocks, stride=1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.inplanes, planes * block.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(planes * block.expansion),
            )

        layers = []
        layers.append(block(self.inplanes, planes, stride, downsample))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.inplanes, planes))

        return nn.Sequential(*layers)

    def _convert_3d_to_input(self, state_vector):
        """
        Convert 3D game state vector to neural network input format.
        Input: state_vector of length 192 (64*3)
        Output: tensor of shape (12, 4, 4) representing the 3D board
        """
        # state_vector format: [player1_board(64), player2_board(64), current_player(64)]
        player1_flat = state_vector[:64]
        player2_flat = state_vector[64:128]
        current_player_flat = state_vector[128:]
        
        # Reshape each to 4x4x4 and then to 4 layers of 4x4
        player1_3d = player1_flat.reshape(4, 4, 4)  # (x, y, z)
        player2_3d = player2_flat.reshape(4, 4, 4)
        current_player_3d = current_player_flat.reshape(4, 4, 4)
        
        # Stack z-layers to create 12 channels of 4x4 each
        channels = []
        for z in range(4):
            channels.append(torch.FloatTensor(player1_3d[:, :, z]))     # Player 1 at level z
        for z in range(4):
            channels.append(torch.FloatTensor(player2_3d[:, :, z]))     # Player 2 at level z  
        for z in range(4):
            channels.append(torch.FloatTensor(current_player_3d[:, :, z]))  # Current player at level z
            
        # Stack to create (12, 4, 4) tensor
        result = torch.stack(channels, dim=0)
        return result

    def forward(self, x):
        if type(x) == np.ndarray:
            # Convert 3D state vector to proper input format
            x = self._convert_3d_to_input(x)
            x = torch.FloatTensor(x)
            x = torch.unsqueeze(x, 0)  # Add batch dimension

        x = self.group1(x)
        x = self.layer1(x)

        # Policy head
        x1 = self.policy_entrance(x)
        x1 = self.bnpolicy(x1)
        x1 = self.relu_pol(x1)
        x1 = x1.view(-1, config3d.polfilters * 16)  # Flatten to policy_flat_size

        if config3d.usehiddenpol:
            x1 = self.hidden_dense_pol(x1)
            x1 = self.relu_hidden_pol(x1)
            x1 = self.fcpol1(x1)
        else:
            x1 = self.fcpol2(x1)

        x1 = self.softmaxpol(x1)

        # Value head
        x2 = self.value_entrance(x)
        x2 = self.bnvalue(x2)
        x2 = self.relu_val(x2)
        x2 = x2.view(-1, 16 * config3d.valfilters)  # Flatten to value_flat_size
        x2 = self.hidden_dense_value(x2)
        x2 = self.relu_hidden_val(x2)
        x2 = self.fcval(x2)
        x2 = self.qval(x2)

        return x2, x1

# -----------------------------------------------------------------#
# builds the 3D model
def resnet18_3d(pretrained=False, model_root=None, **kwargs):
    model = ResNet3D(BasicBlock3D, [config3d.res_tower, 2, 2, 2], **kwargs)
    return model


# ================================= CLASS : ResNet3D training ================================= #

class ResNet3D_Training:
    # -----------------------------------------------------------------#
    def __init__(self, net, batch_size, n_epoch, learning_rate, train_set, test_set, num_worker):
        self.net = net
        self.batch_size = batch_size
        self.n_epochs = n_epoch
        self.learning_rate = learning_rate
        self.num_worker = num_worker
        torch.set_num_threads(1)

        if config3d.use_cuda:
            self.net = self.net.cuda()

        # Training data
        self.train_set = train_set
        self.test_set = test_set

        # Loss functions
        self.criterion_value = nn.MSELoss()
        self.criterion_policy = nn.CrossEntropyLoss()

        # Optimizer
        if config3d.optim == 'sgd':
            self.optimizer = optim.SGD(self.net.parameters(), lr=learning_rate, 
                                     momentum=config3d.momentum, weight_decay=config3d.wdecay)
        elif config3d.optim == 'adam':
            self.optimizer = optim.Adam(self.net.parameters(), lr=learning_rate, 
                                      weight_decay=config3d.wdecay)

    def train(self):
        self.net.train()
        for epoch in range(self.n_epochs):
            train_loader = torch.utils.data.DataLoader(
                self.train_set, batch_size=self.batch_size, shuffle=True, num_workers=self.num_worker)
            
            for batch_idx, (data, policy_target, value_target) in enumerate(train_loader):
                if config3d.use_cuda:
                    data, policy_target, value_target = data.cuda(), policy_target.cuda(), value_target.cuda()

                self.optimizer.zero_grad()
                value_output, policy_output = self.net(data)
                
                value_loss = self.criterion_value(value_output, value_target)
                policy_loss = self.criterion_policy(policy_output, policy_target)
                
                total_loss = value_loss + policy_loss
                total_loss.backward()
                self.optimizer.step()

        return self.net