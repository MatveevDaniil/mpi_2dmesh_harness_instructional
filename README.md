## Sobel operation with MPI

### Description

This study assessed the efficiency of the 2D Sobel operation used for edge detection in the images, using an MPI based parallelization method by implementing three tiling techniques: row, column, and block. 
We implemented all algorithms in C++ language and measured several performance metrics: speedup, data movement among ranks, and distribution of tile sizes. 
We have shown that the row tiling demonstrates the maximum overall speedup even with low kernel performance because of the fast gather and scatter phases while the block tiling is highly efficient in the kernel performance but is limited in the data movement stages. 
These results highlight the importance of the critical memory access patterns towards improving the parallel implementations such as blocking and row strategies.

# Installation and testing

To download and compile this project use:

```
git clone https://github.com/MatveevDaniil/mpi_2dmesh_harness_instructional.git
cd mpi_2dmesh_harness_instructional
mkdir build; cd build; cmake ..; make
```

To repeat the results in Perlmutter:

```
module load cpu
salloc --nodes 4 --qos interactive --time 00:30:00 --constraint cpu --account m3930
bash ../scripts/run_script.sh ./mpi_2dmesh > results_out
```

To plot the output image:

```
python scripts/imshow.py ./data/zebra-gray-int8-4x 7112 5146
```

To plot the charts/tables with performance metrics :

```
python scripts/parse_res_plot_speedup.py
python scripts/calc_messages.py
```