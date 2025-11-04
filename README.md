# toxic-content

## files

* dataset.json: original data
* dataset-parser.py: transform dataset to binary. how to determine whether toxic or normal? marjority wins. if 3 labels, 2 says toxic, 1 normal, then it's toxic.
* hatexplain_detailed: output from dataset-to-binary-parser.py

## command
```python3 dataset-parser.py```

```
=== Summary Statistics ===
Majority-win Toxic:  12,334
Majority-win Normal: 7,814
Pure Toxic:          8,637
Pure Normal:         5,124
```
