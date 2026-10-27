from pathlib import Path

import pandas as pd

DATASET = Path('data/raw/nevworld_708139750131559771_20261005_183106.jsonl')
OUTPUT_DIR = Path('data/processed')
OUTPUT_DIR.mkdir(parents = True, exist_ok = True)
if not DATASET.exists():
    raise FileNotFoundError(f'No se encuentra: ', {DATASET.resolve()})

df = pd.read_json(DATASET, lines = True)


def event_table(event_type, columns):
    selected = [
        'run_id',
        'event_index',
        'tick',
        *columns
        ]
    
    available = [
        column for column in selected 
        if column in df.columns
    ]
    
    table = df.loc[
        df['type'] == event_type,
        available,
    ].copy()
    
    table = table.reindex(columns = selected)

    if not table.empty:
        table['simulation_day'] = table['tick'] // 12000
    
    return table


tables = event_table('hunt_completed', ['villager_id', 'prey_type'])


def verificar(df, tables):
    # Comprobamos que coinciden el total de eventos en el RAW con el CSV de salida.
    lines = (df['type'] == 'hunt_completed').sum()
    assert lines == len(tables)
    
    # Comprobamos que no se repitan la combinación de run_id con event_index
    assert not tables.duplicated(['run_id','event_index']).any() , 'Hay eventos duplicados'
    
    # Comprobamos que no estén vacios los campos de run_id, event_index, tick, villager_id y prey_id
    required_columns = ['run_id', 'event_index', 'tick', 'villager_id', 'prey_type']
    assert tables[required_columns].notna().all().all()
    
    # Que la división sea correcta respecto al tick
    assert (tables['simulation_day'] == tables['tick'] // 12000 ).all(), 'El calculo de los días es incorrecto'
    

def generar_csv(tables):

    output = OUTPUT_DIR / f'hunts.csv'
    tables.to_csv(output, index = False)
    print('hunts  -> ', len(tables))
    print(output)
        

verificar(df, tables)
generar_csv(tables)
