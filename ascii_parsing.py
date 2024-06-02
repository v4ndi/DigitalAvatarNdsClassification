import os
from glob import glob
from tqdm import tqdm

import pandas as pd
import wfdb.io.convert


name_channel = '_o2-m1'
PATH = "D:\\digital_avatar\\train_dataset_nmic_train123"
EXT = "*.ascii"
all_ascii_files = [file
                 for path, subdir, files in os.walk(PATH)
                 for file in glob(os.path.join(path, EXT))]

final_df = []
import numpy as np
import pickle


for file in tqdm(all_ascii_files):
    user = file.split('\\')[-3]
    exp = file.split('\\')[-2]

    #values = np.fromfile(file)

    file = open(file, "r")
    lines = file.readlines()

    values = []
    for line in lines:
        cur_value = int(line)
        values.append(cur_value)

    final_df.append({'user': user, 'exp': exp, 'type': name_channel, 'values': values})

    with open(f'dataset{name_channel}_{user}_{exp}.pkl', 'wb') as f:
        pickle.dump(final_df, f)

    final_df = []

print('Success')




