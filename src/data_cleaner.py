"""
Módulo: data_cleaner
Responsabilidad: Limpiar y preprocesar los datos en un DataFrame de pandas.
"""

import pandas as pd
from typing import List, Optional, Union
from epiweeks import Week # type: ignore
from datetime import date


def parse_with_multiple_formats(date_str: str, possible_formats: list) -> pd.Timestamp:
    """
    Intenta convertir `date_str` a objeto datetime probando cada formato en `possible_formats`.
    Si ninguno funciona, devuelve pd.NaT.
    """
    for fmt in possible_formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            # Si falla el formato, pasa al siguiente
            pass

    # Si ningún formato encaja, devolvemos NaT
    return pd.NaT


class DataCleaner:
    """
    Clase para llevar a cabo tareas de limpieza en un DataFrame de pandas.

    Atributos:
        df (pd.DataFrame): El DataFrame que se está limpiando.
        selected_variables: Variables seleccionadas para el analisis
    """

    def __init__(self, df: pd.DataFrame):
        """
        Inicializa la clase con el DataFrame que se desea limpiar, las variables seleccionadas para el analisis.

        Args:
            df (pd.DataFrame): El DataFrame original que se va a limpiar.
        """
        # No copia internamente el DataFrame para manipularlo
        self.df = df
        self.selected_variables = [
            "Origen Caso",
            "Nr Folio",
            "Tipo de Caso",
            "Fecha Atencion Urgencia",
            "Semana Epidemiologica",
            "Estado",
            "Clasificacion",
            "Subclasificacion",
            "Region",
            "Comuna",
            "Establecimiento Salud",
            "Dependencia",
            "Identificacion Paciente",
            "ID/RUT Paciente",
            "Nombre Paciente",
            "Apellido Paterno Paciente",
            "Apellido Materno Paciente",
            "Sexo Paciente",
            "Fecha Nacimiento Paciente",
            "Edad Paciente",
            "Region Paciente",
            "Comuna Paciente",
            "Direccion Paciente",
            "Se considera pueblo originario",
            "Pueblo originario",
            "Se considera afrodescendiente",
            "Identidad de Genero",
            "Orientacion Sexual",
            "Nacionalidad Paciente",
            "Persona Bajo Cuidado",
            "Lesion fue Autoinfligida",
            "Lesion fue Intencional",
            "Tuvo intencion de Morir",
            "Tiene Antecedentes salud mental",
            "Antecedentes salud mental",
            "Tiene tratamiento salud mental",
            "Lugar tratamiento salud mental",
            "Paciente estudia actualmente",
            "Region de estudios",
            "Comuna de estudios",
            "Nombre establecimiento estudio",
            "Paciente trabaja actualmente",
            "Region de trabajo",
            "Comuna de trabajo",
            "Nombre lugar de trabajo",
            "Fecha del evento",
            "Tipo de Evento",
            "Metodo de Lesion",
            "Detalle metodo de Lesion",
            "Lugar del evento",
            "Detalle del lugar evento",
            "Factor Precipitante",
            "Derivacion",
            "Derivacion Region",
            "Derivacion Comuna",
            "Derivacion Establecimiento",
            "Derivacion detalle"
        ]

    def select_variables(self, selected_variables: List[str]) -> None:
        """
        Selecciona las variables ya predefinidas que se requieren en el analisis.

        Args:
            selected_variables (List[str]): Lista de variables a seleccionar en el dataframe.
        """
        self.df = self.df.loc[:, selected_variables]

    def primary_filter(self) -> None:
        """
        Seleccion de casos que van a entrar en el analisis estadistico

        Args:
            No recibe argumentos
        """
        self.df = self.df[
            (self.df['Origen Caso'].isin(['Notificación LAIN', 'Notificación física']))
            & (self.df['Tipo de Caso'] == 'Cerrado')
            & (self.df['Estado'] == 'Finalizado')
            & (self.df['Clasificacion'] == 'Confirmado LAIN')
            & (self.df['Subclasificacion'].isin(['Con intención suicida', 'Sin intención suicida']))
            & (self.df['Lesion fue Autoinfligida'] == 'Si')
            & (self.df['Lesion fue Intencional'] == 'Si')
            & (self.df['Tuvo intencion de Morir'].isin(['Si', 'No']))
        ]

    def drop_missing(self, how: str = "any", subset: Optional[List[str]] = None) -> None:
        """
        Elimina filas con valores nulos según el criterio especificado.

        Args:
            how (str): 'any' (default) para eliminar filas si al menos
                       un valor es nulo, o 'all' para eliminar filas
                       solo si todos los valores están nulos.
            subset (List[str] | None): Lista de columnas a considerar.
                                       Si es None, aplica a todas.

        Ejemplo:
            cleaner.drop_missing(how="all", subset=["edad_paciente", "sexo_paciente"])
        """
        self.df.dropna(how=how, subset=subset, inplace=True)

    def fill_missing(self, columns: List[str], value: Union[str, int, float]) -> None:
        """
        Rellena valores nulos en columnas específicas con un valor dado.

        Args:
            columns (List[str]): Lista de columnas donde se rellenarán nulos.
            value (str | int | float): Valor con el que se reemplazarán los nulos.

        Ejemplo:
            cleaner.fill_missing(["edad_paciente"], value=0)
        """
        for col in columns:
            self.df[col].fillna(value, inplace=True)

    def remove_outliers_iqr(self, column: str, factor: float = 1.5) -> None:
        """
        Elimina outliers en una columna numérica según el método de rango intercuartil (IQR).

        Args:
            column (str): Nombre de la columna donde se quieren eliminar outliers.
            factor (float): Factor para multiplicar el IQR.
                            1.5 es el valor tradicional,
                            aunque 3.0 se utiliza para detectar outliers más extremos.

        Ejemplo:
            cleaner.remove_outliers_iqr("edad_paciente", factor=1.5)
        """
        if column not in self.df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame.")

        q1 = self.df[column].quantile(0.25)
        q3 = self.df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - (factor * iqr)
        upper_bound = q3 + (factor * iqr)

        before_count = len(self.df)
        self.df = self.df[
            (self.df[column] >= lower_bound) &
            (self.df[column] <= upper_bound)
            ]
        after_count = len(self.df)
        print(f"Eliminados {before_count - after_count} outliers en '{column}' (IQR).")

    def remove_outliers_zscore(self, column: str, z_threshold: float = 3.0) -> None:
        """
        Elimina outliers en una columna numérica usando el método de puntaje Z (Z-score).

        Args:
            column (str): Nombre de la columna donde se quieren eliminar outliers.
            z_threshold (float): Umbral de Z-score. Por defecto 3.0 (3 desviaciones estándar).

        Ejemplo:
            cleaner.remove_outliers_zscore("edad_paciente", z_threshold=3.0)
        """
        if column not in self.df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame.")

        col_mean = self.df[column].mean()
        col_std = self.df[column].std()

        # Evitar división por cero si la desviación estándar es 0
        if col_std == 0:
            print(f"No se pueden detectar outliers con Z-score en '{column}' porque la desviación estándar es 0.")
            return

        before_count = len(self.df)
        z_scores = (self.df[column] - col_mean) / col_std
        self.df = self.df[abs(z_scores) <= z_threshold]
        after_count = len(self.df)
        print(f"Eliminados {before_count - after_count} outliers en '{column}' (Z-score).")

    def rename_columns(self, columns_mapping: dict) -> None:
        """
        Renombra columnas según un diccionario de mapeo.

        Args:
            columns_mapping (dict): {nombre_actual: nombre_nuevo}.

        Ejemplo:
            cleaner.rename_columns({"fecha_del_evento": "fecha_evento"})
        """
        self.df.rename(columns=columns_mapping, inplace=True)

    def drop_duplicates(self, subset: Optional[List[str]] = None, keep: str = "first") -> None:
        """
        Elimina filas duplicadas en función de un subconjunto de columnas.

        Args:
            subset (List[str] | None): Columnas a considerar para identificar duplicados.
            keep (str): Indica cuál duplicado mantener: 'first', 'last' o False para eliminar todos.

        Ejemplo:
            cleaner.drop_duplicates(subset=["id_paciente"])
        """
        before_count = len(self.df)
        self.df.drop_duplicates(subset=subset, keep=keep, inplace=True)
        after_count = len(self.df)
        print(f"Eliminados {before_count - after_count} duplicados.")

    def get_clean_data(self) -> pd.DataFrame:
        """
        Retorna el DataFrame limpio (procesado hasta el momento).

        Returns:
            pd.DataFrame: DataFrame ya limpio según las transformaciones aplicadas.
        """
        return self.df


class DateCleaner:
    """" 
    Clase para limpiar y preprocesar columnas de fechas en un DataFrame de pandas."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df
        self.variables_log = ['Nr Folio', 'ID/RUT Paciente', 'Comuna']

    def review_format(self) -> None:
        possible_formats = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]  # Define los formatos esperados

        # Conviertes la columna intentando cada formato
        self.df['Fecha Atencion Urgencia'] = self.df['Fecha Atencion Urgencia'].apply(
            lambda x: parse_with_multiple_formats(x, possible_formats) if pd.notnull(x) else pd.NaT
        )
        self.df.loc[self.df['Fecha Atencion Urgencia'].isnull(), self.variables_log].to_excel(
            "data/logs/fechas_imposibles_atencion_urgencia.xlsx"
        )

        self.df['Fecha del evento'] = self.df['Fecha del evento'].apply(
            lambda x: parse_with_multiple_formats(x, possible_formats) if pd.notnull(x) else pd.NaT
        )
        self.df.loc[self.df['Fecha del evento'].isnull(), self.variables_log].to_excel(
            "data/logs/fechas_imposibles_evento.xlsx"
        )

        self.df['Fecha Nacimiento Paciente'] = self.df['Fecha Nacimiento Paciente'].apply(
            lambda x: parse_with_multiple_formats(x, possible_formats) if pd.notnull(x) else pd.NaT
        )
        self.df.loc[self.df['Fecha Nacimiento Paciente'].isnull(), self.variables_log].to_excel(
            "data/logs/fechas_imposibles_nacimiento_paciente.xlsx"
        )

    def review_nat (self) -> None:
        """
        Método que se aplica inmediatamente después de date_adjust().
        Revisa valores NaT en:
          - Fecha Atencion Urgencia
          - Fecha del evento
          - Fecha Nacimiento Paciente
        e implementa la estrategia de imputación o descarte según la lógica definida.
        """

        # -------------------------------------------------------------
        # 1. Si 'Fecha Atencion Urgencia' es NaT pero 'Fecha del evento'
        #    sí existe, igualar una a la otra.
        # -------------------------------------------------------------
        mask_atencion_nat = self.df['Fecha Atencion Urgencia'].isnull() & self.df[
            'Fecha del evento'].notnull()
        if mask_atencion_nat.any():
            self.df.loc[mask_atencion_nat, 'Fecha Atencion Urgencia'] = self.df.loc[
                mask_atencion_nat, 'Fecha del evento']
            self.df.loc[mask_atencion_nat, self.variables_log].to_excel(
                'data/logs/log_fecha_atencion_urgencias_null.xlsx',
                sheet_name='Fecha Atencion Urgencia Imputada'
            )

        # -------------------------------------------------------------
        # 2. Revisar el porcentaje de NaT en 'Fecha Atencion Urgencia'.
        #    Si >= 10%, imputar con la mediana.
        # -------------------------------------------------------------
        mask_atencion_nat = self.df['Fecha Atencion Urgencia'].isnull()
        prop_na_atencion = self.df[
            'Fecha Atencion Urgencia'].isnull().mean()  # mean() da el porcentaje de True
        if prop_na_atencion >= 0.1:
            # Calcula la mediana de las fechas no nulas
            median_atencion = self.df['Fecha Atencion Urgencia'].median()
            self.df['Fecha Atencion Urgencia'].fillna(median_atencion, inplace=True)
            self.df.loc[mask_atencion_nat, self.variables_log].to_excel(
                'data/logs/log_fecha_atencion_urgencias_mediana.xlsx',
                sheet_name='Fecha Atencion Urgencia Imputada'
            )

        # -------------------------------------------------------------
        # 3. Si 'Fecha del evento' es NaT pero 'Fecha Atencion Urgencia'
        #    sí existe, igualar la primera a la segunda.
        # -------------------------------------------------------------
        mask_evento_nat = self.df['Fecha del evento'].isnull() & self.df['Fecha Atencion Urgencia'].notnull()
        if mask_evento_nat.any():
            self.df.loc[mask_evento_nat, 'Fecha del evento'] = self.df.loc[
                mask_evento_nat, 'Fecha Atencion Urgencia']
            self.df.loc[mask_evento_nat, self.variables_log].to_excel(
                'data/logs/log_fecha_evento_null.xlsx',
                sheet_name='Fecha Evento Imputada'
            )

        # -------------------------------------------------------------
        # 4. Si aún hay NaT en 'Fecha del evento', imputar la mediana.
        # -------------------------------------------------------------
        mask_evento_nat = self.df['Fecha del evento'].isnull()
        if mask_evento_nat.any():
            median_evento = self.df['Fecha del evento'].median()
            self.df['Fecha del evento'].fillna(median_evento, inplace=True)
            self.df.loc[mask_evento_nat, self.variables_log].to_excel(
                'data/logs/log_fecha_evento_mediana.xlsx',
                sheet_name='Fecha Evento Imputada'
            )

        # -------------------------------------------------------------
        # 5. Manejo de 'Fecha Nacimiento Paciente' cuando es NaT.
        #    - Inferirla a partir de la edad (si el paciente > 10 años).
        #    - Si luego de eso aún hay NaT, imputar la mediana si < 10%.
        #    - Caso extremo: si sigue >= 10% de NaT, eliminar filas.
        # -------------------------------------------------------------
        mask_nac_nat = self.df['Fecha Nacimiento Paciente'].isnull()
        if mask_nac_nat.any():
            # 5.1 Inferir a partir de la edad, SOLO si Edad > 10 y la Edad no es NaN
            if 'Edad Paciente' in self.df.columns:
                mask_puede_inferir = (
                        mask_nac_nat &
                        self.df['Edad Paciente'].notnull() &
                        (self.df['Edad Paciente'] > 10)
                )
                # Ejemplo simplificado: tomar la fecha del evento y restarle "X años"
                # para obtener un "aprox" de la fecha de nacimiento.
                # O podrías usar la fecha de urgencia. Tú decides la coherencia.
                # (Esto es muy simplificado; puede introducir cierta imprecisión)
                if mask_puede_inferir.any():
                    self.df.loc[mask_puede_inferir, 'Fecha Nacimiento Paciente'] = (
                            self.df.loc[mask_puede_inferir, 'Fecha del evento'] -
                            pd.to_timedelta(self.df.loc[mask_puede_inferir, 'Edad Paciente'] * 365, unit='D')
                    )
                    self.df.loc[mask_puede_inferir, self.variables_log].to_excel(
                        'data/logs/log_fecha_nacimiento_null.xlsx',
                        sheet_name='Fecha Nacimiento Imputada')

            # 5.2 Recalcular cuántos NaT quedan en 'Fecha Nacimiento Paciente'
            prop_na_nacimiento = self.df['Fecha Nacimiento Paciente'].isnull().mean()
            mask_nac_nat = self.df['Fecha Nacimiento Paciente'].isnull()

            if 0 < prop_na_nacimiento < 0.1:
                median_nac = self.df['Fecha Nacimiento Paciente'].median()
                self.df['Fecha Nacimiento Paciente'].fillna(median_nac, inplace=True)
                self.df.loc[mask_nac_nat, self.variables_log].to_excel(
                    'data/logs/log_fecha_nacimiento_mediana.xlsx',
                    sheet_name='Fecha Nacimiento Imputada'
                )
            elif prop_na_nacimiento >= 0.1:
                # Caso extremo: se decide eliminar
                self.df = self.df[self.df['Fecha Nacimiento Paciente'].notnull()]
                self.df.loc[mask_nac_nat, self.variables_log].to_excel(
                    'data/logs/log_fecha_nacimiento_eliminadas.xlsx',
                    sheet_name='Fecha Nacimiento Eliminada'
                )

    def review_coherence(self):
        """Se aplica posterior a review_nat"""
        incoherence_mask = self.df['Fecha del evento'].notnull() & (
            self.df['Fecha del evento'] > self.df['Fecha Atencion Urgencia']
        )
        if incoherence_mask.any():
            self.df.loc[incoherence_mask, 'Fecha Atencion Urgencia'] = (self.df.loc[incoherence_mask, 'Fecha del evento'])
            self.df.loc[incoherence_mask, self.variables_log].to_excel(
                'data/logs/incoherence_date_1.xlsx', sheet_name='Fechas imputadas'
            )

        incoherence_mask = self.df['Fecha Atencion Urgencia'].notnull() & (
                self.df['Fecha Atencion Urgencia'] < self.df['Fecha del evento']
        )
        if incoherence_mask.any():
            self.df.loc[incoherence_mask, 'Fecha del evento'] = (
                self.df.loc[incoherence_mask, 'Fecha Atencion Urgencia'])
            self.df.loc[incoherence_mask, self.variables_log].to_excel(
                'data/logs/incoherence_date_2.xlsx', sheet_name='Fechas imputadas'
            )


class IntegerCleaner:
    """
    A class for cleaning integer-based columns in a DataFrame, specifically designed for epidemiological data.
    This class provides methods to clean and process integer data fields, with specific
    functionality for handling epidemiological weeks and patient age data.
    Attributes:
        df (pd.DataFrame): The input DataFrame containing the data to be cleaned.
    Methods:
        semana_epidemiologica(): Processes and cleans epidemiological week data.
        edad_paciente(): Processes and cleans patient age data.
    Example:
        >>> df = pd.DataFrame(...)
        >>> cleaner = IntegerCleaner(df)
        >>> cleaner.semana_epidemiologica()
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    def semana_epidemiologica(self):
        """
        Calculate the epidemiological week for each record based on event date or emergency care date.
        The function performs the following operations:
        1. Calculates epidemiological week using 'Fecha del evento' (event date) if available
        2. For records without event date, uses 'Fecha Atencion Urgencia' (emergency care date)
        3. Handles missing values based on percentage of nulls:
            - If nulls < 10%: imputes with median and logs to Excel
            - If nulls >= 10%: removes rows and logs to Excel
        Notes:
            - Uses Week.fromdate() to calculate epidemiological week
            - Creates logs in 'data/logs/' directory
            - Modifies the dataframe in place
        Returns:
            None
        """
        
        week_mask = self.df['Fecha del evento'].notnull()
        week_mask = self.df['Fecha del evento'].notnull()
        if week_mask.any():
            # Calcula la semana epidemiológica usando Week.fromdate()
            self.df.loc[week_mask, 'Semana Epidemiologica'] = self.df.loc[week_mask, 'Fecha del evento'].apply(
                lambda x: Week.fromdate(x).week if isinstance(x, (date, pd.Timestamp)) else pd.NaT
            )

        mask_false = ~week_mask
        if mask_false.any():
            # Calcula la semana epidemiológica de los valores restantes
            self.df.loc[mask_false, 'Semana Epidemiologica'] = self.df.loc[mask_false, 'Fecha Atencion Urgencia'].apply(
                lambda x: Week.fromdate(x).week if isinstance(x, (date, pd.Timestamp)) else pd.NaT
            )
        
        mask_null = self.df['Semana Epidemiologica'].isnull()
        prop_na_sem_epidem = self.df['Semana Epidemiologica'].isnull().mean()
        if 0 < prop_na_sem_epidem < 0.1:
            # Imputar con la mediana
            median_semana = self.df['Semana Epidemiologica'].median()
            self.df['Semana Epidemiologica'].fillna(median_semana, inplace=True)
            self.df.loc[mask_null, 'Semana Epidemiologica'].to_excel(
                'data/logs/semana_epidemiologica_mediana.xlsx',
                sheet_name='Semana Epidemiologica Imputada'
            )
        elif prop_na_sem_epidem >= 0.1:
            # Eliminar filas con NaT
            self.df = self.df[self.df['Semana Epidemiologica'].notnull()]
            self.df.loc[mask_null, 'Semana Epidemiologica'].to_excel(
                'data/logs/semana_epidemiologica_eliminadas.xlsx',
                sheet_name='Semana Epidemiologica Eliminada'
            )

    def edad_paciente(self):
        """
        Calcula la edad en años a partir de la 'Fecha Nacimiento Paciente' y la 'Fecha del evento'.
        La edad se almacena en una nueva columna llamada 'Edad Calculada'.

        Lógica:
        - Si alguna de las dos fechas está vacía (NaT), la edad se mantendrá en NaN.
        - Se toman la diferencia en días y se divide entre 365 para obtener años aproximados.
        - Si la diferencia de días resultara negativa (evento antes de nacer), se marca NaN 
            (o se podrían descartar esos casos como registros inválidos).
        """

        # 1. Verificar que ambas columnas existan en el DataFrame
        if 'Fecha Nacimiento Paciente' not in self.df.columns or 'Fecha del evento' not in self.df.columns:
            print("No se encontraron las columnas requeridas para calcular la edad.")
            return
    
        # 2. Crear una máscara para las filas donde ambas fechas NO sean nulas
        mask_fechas_validas = (
            self.df['Fecha Nacimiento Paciente'].notnull() & 
            self.df['Fecha del evento'].notnull()
        )

        # 3. Calcular la diferencia en días (vectorizado) solo para las filas con fechas válidas
        #    Esto devuelve un objeto Timedelta.
        diferencia_dias = (
            self.df.loc[mask_fechas_validas, 'Fecha del evento'] -
            self.df.loc[mask_fechas_validas, 'Fecha Nacimiento Paciente']
        ).dt.days
        
        # 4. Convertir la diferencia de días a años (aprox), ignorando los valores negativos o inválidos
        #    Si quieres descartar los casos negativos, puedes marcar la edad como NaN o 0.
        #    Aquí, los marcamos como NaN para indicar inconsistencia.
        edad_approx = diferencia_dias.apply(
            lambda d: d // 365 if d is not None and d >= 0 else float('nan')
        )

        # 5. Asignar la columna "Edad Calculada" en el DataFrame
        #    Para filas que no cumplen la máscara, quedará en NaN por defecto.
        self.df['Edad Calculada'] = float('nan')  # Inicializa con NaN
        self.df.loc[mask_fechas_validas, 'Edad Calculada'] = edad_approx

        # 6. Calcular edades faltantes a partir de Fecha Atencion Urgencia
        mask_edades_faltantes = self.df['Edad Calculada'].isnull() & self.df[
            'Fecha Atencion Urgencia'].notnull()

        if mask_edades_faltantes.any():
            diferencia_dias = (
                self.df.loc[mask_edades_faltantes, 'Fecha Atencion Urgencia'] -
                self.df.loc[mask_edades_faltantes, 'Fecha Nacimiento Paciente']
            ).dt.days
            edad_approx = diferencia_dias.apply(
                lambda d: d // 365 if d is not None and d >= 0 else float('nan')
            )
            self.df.loc[mask_edades_faltantes, 'Edad Calculada'] = edad_approx

        # 7. Imputar la mediana de las edades faltantes si hay < 10% de datos faltantes
        prop_na_edad = self.df['Edad Calculada'].isnull().mean()
        mask_edad_null = self.df['Edad Calculada'].isnull()

        if 0 < prop_na_edad < 0.1:
            median_edad = self.df['Edad Calculada'].median()
            self.df['Edad Calculada'].fillna(median_edad, inplace=True)
            self.df.loc[mask_edad_null, 'Edad Calculada'].to_excel(
                'data/logs/edad_paciente_media.xlsx',
                sheet_name='Edad Paciente Imputada'
            )
        elif prop_na_edad >= 0.1:
            self.df = self.df[self.df['Edad Calculada'].notnull()]
            self.df.loc[mask_edad_null, 'Edad Calculada'].to_excel(
                'data/logs/edad_paciente_eliminadas.xlsx',
                sheet_name='Edad Paciente Eliminada'
            )
