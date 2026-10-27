from pathlib import Path
import pandas as pd

DATA_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
REPORTS_DIR.mkdir(parents=True, exist_ok = True)

if not REPORTS_DIR.exists:
    raise FileNotFoundError('No se encuentra ', {REPORTS_DIR.resolve()})
assert (DATA_DIR / 'resources.csv'), 'El archivo resources.csv no existe'
assert (DATA_DIR / 'hunts.csv').exists(), 'El archivo hunts.csv no existe'


resources = pd.read_csv(DATA_DIR / 'resources.csv')
hunts = pd.read_csv(DATA_DIR / 'hunts.csv')


required_columns = [
    'run_id', 'event_index', 'tick'
]
hunt_columns = required_columns + ['villager_id', 'prey_type', 'simulation_day']
resource_columns = required_columns + ['resource_type', 'amount_delta']

for column in hunt_columns:
    assert column in hunts.columns, (f'Falta la columna {column} en hunts.csv')
for  column in resource_columns:
    assert column in resources.columns, (f'Falta la columna {column} en resources.csv')

assert not hunts.duplicated(['run_id', 'event_index']).any(), 'Hay eventos duplicados en hunts.csv'
assert not resources.duplicated(['run_id', 'event_index']).any(), 'Hay eventos duplicados en resources.csv'

if hunts.empty:
    print('No hay cacerías completadas registradas.')
else:
    
    hunts_completed = len(hunts)
    print('Total cazas completadas registradas: ', hunts_completed)
    
    prey_counts = hunts['prey_type'].value_counts()
    print('\nTOTAL POR PRESA: ')
    print(prey_counts)
    
    prey_percent_raw = hunts['prey_type'].value_counts(normalize = True) * 100
    prey_percent = prey_percent_raw.round(1)
    print('\nPORCENTAES DE CACERÍAS POR PRESA: ')
    print(prey_percent)
    
    daily_counts = hunts['simulation_day'].value_counts().sort_index()
    print('\nCACERÍAS POR DÍA: ')
    print(daily_counts)
    
    assert prey_counts.sum() == hunts_completed
    assert daily_counts.sum() == hunts_completed
    
    
    
    gains = resources[resources['amount_delta'] > 0]
    spending = resources[resources['amount_delta'] < 0].copy()
    food_gains =gains['amount_delta'].sum()
    food_reductions = spending['amount_delta'].abs().sum()
    
    print('\nINCREMENTOS REGISTRADOS:')
    print(gains.groupby('resource_type')['amount_delta'].sum())
    
    print('\nREDUCCIONES REGISTRADAS')
    print(spending.groupby('resource_type')['amount_delta'].sum())
    
    food = resources[resources['resource_type'] == 'food']
    food_net = food['amount_delta'].sum()
    print('\nBALANCE NETO DE COMIDA')
    print(food_net)
    
    assert abs(
        (food_gains - food_reductions) - food_net
    ) < 0.000001, 'El balance neto de comida no coincide'
    
    summary = pd.DataFrame([
    {'metric': 'hunt_events', 'value': hunts_completed},
    {'metric': 'food_change_events', 'value': len(food)},
    {'metric': 'food_gains', 'value': food_gains},
    {'metric': 'food_reductions', 'value': food_reductions},
    {'metric': 'food_net_change', 'value': food_net},
    ])
    

    summary.to_csv(REPORTS_DIR / 'hunting_summary.csv', index=False)

