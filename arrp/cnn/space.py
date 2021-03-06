from gaussian_process import Space

space = Space({
    "convolutionals":[{
        "Conv1D_kwargs":{
            "filters":(16,32,64,128),
            "kernel_size":(3,5,8,10,16),
            "activation":"relu",
        },
        "MaxPooling1D_kwargs":{
            "pool_size":(2,)
        },
        "layers":[1,3]
    },
    {
        "Conv1D_kwargs":{
            "filters":(16,32,64,128),
            "kernel_size":(3,5,8,10,16),
            "activation":"relu",
        },
        "MaxPooling1D_kwargs":{
            "pool_size":(2,)
        },
        "layers":[1,3]
    }],
    "dense":[{
        "layers":2,
        "units":32,
        "activation":"relu"
    },
    {
        "layers":2,
        "units":16,
        "activation":"relu"
    }]
})