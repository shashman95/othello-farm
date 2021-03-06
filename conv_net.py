import numpy as np
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms
from stateB import State
import torch.nn.functional as F
import torch.optim as optim
import random

seed = 42
np.random.seed(seed)
torch.manual_seed(seed)

learning_rate = 0.001
batch_size = 100
num_epochs = 10
num_classes = 64
in_channels = 3
class ConvNet(nn.Module):
    def __init__(self, conv_encodings, fc_encodings):
        super(ConvNet, self).__init__()

        self.conv_encodings = conv_encodings
        self.fc_encodings = fc_encodings
        # conv layers
        for i, encoding in enumerate(conv_encodings):
            exec(self.str_convx(encoding, i))
        # fc layers
        for i, encoding in enumerate(fc_encodings):
            exec(self.str_fcx(encoding, i))
        
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.SGD(self.parameters(), lr=learning_rate, momentum=0.2)
        



        # old init:
        # self.conv0 = nn.Conv2d(in_channels, 64, kernel_size=3, stride=1, padding=1)
        # self.conv1 = nn.Conv2d(64, 64, kernel_size=5, stride=1, padding=1)
        # self.fc0 = nn.Linear(57600, 1000)#64*36, 1000)
        # self.fc1 = nn.Linear(1000, num_classes)
        # self.criterion = nn.CrossEntropyLoss()
        # self.optimizer = optim.SGD(self.parameters(), lr=learning_rate, momentum=0.2)
        
    def str_convx(self, encoding, n):
        return "self.conv{} = nn.Conv2d({}, {}, kernel_size={}, stride=1, padding={})\n".format(n, encoding.get('in_channels'), encoding.get('num_filters'), encoding.get('kernel_size'), encoding.get('padding'))

    def str_fcx(self, encoding, n):
        return "self.fc{} = nn.Linear({}, {})\n".format(n, encoding.get('inputs'), encoding.get('outputs'))

    def gen_conv_encodings(self):
        pass
        # ((old_num_filters)^1/2-kernel_size+1)^2 = new_in_channels

    def str_run_convx(self):
        s = []
        for i in range(1, len(self.conv_encodings)):
            s.append('out = F.relu(self.conv{}(out))\n'.format(i))
        return ''.join(s)

    def str_run_fcx(self):
        s = []
        for i in range(0, len(self.fc_encodings)):
            s.append('out = F.relu(self.fc{}(out))\n'.format(i))
        return ''.join(s)

    def forward(self, x):
        out = F.relu(self.conv0(x))
        exec(self.str_run_convx())
        # self.str_run_convx()
        out = F.relu(out.reshape(out.size(0), -1))
        print('[[[[[[[[[[[[[[[[[[[[[[[[[[[]]]]]]]]]]]]]]]]]]]]]]]]]]]')
        exec(self.str_run_fcx())
        return out
        
        #old forward:
        # out = F.relu(self.conv0(x))
        # out = F.relu(self.conv1(out))
        # out = F.relu(out.reshape(out.size(0), -1))
        # out = self.fc0(out)
        # out = self.fc1(out)
        # return out
        

    def train_on_batch(self, in_batch, label_batch, epochs, learning_rate):
        
        for _ in range(epochs):
            self.optimizer.zero_grad()
            outputs = self(in_batch)
            # loss = criterion(outputs, label_batch.long())
            loss = self.criterion(outputs, torch.max(label_batch, 1)[1])
            loss.backward()
            self.optimizer.step()

    def forward_indices(self, x):
        return torch.max(self.forward(x), 1)

    
    def clone(self, mutations=False):
        '''
        returns clone of net
        point mutates weights randomly if mutate=True
        '''
        # make clone
        clone = ConvNet()
        clone.load_state_dict(self.state_dict())
        if mutations:
            #conv1
            clone.conv1.weight.data.add_(ConvNet.generate_mutations(self.conv1, .0005, 150))
            
            # fc1
            clone.fc1.weight.data.add_(ConvNet.generate_mutations(self.fc1, .0005, 150))

            # fc2
            clone.fc2.weight.data.add_(ConvNet.generate_mutations(self.fc2, .0005, 150))
        return clone

    @staticmethod
    def generate_conv_encoding(in_channels, num_filters, kernel_size, padding):
        return {'in_channels': in_channels, 'num_filters': num_filters, 'kernel_size': kernel_size, 'padding':padding}
    
    def generate_fc_encoding(inputs, outputs):
        return {'inputs':inputs, 'outputs':outputs}

    @staticmethod
    def conv_layer_from_encoding(encoding):
        return nn.Conv2d(encoding.get('in_channels'), encoding.get('num_filters'), kernel_size=encoding.get('kernel_size'), stride=1, padding=encoding.get('padding'))

    @staticmethod
    def conv_layer(n_ch, n_fil, kernel_s, pad):
        return ConvNet.conv_layer_from_encoding(ConvNet.generate_conv_encoding(n_ch, n_fil, kernel_s, pad))

    @staticmethod
    def generate_mutations(net_layer, bound, rate_denom):
        '''
        rate_denom: the chance of mutation is 1/rate_denom
        bound: mutations range from -bound to bound
        net_layer: is for example net.conv1
        returns tensor same size as layer with zeroes and a few mutations.
        to apply mutation: add returned tensor to net.layer.weight.data like layer.weight.data.add_(returned tensor)
        '''
        shape = net_layer.weight.size()
        mutations = torch.empty(shape).uniform_(-bound, bound)
        mask = torch.randint(0, rate_denom, shape)
        masked_mutations = torch.where(mask==0, mutations, torch.zeros(shape))
        
        return masked_mutations 

def main():
    

    conv_encodings = [ConvNet.generate_conv_encoding(3, 64, 3, 1)]
    fc_encodings = [ConvNet.generate_fc_encoding(57600, 1000)]
    net = ConvNet(conv_encodings, fc_encodings)
    print(net)



    # print(ConvNet.conv_layer(4, 64, 5, 2))
    # n = ConvNet()
    # layer = n.state_dict().get('conv1.weight')
    # print(layer.size())
    # channels = 3
    # k_size = 3
    # new_filter = torch.ones(channels,k_size,k_size)
    # print(new_filter)

    # # print(layer)
    # # print('\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')
    # # print(layer.unbind())
    # new_layer = torch.stack((layer.unbind(), new_filter))
    # print(new_layer.size())
    # # torch.cat([layer], new_filter)

    # print(layer.size())


if __name__ == '__main__':
    main()