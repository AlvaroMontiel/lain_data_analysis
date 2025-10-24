import pandas as pd
from src.data_loader import DataLoader
from src.data_cleaner import FilterData
from src.data_cleaner import IntegerCleaner
from src.data_cleaner import DateCleaner
from src.data_cleaner import DuplicateCleaner

# -------------------------------------------------------------
# Data Loading
# Cargar datos desde un archivo Excel
# -------------------------------------------------------------
ruta_excel = "data/reporte_formularios_251024_1216.xlsx"
hoja_excel = "reporte_formularios_251024_1216"

loader = DataLoader(file_path=ruta_excel, sheet_name=hoja_excel)
df_raw = loader.load_data()

print(f"Comenzando el proceso de filtrado y limpieza de datos \n")
print(f"Etapa 1: Filtrado de datos \n")

    # Etapa 1: Filtrar datos
clean_data = FilterData(df_raw)
df_clean = clean_data.get_filter_data()    

print(f"Etapa 2: Limpieza de las columnas de fecha \n")
# Etapa 2: Limpiar columnas de fecha
clean_data = DateCleaner(df_clean)
df_clean = clean_data.get_clean_date()
    
print(f"Etapa 3: Limpieza de columnas numericas y de ID \n")
# Etapa 3: Limpiar columnas numéricas y de identificación
clean_data = IntegerCleaner(df_clean)
df_clean = clean_data.get_clean_integer()
    
print(f"Etapa 4: Eliminacion de duplicados \n")
# Etapa 4: Eliminar duplicados y ajustes finales
clean_data = DuplicateCleaner(df_clean)
df_clean = clean_data.get_clean_duplicates()

df_clean.to_excel("data/set_datos_lain_para_analisis.xlsx")

