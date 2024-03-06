#!/bin/bash

toProcess="/mnt/vsi-db/Code/DACHS/"
monitorFiles="AutoMOFs05_[MLTH]???.xlsx"

cd $toProcess

for f in `find "$toProcess" -maxdepth 3 -name "$monitorFiles" -type f`
do
        echo "$f" # >> ~/raw.log 2&>1
        PYTHONPATH=src python -m dachs -l tests/testData/AutoMOFs_Logbook_Testing.xlsx -s0 tests/testData/AutoMOFs05_Solution0.xlsx -s1 tests/testData/AutoMOFs05_Solution1.xlsx -s "$f" -a AMSET_5
        # groupNum=`echo "$f" | awk '{split($0,a,"_"); print a[2]}'`
        # python3 processingCode/datamerge/main.py -f "$f" -C "$toProcess/mergeConfig.yaml" -o "$toProcess/merged-$groupNum.nxs" -g "20*.nxs"
        # python3 processingCode/datamerge/main.py -f "$f" -C "$toProcess/mergeConfig.yaml" -o "$toProcess/automatic.nxs" -g "20*.nxs"
        # python3 processingCode/scicatMergedDataUpload.py -f "$toProcess/merged-$groupNum.nxs"
done

