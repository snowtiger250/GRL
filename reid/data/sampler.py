from __future__ import absolute_import
from collections import defaultdict

import numpy as np
import torch

from torch.utils.data.sampler import (
    Sampler, SequentialSampler, RandomSampler, SubsetRandomSampler,
    WeightedRandomSampler)


def No_index(a, b):  # a = <class 'list'>: [2, 2, 3, 4, 4, 4]  b = 4
    assert isinstance(a, list)
    return [i for i, j in enumerate(a) if j != b]


class RandomIdentitySampler(Sampler):

    def __init__(self, data_source, num_instances=1):
        self.data_source = data_source
        self.num_instances = num_instances
        self.index_dic = defaultdict(list)
        for index, (_, pid, _) in enumerate(data_source):
            self.index_dic[pid].append(index)
        self.pids = list(self.index_dic.keys())
        self.num_samples = len(data_source)

    def __len__(self):
        return self.num_samples * self.num_instances

    def __iter__(self):
        indices = torch.randperm(self.num_samples)
        ret = []
        for i in indices:
            pid = self.pids[i]
            t = self.index_dic[pid]
            if len(t) >= self.num_instances:
                t = np.random.choice(t, size=self.num_instances, replace=False)
            else:
                t = np.random.choice(t, size=self.num_instances, replace=True)
            ret.extend(t)
        return iter(ret)


class RandomPairSampler(Sampler):
    def __init__(self, data_source):
        self.data_source = data_source
        self.index_pid = defaultdict(int)
        self.pid_cam = defaultdict(list)
        self.pid_index = defaultdict(list)
        self.num_samples = len(data_source)
        for index, (_, _, _, pid, cam) in enumerate(data_source):
            self.index_pid[index] = pid
            self.pid_cam[pid].append(cam)
            self.pid_index[pid].append(index)

    def __len__(self):
        return self.num_samples * 2

    def __iter__(self):
        indices = torch.randperm(self.num_samples)
        ret = []
        for i in indices:
            i = int(i)
            _, _, i_label, i_pid, i_cam = self.data_source[i]  # relabel ?
            ret.append(i)
            pid_i = self.index_pid[i]
            cams = self.pid_cam[pid_i]
            index = self.pid_index[pid_i]
            select_cams = No_index(cams, i_cam)
            try:
                select_camind = np.random.choice(select_cams)
            except ValueError:
                print(cams)
                print(pid_i)
                print(i_label)
            select_ind = index[select_camind]
            ret.append(select_ind)

        return iter(ret)


class RandomPairSamplerForMars(Sampler):
    def __init__(self, data_source):
        self.data_source = data_source
        self.index_pid = defaultdict(int)
        self.pid_cam = defaultdict(list)
        self.pid_index = defaultdict(list)
        self.num_samples = len(data_source)
        for index, (_, pid, cam) in enumerate(data_source):
            self.index_pid[index] = pid
            self.pid_cam[pid].append(cam)
            self.pid_index[pid].append(index)

    def __len__(self):
        return self.num_samples * 2

    def __iter__(self):
        indices = torch.randperm(self.num_samples)  # 8298  打乱顺序
        ret = []
        for i in indices:
            i = int(i)  # 第3367行
            _, i_pid, i_cam = self.data_source[i]  # relabel ?
            ret.append(i)  # [3367]
            pid_i = self.index_pid[i]  # pid_i = 182
            cams = self.pid_cam[pid_i]  # <class 'list'>: [2, 2, 3, 4, 4, 4]
            index = self.pid_index[pid_i]  # <class 'list'>: [3363, 3364, 3365, 3366, 3367, 3368]
            if len(set(cams)) == 1:  # 只有1个cam
                if len(index) == 1:  # 只有1个cam并且只有一个tracklet
                    select_camind = 0
                else:
                    select_cams = No_index(index, i)
                    select_camind = np.random.choice(select_cams)
            else:
                select_cams = No_index(cams, i_cam)
                try:
                    select_camind = np.random.choice(select_cams)
                except ValueError:
                    print(cams)
                    print(pid_i)
                    # print(i_label)
            select_ind = index[select_camind]
            ret.append(select_ind)

        return iter(ret)
