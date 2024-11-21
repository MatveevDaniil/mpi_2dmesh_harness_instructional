import itertools
import pandas as pd
import matplotlib.pyplot as plt


def calc_sent_messages(pnum: int) -> int:
  # we send pnum - 1 messages from rank 0 to all other ranks in the scatter phase
  # we send pnum - 1 messages from all other ranks to rank 0 in the gather phase
  return 2 * (pnum - 1)

def calc_moved_data(pnum: int, x: int, y: int, g: int) -> tuple[int]:
  cell_count = 0
  max_count = 0
  if g == 1:
    y_step = y // pnum
    y_loc = [y_step * i for i in range(pnum + 1)]
    y_loc[-1] = y
    for h in range(2, pnum + 1):
      ghost_ymin = 0 if h == 1 else 1
      ghost_ymax = 0 if h == pnum else 1
      ysize = y_loc[h] - y_loc[h - 1]
      tile_data_move = x * (2 * ysize + ghost_ymin + ghost_ymax)
      cell_count += tile_data_move
      max_count = max(max_count, tile_data_move)
  elif g == 2:
    x_step = x // pnum
    x_loc = [x_step * i for i in range(pnum + 1)]
    x_loc[-1] = x
    for w in range(2, pnum + 1):
      ghost_xmin = 0 if w == 1 else 1
      ghost_xmax = 0 if w == pnum else 1
      xsize = x_loc[w] - x_loc[w - 1]
      tile_data_move = y * (2 * xsize + ghost_xmin + ghost_xmax)
      cell_count += tile_data_move
      max_count = max(max_count, tile_data_move)
  elif g == 3:
    groot = round(pnum ** 0.5)
    x_step = x // groot
    y_step = y // groot
    x_loc = [x_step * i for i in range(groot + 1)]
    x_loc[-1] = x
    y_loc = [y_step * i for i in range(groot + 1)]
    y_loc[-1] = y
    for wi, hi in itertools.product(range(1, groot + 1), repeat=2):
      if wi == hi == 1:
        continue
      ghost_xmin = 0 if wi == 1 else 1
      ghost_xmax = 0 if wi == groot else 1
      ghost_ymin = 0 if hi == 1 else 1
      ghost_ymax = 0 if hi == groot else 1
      xsize = x_loc[wi] - x_loc[wi - 1]
      ysize = y_loc[hi] - y_loc[hi - 1]
      xsize_ghosted = xsize + ghost_xmin + ghost_xmax
      ysize_ghosted = ysize + ghost_ymin + ghost_ymax
      tile_data_move = xsize_ghosted * ysize_ghosted + xsize * ysize
      cell_count += tile_data_move
      max_count = max(max_count, tile_data_move)
  return cell_count * 4, max_count


G = (1, 2, 3)
G2LABEL = {
  1: 'Row Tiling',
  2: 'Column Tiling',
  3: 'Block Tiling'
}
PNUM = (4, 9, 16, 25, 36, 49, 64, 81)
X, Y = 7112, 5146


def analyze_tiling_size():
  max_cnt_dict = {1: {}, 2: {}, 3: {}}
  for g in G:
    for pnum in PNUM:
      _, max_cnt_dict[g][pnum] = calc_moved_data(pnum, X, Y, g)

  for g, values in max_cnt_dict.items():
      x = list(values.keys())
      y = list(values.values())
      plt.plot(x, y, marker='o', label=G2LABEL[g])

  plt.xlabel('Number of Processes')
  plt.ylabel('Maximal Tile Size')
  plt.title('Maximal Tile Size vs Number of Processes for Different Groups')
  plt.legend()
  plt.grid(True)
  plt.tight_layout()
  plt.savefig('scripts/max_count_vs_pnum.png', dpi=300)
  plt.close()

analyze_tiling_size()

def analyze_messages_moved_data():
  moved_data = {g: [calc_moved_data(pnum, X, Y, g)[0] / 10 ** 6 for pnum in PNUM] for g in G}
  data = {
    'Concurrency Level': PNUM,
    'Number of Messages': [calc_sent_messages(pnum) for pnum in PNUM],
    'Row-Slab': [f'{moved_data[1][i]:.2f}' for i, pnum in enumerate(PNUM)],
    'Column-Slab': [f'{moved_data[2][i]:.2f}' for i, pnum in enumerate(PNUM)],
    'Block': [f'{moved_data[3][i]:.2f}' for i, pnum in enumerate(PNUM)]
  }

  df = pd.DataFrame(data)

  with open('scripts/messages_moved_data.tex', 'w') as f:
    f.write(df.to_latex(index=False))

analyze_messages_moved_data()