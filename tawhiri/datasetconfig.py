from functools import reduce


# lat lon  [1] treated as int and in the end used * scaler[2]
defaultConfig = [
    [65, 0, 3],
    [47, 0, 1],
    [3, 0, 1],
    [361, 2*(-90), 0.5], 
    [720, 2*0, 0.5]
];

dlShortConfig = [
    [5, 0, 3],          # data is available abt 6h after run, then use T+6,T+9,T+12 (3 data filtes) ##now T0 T3... (5 files)
    [47, 0, 1],
    [3, 0, 1],
    [41, 2*40, 0.5],     # [40N..60N]
    [40, 2*0, 0.5],      # [0E..20E)
]

config = dlShortConfig
shape = tuple(map(lambda x: x[0], config))

print("shape is ",shape)
print("mmap file size is ", reduce(lambda x,y: x*y, shape, 1)*4)
