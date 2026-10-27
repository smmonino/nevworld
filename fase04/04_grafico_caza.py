from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

DATA_DIR = Path('data/processed')
CHARTS_DIR = Path('reports/charts')
CHARTS_DIR.mkdir(parents = True, exist_ok = True)

assert (DATA_DIR / 'hunts.csv').exists(), 'No existe hunts.csv'

hunts = pd.read_csv(DATA_DIR / 'hunts.csv')

assert 'prey_type' in hunts.columns, "Falta la columna \'prey_type\' en hunts.csv"
assert hunts['prey_type'].notna().all(), 'Hay cacerías sin tipo de presa'

if hunts.empty:
    print('No hay cacerías completadas.')
else:
    hunts_counts = hunts['prey_type'].value_counts()

    plt.figure(figsize=(8, 4))
    hunts_counts.plot.bar(color = ['steelblue','darkorange'])
    plt.title('Tipos de presa con cacerías completadas')
    plt.xlabel('Tipo de presa')
    plt.ylabel('Total de cacerías completadas')

    plt.xticks(rotation = 30, ha = 'right')
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '05_hunts_by_prey.png')
    plt.close()
    
    assert hunts_counts.sum() == len(hunts)
    
    print('Recuento por presa:')
    print(hunts_counts)
    print('Total de cacerías:', len(hunts))
    print('Gráfico guardado en:', CHARTS_DIR / '05_hunts_by_prey.png')