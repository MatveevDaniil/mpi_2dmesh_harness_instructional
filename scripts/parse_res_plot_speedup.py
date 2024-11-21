import re
import matplotlib.pyplot as plt

def parse_results(output: str) -> tuple[dict[int, dict[int, float]]]:
  pattern = re.compile(r'srun -n (\d+) ./mpi_2dmesh -i (.+) -x (\d+) -y (\d+) -g (\d+)\s+'
                        r'Timing results from rank 0:\s+'
                        r'Scatter time:\s+([\d.]+) \(ms\)\s+'
                        r'Sobel time:\s+([\d.]+) \(ms\)\s+'
                        r'Gather time:\s+([\d.]+) \(ms\)')
      
  output = '\n'.join(line for line in output.split('\n') if not line.startswith('srun:'))
  matches = pattern.findall(output)
  scatter2time = {1: {}, 2: {}, 3: {}}
  sobel2time = {1: {}, 2: {}, 3: {}}
  gather2time = {1: {}, 2: {}, 3: {}}
  for match in matches:
    n = int(match[0])
    g = int(match[4])
    scatter_time = float(match[5])
    sobel_time = float(match[6])
    gather_time = float(match[7])
    scatter2time[g][n] = scatter_time
    sobel2time[g][n] = sobel_time
    gather2time[g][n] = gather_time
  return scatter2time, sobel2time, gather2time

raw_results = open('results_out').read()
def calc_speedup(result_dict):
  speedup = {}
  for g in result_dict:
    speedup[g] = {}
    for n in result_dict[g]:
      speedup[g][n] = result_dict[g][4] / result_dict[g][n]
  return speedup

scatter2time, sobel2time, gather2time = parse_results(raw_results)
scatter_speedup = calc_speedup(scatter2time)
sobel_speedup = calc_speedup(sobel2time)
gather_speedup = calc_speedup(gather2time)
overal_speedup = {}
for g in (1, 2, 3):
  overal_speedup[g] = {}
  for n in scatter2time[g]:
    overal_speedup[g][n] = scatter2time[g][n] + sobel2time[g][n] + gather2time[g][n]
  overal_speedup_4 = overal_speedup[g][4]
  for n in overal_speedup[g]:
    overal_speedup[g][n] = overal_speedup_4 / overal_speedup[g][n]
idx2label = {
  1: 'Row Tiling',
  2: 'Collumn Tiling',
  3: 'Block Tiling'
}

def plot_speedup(speedup: dict[int, dict[int, float]], title: str):
  for g in speedup:
    plt.plot(speedup[g].keys(), speedup[g].values(), label=idx2label[g])
    plt.scatter(speedup[g].keys(), speedup[g].values())
  plt.xlabel('Number of Processes')
  plt.ylabel('Speedup')
  plt.title(title)
  plt.legend()
  plt.tight_layout()
  plt.savefig(f'scripts/{title}.png', dpi=300)
  plt.close()



plot_speedup(scatter_speedup, 'Scatter Phase Speedup')
plot_speedup(sobel_speedup, 'Sobel Kernel Speedup')
plot_speedup(gather_speedup, 'Gather Phase Speedup')
plot_speedup(overal_speedup, 'Overall Speedup')