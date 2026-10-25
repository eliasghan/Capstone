# Datasheets

One datasheet per function, completed from the Module 25 template. Each records that function's scenario, data structure, noise behaviour, the optimisation strategy used and why it changed, preprocessing, what each week taught, the final result, and the pitfalls a future user should know about.

| | Function | Dim | Scenario | Best found |
|---|---|---|---|---|
| [Function 1](data_sheet_function_1.md) | Contamination source detection | 2-D | Detecting likely contamination sources in a two-dimensional area, such as a radiation field, where only proximity to a source yields a non-zero reading. | **1.05167e-04** |
| [Function 2](data_sheet_function_2.md) | Noisy log-likelihood of a mystery model | 2-D | A black-box machine-learning model that takes two numbers and returns a log-likelihood score. | **0.689468** |
| [Function 3](data_sheet_function_3.md) | Drug discovery - adverse reactions from three compounds | 3-D | A drug discovery project testing combinations of three compounds. | **-0.0252350** |
| [Function 4](data_sheet_function_4.md) | Warehouse placement surrogate - four hyperparameters | 4-D | An ML model that approximates an expensive warehouse product-placement calculation. | **0.6027542** |
| [Function 5](data_sheet_function_5.md) | Chemical process yield - four variables | 4-D | The yield of a chemical process in a factory, controlled by four variables. | **8662.405** |
| [Function 6](data_sheet_function_6.md) | Cake recipe - five ingredients | 5-D | Optimising a cake recipe with five ingredient quantities - for example flour, sugar, eggs, butter and milk. | **-0.2497464** |
| [Function 7](data_sheet_function_7.md) | ML model with six hyperparameters | 6-D | Tuning a machine-learning model through six hyperparameters - for example learning rate, regularisation strength or number of hidden layers. | **2.748654** |
| [Function 8](data_sheet_function_8.md) | High-dimensional model tuning - eight parameters | 8-D | An eight-dimensional black box in which every input affects the output and the internals are unknown - framed as tuning a model with eight hyperparameters and reading back a validation score. | **9.974458** |

A dataset-level datasheet covering the collection process, sampling bias and intended uses across all eight functions is in [`dataset_overview.md`](dataset_overview.md).
