import torch
import torchani
import torchani.data
import tqdm
import math
import timeit

import configs
configs.benchmark = True
from common import *

ds = torchani.data.load_dataset(configs.data_path)
sampler = torchani.data.BatchSampler(ds, 256, 4)
dataloader = torch.utils.data.DataLoader(ds, batch_sampler=sampler, collate_fn=torchani.data.collate, num_workers=20)

optimizer = torch.optim.Adam(model.parameters(), amsgrad=True)

def optimize_step(a):
    mse = a.avg()
    optimizer.zero_grad()
    mse.backward()
    optimizer.step()

start = timeit.default_timer()
for batch in tqdm.tqdm(dataloader, total=len(sampler)):
    a = Averager()
    for molecule_id in batch:
        _species = ds.species[molecule_id]
        coordinates, energies = batch[molecule_id]
        coordinates = coordinates.to(aev_computer.device)
        energies = energies.to(aev_computer.device)
        a.add(*evaluate(coordinates, energies, _species))
    optimize_step(a)

elapsed = round(timeit.default_timer() - start, 2)
print('Epoch time:', elapsed)
print('Radial terms:', aev_computer.timers['radial terms'])
print('Angular terms:', aev_computer.timers['angular terms'])
print('Terms and indices:', aev_computer.timers['terms and indices'])
print('Partition:', aev_computer.timers['partition'])
print('Assemble:', aev_computer.timers['assemble'])
print('Total AEV:', aev_computer.timers['total'])
print('NN:', model.timers['nn'])
print('Total Forward:', model.timers['forward'])