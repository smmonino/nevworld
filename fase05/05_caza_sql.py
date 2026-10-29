from pathlib import Path
import pandas as pd
import duckdb

DATA_DIR = Path('data/processed')
hunts_csv = Path(DATA_DIR / 'hunts.csv')



if not hunts_csv.exists():
    raise FileNotFoundError("No existe el fichero \'hunts.csv\'")
else:
    hunts_table = pd.read_csv(hunts_csv)
    assert not hunts_table.empty, "No hay registros para \'hunts.csv\'"
    assert 'prey_type' in hunts_table.columns, "No se encuentra el campo \'prey_type\' en \'hunts.csv\'"
    assert hunts_table[['prey_type']].notna().all().all(), "Existen valores nulos en \'prey_type\'"
    
    PARQUET_DIR = DATA_DIR / 'parquet'
    PARQUET_DIR.mkdir(exist_ok = True)
    
    parquet_path = PARQUET_DIR / 'hunts.parquet'
    hunts_table.to_parquet(parquet_path, engine = 'pyarrow', index = False)
    
    print('Tamaño CSV: ', hunts_csv.stat().st_size, 'bytes')
    print('Tamaño PARQUET: ', parquet_path.stat().st_size, 'bytes')
    
    connection = duckdb.connect()
    hunt_query = """
        SELECT
            prey_type,
            COUNT (*) AS hunt_count,
        FROM read_parquet('data/processed/parquet/hunts.parquet')
        GROUP BY prey_type
        ORDER BY prey_type DESC
    """
    hunts_summary = connection.execute(
        hunt_query
    ).fetchdf()
    print(hunts_summary)
    
    print('summary sql', hunts_summary)
    
    assert hunts_summary['hunt_count'].sum() == len(hunts_table), 'El total no coincide de la consulta con el fichero'
    
    recuento_tabla = hunts_table['prey_type'].value_counts().sort_index()
    recuento_sql = hunts_summary.set_index('prey_type')['hunt_count'].sort_index()
    print('recuento tabla', recuento_tabla, 'recuento sql',recuento_sql)
    print(f"El recuento {'SÍ' if recuento_tabla.equals(recuento_sql) else 'NO'} coincide")
    
    hunts_summary.to_csv(
        'reports/hunts_by_prey_sql.csv',
        index = False
    )
    
    connection.close()
    
    
    
# if hunts_table.empty:
#     print(f'El archivo \'hunts.csv\' está vacío')
# else:
#     assert 'prey_type' in hunts_table.columns, 'No existe la columna \'prey_type\''
#     assert hunts_table[['prey_type']].notna().all().all(), 'Existen valores nulos para el campo prey_type'
    
#     PARQUET_DIR = DATA_DIR / 'parquet'
#     PARQUET_DIR.mkdir(exist_ok = True)
    
#     parquet_path = PARQUET_DIR / 'hunts.parquet'
#     hunts_table.to_parquet(parquet_path, engine = 'pyarrow', index = False)
    
#     print('hunts.csv')
#     print(' CSV: ', hunts_csv.stat().st_size, 'bytes')
#     print(' Parquet: ', parquet_path.stat().st_size, 'bytes')
    
#     connection = duckdb.connect()
    
#     hunt_query = """
#         SELECT
#             COUNT(*) AS hunt_count,
#         FROM read_parquet('data/processed/parquet/hunts.parquet'),
#         GROUP BY prey_type,
#         ORDER BY prey_type DESC
#     """
    
#     hunts_summary = connection.execute(
#         hunt_query
#     ).fetchdf()
#     print(hunts_summary)
    
#     assert hunts_summary['hunt_count'].sum() == len(hunts_table)
    
#     expected = hunts_table['prey_type'].value_counts()
#     actual = hunts_summary.set_index('prey_type')['hunt_count']
    
    
    