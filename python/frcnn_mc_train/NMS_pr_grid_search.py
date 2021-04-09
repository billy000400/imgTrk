### imports starts
import sys
from pathlib import Path
import pickle
import cv2

import pandas as pd
import numpy as np

import tensorflow as tf
from tensorflow.image import non_max_suppression_with_scores

util_dir = Path.cwd().parent.joinpath('Utility')
sys.path.insert(1, str(util_dir))
from Configuration import frcnn_config
from Abstract import make_anchors, normalize_anchor, propose_score_bbox_list
from Layers import rpn
from Information import *

from NMS_pr_analysis import region_proposal_analysis
### imports end

pbanner()
psystem('Faster R-CNN Object Detection System')
pmode('Testing')

cwd = Path.cwd()
pickle_path = cwd.joinpath('frcnn.train.config.pickle')
C = pickle.load(open(pickle_path,'rb'))

max_output_size = 10
ITs = [0.7]
STs = [0.911, 0.912, 0.913, 0.914, 0.915, 0.916, 0.917, 0.918, 0.919]
#STs = list(np.round(np.arange(0.99,0.998,0.001,dtype=np.float32),3))
# Sigmas = np.linspace(0,1,11).tolist()
Sigmas = [1e2]
IoU_cuts = [0.5]


data_dir = C.sub_data_dir
csv_file = data_dir.joinpath("mc_NMS_grid_search_10_ST_[0.91,0.92].csv")

df = pd.DataFrame(columns=["IoU_threshold", "Score_threshold", "Sigma", "Precision", "Recall", "Degeneracy", "mAP@.75", "mAP@.5", "mAP@[.5,.95]"])

prNum = len(ITs)*len(STs)*len(Sigmas)
prIdx = 0
for IT in ITs:
    for ST in STs:
        for Sigma in Sigmas:
            pinfo(f"Evaluating parameter set: {prIdx+1}/{prNum}")
            prIdx += 1
            tmp = {}
            tmp["IoU_threshold"] = IT
            tmp["Score_threshold"] = ST
            tmp["Sigma"] = Sigma
            df_tmp = region_proposal_analysis(C, max_output_size, IT, ST, Sigma, IoU_cuts=IoU_cuts)
            tmp["Precision"] = df_tmp.loc[0,0.5]
            tmp["Recall"] = df_tmp.loc[1,0.5]
            tmp["Degeneracy"] = df_tmp.loc[2,0.5]
            tmp['mAP@.75'] = df_tmp.loc[3,0.5]
            tmp['mAP@.5'] = df_tmp.loc[4,0.5]
            tmp['mAP@[.5,.95]'] = df_tmp.loc[5,0.5]
            df = df.append(tmp, ignore_index=True)
            df.to_csv(csv_file, index=False)

# don't use pinfo, because you cannot concatenate string with a dataframe
print(df)
