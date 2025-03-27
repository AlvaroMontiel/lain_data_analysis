"""
Module: data_cleaner
Responsability: Clean and make a preprocess of data in a pandas DataFrame.
"""

import pandas as pd
from typing import List, Optional, Union
from epiweeks import Week # type: ignore
from datetime import date
from itertools import cycle
from fuzzywuzzy import fuzz
import streamlit as st


def parse_with_multiple_formats(date_str: str, possible_formats: list) -> pd.Timestamp:
    """
    Attempts to convert `date_str` to a datetime object by trying each format in `possible_formats`.
    If none work, returns pd.NaT.
    """
    for fmt in possible_formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except ValueError:
            # Si falla el formato, pasa al siguiente
            pass

    # Si ningún formato encaja, devolvemos NaT
    return pd.NaT

def digito_verificador(rut):
    """
    Calculates the verification digit of a Chilean RUT.
    Args:
        rut (int): The base number of the RUT.
    Returns:
        int: The calculated verification digit.
    """
    reversed_digits = map(int, reversed(str(rut)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    dv = (-s) % 11
    return 'K' if dv == 10 else 0 if dv == 11 else dv


class FilterData:
    """
    Class for performing cleaning tasks on a pandas DataFrame.

    The DataFrame (`df`) is expected to contain specific columns with the following structure:
        - 'Origen Caso' (str): Source of the case.
        - 'Nr Folio' (int): Case number.
        - 'Tipo de Caso' (str): Type of case.
        - 'Fecha Atencion Urgencia' (datetime): Date of emergency care.
        - 'Semana Epidemiologica' (int): Epidemiological week.
        - 'Estado' (str): Current state of the case.
        - 'Clasificacion' (str): Classification of the case.
        - 'Subclasificacion' (str): Subclassification of the case.
        - Additional columns as listed in `selected_variables`.

    Attributes:
        df (pd.DataFrame): The DataFrame being cleaned.
        selected_variables: Variables selected for analysis.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the class with the DataFrame to be cleaned and the variables selected for analysis.

        Args:
            df (pd.DataFrame): The original DataFrame to be cleaned.
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

    def filter_columns(self, selected_variables: List[str]) -> None:
        """
        Filters the predefined columns required for the analysis.

        Args:
            selected_variables (List[str]): Lista de columnas a filtrar en el DataFrame.
        """
        self.df = self.df.loc[:, selected_variables]

    def get_filter_data(self) -> None:
        """
        Selection of cases to be included in the statistical analysis.

        Args:
            None
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
 

class DateCleaner:
    """
    A class for cleaning and preprocessing date-related columns in a pandas DataFrame.
    This class provides methods to clean, validate, and ensure coherence of date information
    in a DataFrame, specifically handling three main date columns:
    The class implements various cleaning strategies including:
    - Date format standardization
    - Handling of NaT (Not a Time) values
    - Date coherence validation
    - Data imputation for missing values
    - Logging of modifications for accountability
    All modifications to the data are logged in Excel files stored in the data/logs directory.
        df (pd.DataFrame): The input DataFrame containing the date columns to be cleaned.
        variables_log (List[str]): List of variables to be included in log files when recording changes.
    Example:
        >>> df = pd.DataFrame({'Fecha Atencion Urgencia': ['2023-01-01', '2023/02/01'],
                              'Fecha del evento': ['2023-01-01', '2023-02-01'],
                              'Fecha Nacimiento Paciente': ['1990-01-01', '1991-01-01']})
        >>> cleaner = DateCleaner(df)
        >>> cleaned_df = cleaner.get_clean_date()
    Notes:
        - The class assumes the existence of specific date columns in the DataFrame
        - All cleaning operations are performed in-place on the DataFrame
        - Log files are created in the 'data/logs' directory for tracking changes
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initializes the class with the DataFrame to be cleaned.

        Args:
            df (pd.DataFrame): The original DataFrame to be cleaned.

        Attributes:
            variables_log (List[str]): List of variables to log in case of invalid dates.
        """
        self.df = df
        self.variables_log = ['Nr Folio', 'ID/RUT Paciente', 'Comuna']

    def review_format(self) -> None:
        """
        This method processes three date columns in the DataFrame:
        - 'Fecha Atencion Urgencia' (Emergency Care Date)
        - 'Fecha del evento' (Event Date)  
        - 'Fecha Nacimiento Paciente' (Patient Birth Date)
        For each column, it attempts to parse dates using multiple common formats.
        Invalid or unparseable dates are set to NaT (Not a Time).
        Records with unparseable dates are logged to separate Excel files in the data/logs directory.
        The following date formats are supported:
        - DD/MM/YYYY
        - DD-MM-YYYY 
        - YYYY-MM-DD
        Side Effects:
            - Modifies the date columns in the DataFrame in place
            - Creates Excel log files for records with invalid dates
        """
        
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
        Reviews and handles NaT (Not a Time) values in date columns through a series of steps:

            1. If 'Fecha Atencion Urgencia' is NaT but 'Fecha del evento' exists, equals them
            2. If 'Fecha Atencion Urgencia' has ≥10% NaT, imputes median value
            3. If 'Fecha del evento' is NaT but 'Fecha Atencion Urgencia' exists, equals them
            4. If any remaining NaT in 'Fecha del evento', imputes median value
            5. For 'Fecha Nacimiento Paciente' NaT values:
                - Infers from age if patient >10 years old
                - If <10% NaT remain, imputes median
                - If ≥10% NaT remain, removes those rows

        The method logs all changes to Excel files in data/logs/ directory.

        Notes:
            - Should be called immediately after date_adjust()
            - Modifies the dataframe in-place
            - Creates log files for tracking changes
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
        """
        Check and fix coherence of event dates in the DataFrame.
        After running review_nat(), this method ensures chronological consistency
        between 'Fecha del evento' (Event Date) and 'Fecha Atencion Urgencia' 
        (Emergency Care Date). It makes corrections when:
        1. Event Date is after Emergency Care Date:
           Updates Emergency Care Date to match Event Date
        2. Emergency Care Date is before Event Date:
           Updates Event Date to match Emergency Care Date
        When corrections are made, the affected records are logged to Excel files:
        - data/logs/incoherence_date_1.xlsx for first case
        - data/logs/incoherence_date_2.xlsx for second case
        """
        
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

    def get_clean_date(self) -> pd.DataFrame:
        """
        This method processes the DataFrame by applying sequential cleaning operations:
        1. Reviews format issues in dates
        2. Checks for NaT (Not a Time) values
        3. Verifies data coherence between dates

        The cleaned DataFrame with format corrections, NaT handling, and coherence checks applied.

        Returns:
            pd.DataFrame: The cleaned DataFrame after applying all date cleaning methods
        """

        # Aplicar metodos de limpieza de la clase
        self.review_format()
        self.review_nat()
        self.review_coherence()

        return self.df


class IntegerCleaner:
    """
    Class for cleaning integer-based columns in a DataFrame

    A class for cleaning integer-based columns in a DataFrame Specifically designed for epidemiological data.
    This class provides methods to clean and process integer data fields, with specific
    functionality for handling epidemiological weeks and patient age data.
    
    Attributes:
        df (pd.DataFrame): The input DataFrame containing the data to be cleaned.
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
        Calculate patient age based on birth date and event date.
        This method calculates the age in years using 'Fecha Nacimiento Paciente' (birth date)
        and 'Fecha del evento' (event date) columns. Results are stored in a new 'Edad Calculada'
        (calculated age) column.
        The calculation follows these steps:
        1. Verify required columns exist
        2. Calculate age using event date - birth date
        3. For missing ages, attempt calculation using emergency care date
        4. Handle missing values based on percentage:
            - If <10% missing: impute with median age
            - If ≥10% missing: remove rows with missing age
        Notes:
            - Ages are calculated by dividing days difference by 365
            - Negative ages (event before birth) are marked as NaN
            - Missing dates result in NaN ages
            - Imputed/removed age records are logged to Excel files
        Returns:
            None. Modifies the DataFrame in place by:
            - Adding 'Edad Calculada' column
            - Potentially removing rows with invalid ages
            - Creating log files for imputed/removed ages
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

    def get_clean_integer(self) -> pd.DataFrame:
        """
        Returns the cleaned DataFrame after applying all cleaning methods.

        This method applies all the cleaning methods defined in the class
        to the DataFrame, specifically:
        - Cleaning epidemiological week data
        - Cleaning patient age data

        Returns
        -------
        pd.DataFrame
            The cleaned DataFrame with all cleaning transformations applied
        """
        # Aplicar metodos de limpieza de la clase
        self.semana_epidemiologica()
        self.edad_paciente()

        return self.df


class DuplicateCleaner():
    """
    Class for detecting and resolving duplicate records in a DataFrame.

    This class identifies duplicates based on normalized text fields, RUT/ID validation, 
    and date comparisons, with a configurable similarity threshold. It provides methods 
    to log duplicates, retain the most complete record, and clean the DataFrame.

    Attributes:
        df (pd.DataFrame): The input DataFrame containing the data to be cleaned.
        columns_to_normalize (List[str]): List of text columns to normalize for comparison.
        duplicate_groups (List[List[int]]): Groups of indices for detected duplicate records.
        log_duplicados (List[pd.DataFrame]): Logs of detected duplicate records.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        """
        Initializes the class with the DataFrame to be cleaned.

        Attributes:
            df (pd.DataFrame): The input DataFrame containing the data to be cleaned.
            columns_to_normalize (List[str]): List of text columns to normalize for comparison.
            duplicate_groups (List[List[int]]): Groups of indices for detected duplicate records.
            log_duplicados (List[pd.DataFrame]): Logs of detected duplicate records.
        """

        self.df = df
        self.columns_to_normalize = [
            "Identificacion Paciente",
            "Nombre Paciente",
            "Apellido Paterno Paciente",
            "Apellido Materno Paciente"
        ]
        self.duplicate_groups = []  # Grupos de duplicados encontrados
        self.log_duplicados = []

    def name_normalization(self) -> None:
        """
        Normalizes text columns for duplicate detection by applying standardization transformations.
        This method processes specified columns in the DataFrame by:
        1. Converting text to lowercase
        2. Removing accents and diacritical marks
        3. Trimming leading/trailing spaces
        4. Creating a 'nombre_completo' field by concatenating patient name fields
        The normalization is applied to all columns specified in self.columns_to_normalize.
        Empty values are filled with blank strings before processing.
        Returns:
            None
        Side effects:
            - Modifies the DataFrame columns in-place
            - Creates a new 'nombre_completo' column by concatenating name fields
        """
        
        for col in self.columns_to_normalize:
            if col in self.df.columns:
                self.df[col] = (
                    self.df[col].fillna('')
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .str.normalize('NFKD')
                    .str.encode('ascii', errors='ignore')
                    .str.decode('utf-8')
                )

        self.df['nombre_completo'] = (
            self.df['Nombre Paciente'] +
            self.df['Apellido Paterno Paciente'] +
            self.df['Apellido Materno Paciente']
        )

    def normalize_identifications_ids(self) -> None:
        """
        Normalizes identification fields for patients by processing RUN/RUT and other ID types.

        This method handles two main cases:
        1. For RUN identifications with hyphens:
            - Splits the ID into base number and verification digit
            - Cleans non-numeric characters from base number
            - Calculates and verifies the verification digit

        2. For non-RUN identifications:
            - Removes non-numeric characters
            - Converts to integer format where possible

        The method modifies the following DataFrame columns in-place:
        - 'id_rut_id_base': Contains the cleaned numeric base ID
        - 'dv_original': Original verification digit (for RUN only)
        - 'dv_calculado': Calculated verification digit (for RUN only)

        Returns:
            None. The method modifies the DataFrame in-place.

        Note:
            - RUN/RUT is the Chilean national ID number
            - The method assumes the existence of 'Identificacion Paciente' and 'ID/RUT Paciente' columns
            """

        # Normalizar los RUN/RUT y calcular el dígito verificador
        rut_mask = (
            self.df['Identificacion Paciente'] == 'RUN'
        ) & (self.df['ID/RUT Paciente'].str.contains('-'))

        if rut_mask.any():
            # Dividir el RUT en número base y dígito verificador original
            split_rut = self.df.loc[rut_mask, 'ID/RUT Paciente'].str.split('-', expand=True)
            self.df.loc[rut_mask, 'id_rut_id_base'] = split_rut[0]  # Rut base
            self.df.loc[rut_mask, 'dv_original'] = split_rut[1]  # DV original

            # Limpiar el número base (eliminar caracteres no numéricos)
            self.df.loc[rut_mask, 'id_rut_id_base'] = self.df.loc[rut_mask, 'id_rut_id_base'].str.replace(
                '[^0-9]', '', regex=True
            ).str.strip()  # Elimina espacios en blanco antes y después

            self.df.loc[rut_mask, 'id_rut_id_base'] = self.df.loc[rut_mask, 'id_rut_id_base'].apply(
                lambda x: int(x) if x.isdigit() else None
            )

            # Calcular el dígito verificador
            self.df.loc[rut_mask, 'dv_calculado'] = self.df.loc[rut_mask, 'id_rut_id_base'].apply(
                lambda x: digito_verificador(x)
            )

        # Normalizar otros tipos de identificación
        mask_others_ids = self.df['Identificacion Paciente'] != 'RUN'

        if mask_others_ids.any():
            self.df.loc[mask_others_ids, 'id_rut_id_base'] = self.df.loc[mask_others_ids, 'ID/RUT Paciente'].str.replace(
                '[^0-9]', '', regex=True).str.strip()  # Elimina espacios en blanco antes y después

            # Convertir a entero, manejando valores vacíos
            self.df.loc[mask_others_ids, 'id_rut_id_base'] = self.df.loc[mask_others_ids, 'id_rut_id_base'].apply(
                lambda x: int(x) if (isinstance(x, str) and x.isdigit()) or (isinstance(x, float) and not pd.isna(x)) else None
            )

    def find_duplicates(self, similarity_threshold=90) -> pd.DataFrame:
        """
        Find and mark duplicate records in the DataFrame based on similarity comparison.
        This method identifies potential duplicate records by comparing a combined key of multiple fields
        using fuzzy string matching. Records are considered duplicates if their similarity exceeds the
        specified threshold.
        Args:
            similarity_threshold (int, optional): The minimum similarity percentage required to consider
                two records as duplicates. Defaults to 90.
        Returns:
            pd.DataFrame: A DataFrame containing only the identified duplicate records.
        Notes:
            - The method normalizes names and IDs before comparison
            - Comparison is based on: ID/RUT, full name, birth date, event date, and commune
            - Duplicates are marked in the original DataFrame with 'es_duplicado' column
            - Duplicate groups are stored in self.duplicate_groups
            - Detailed logs are saved to 'data/logs/duplicados.xlsx' and 'log_duplicados.txt'
        Side Effects:
            - Modifies the original DataFrame by adding 'es_duplicado' and 'compare_key' columns
            - Creates log files with duplicate records information
            - Updates self.duplicate_groups and self.log_duplicados

        """

        # Normalizar previamente nombres e identificaciones
        self.name_normalization()
        self.normalize_identifications_ids()

        # Crear columna combinada de comparación
        self.df['compare_key'] = (
            self.df['id_rut_id_base'].astype(str).fillna('') +
            self.df['nombre_completo'] +
            pd.to_datetime(self.df['Fecha Nacimiento Paciente'], errors='coerce').astype(str) +
            pd.to_datetime(self.df['Fecha del evento'], errors='coerce').astype(str) +
            self.df['Comuna'].fillna('').str.lower()
        )

        # DataFrame para resultados
        duplicates = []
        checked_indices = set()
        

        # Iterar sobre cada fila del DataFrame
        for idx, row in self.df.iterrows():
            if idx in checked_indices:
                continue

            current_key = row['compare_key']
            current_group = [idx]

            for idx2, row2 in self.df.loc[idx+1:].iterrows():
                if idx2 in checked_indices:
                    continue

                compare_key = row2['compare_key']

                # Calcular similitud usando fuzzywuzzy
                similarity = fuzz.ratio(current_key, compare_key)

                if similarity >= similarity_threshold:
                    current_group.append(idx2)
                    checked_indices.add(idx2)

            if len(current_group) > 1:
                duplicates.extend(current_group)
                self.duplicate_groups.append(current_group)  # Guarda los grupos aquí
                self.log_duplicados.append(self.df.loc[current_group, [
                    'ID/RUT Paciente', 
                    'Nombre Paciente', 
                    'Apellido Paterno Paciente',
                    'Apellido Materno Paciente', 
                    'Fecha Nacimiento Paciente',
                    'Fecha del evento', 
                    'Comuna', 
                    'Establecimiento Salud']])

        # Marcar duplicados en el DataFrame original
        self.df['es_duplicado'] = False
        self.df.loc[duplicates, 'es_duplicado'] = True


        # Logs de los duplicados detectados
        self.df.loc[duplicates, 'compare_key'].to_excel('data/logs/duplicados.xlsx', index=False) # mi forma
        
        # GPT style
        with open('log_duplicados.txt', 'w', encoding='utf-8') as log:
            for i, grupo in enumerate(self.log_duplicados, start=1):
                log.write(f"\n{'-'*20} Grupo duplicado {i} {'-'*20}\n")
                log.write(grupo.to_string(index=True))
                log.write("\n")

        return self.df[self.df['es_duplicado']]

    def keep_best_record(self) -> pd.DataFrame:
        """
        For each group of duplicate records, keeps the one with the most non-null values
        and discards the others. Discarded records are logged to a text file including
        key identifying information.
            pd.DataFrame: DataFrame with only the most complete record from each duplicate group,
                         with index reset. Updates the internal DataFrame state.
        Notes:
            - Writes discarded records to 'log_registros_descartados.txt'
            - Uses the following columns for logging discarded records:
                - ID/RUT Paciente
                - Nombre Paciente 
                - Apellido Paterno Paciente
                - Apellido Materno Paciente
                - Fecha de nacimiento del paciente
                - Fecha del evento
                - Comuna
                - Establecimiento de Salud
        """

        indices_to_drop = []
        log_descartados = []

        for group_indices in self.duplicate_groups:
            group_df = self.df.loc[group_indices]
            completeness = group_df.notna().sum(axis=1)
            best_index = completeness.idxmax()
            drop_indices = group_df.index.difference([best_index])
            indices_to_drop.extend(drop_indices)
            log_descartados.append(self.df.loc[drop_indices, [
                'ID/RUT Paciente', 'Nombre Paciente', 'Apellido Paterno Paciente',
                'Apellido Materno Paciente', 'Fecha Nacimiento Paciente',
                'Fecha del evento', 'Comuna', 'Establecimiento Salud'
            ]])

        # Generar log de registros descartados
        with open('log_registros_descartados.txt', 'w', encoding='utf-8') as log:
            for i, grupo in enumerate(log_descartados, start=1):
                log.write(f"\n{'-'*20} Registros descartados del grupo {i} {'-'*20}\n")
                log.write(grupo.to_string(index=True))
                log.write("\n")

        # Eliminar registros descartados
        self.df = self.df.drop(indices_to_drop).reset_index(drop=True)

        return self.df
    
    def get_clean_duplicates(self) -> pd.DataFrame:
        """
        This method applies cleaning methods of the class to handle duplicates:
        1. Finds duplicate records using find_duplicates()
        2. Keeps the best version of each duplicate using keep_best_record()
        Returns
        -------
        pd.DataFrame
            The cleaned DataFrame with duplicates handled, where only the best version
            of each duplicate record is kept.
        """
        
        # Aplicar metodos de limpieza de la clase
        self.find_duplicates()
        self.keep_best_record()

        return self.df


class CategoricalCleaner():

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    # TODO: Implementar el método para otra iteracion del proyecto 


class ApplyCleaners():
    """
    This class orchestrates the data cleaning process by sequentially applying multiple cleaners to a pandas DataFrame.

    The `ApplyCleaners` class is designed to streamline the data preprocessing workflow by integrating various cleaning 
    operations into a single pipeline. It applies the following steps in order:
    
    1. **FilterData**: Filters and selects relevant columns and rows based on predefined criteria.
    2. **DateCleaner**: Cleans and preprocesses date-related columns, handling invalid or missing dates.
    3. **IntegerCleaner**: Processes integer-based columns, such as epidemiological weeks and patient age.
    4. **DuplicateCleaner**: Identifies and resolves duplicate records based on normalized text fields and other criteria.
    5. **CategoricalCleaner** (future implementation): Will handle categorical data cleaning.

    This class ensures that the DataFrame is cleaned comprehensively and consistently, making it ready for analysis or 
    further processing.

    Attributes:
        df (pd.DataFrame): The input DataFrame containing the data to be cleaned.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df

    @st.cache_data
    def apply_cleaners(_self) -> pd.DataFrame:
        """
        Apply all data cleaners to a DataFrame sequentially.

        This method processes the input DataFrame through multiple cleaning stages:
        1. Filtering selected variables
        2. Cleaning date columns
        3. Cleaning integer columns
        4. Removing duplicates

        Returns:
            pd.DataFrame: The cleaned DataFrame after applying all cleaning operations.
        """

        _self.filter_data = FilterData(_self.df)
        _self.filter_data.filter_columns(_self.filter_data.selected_variables)
        _self.filter_data.get_filter_data()

        _self.date_cleaner = DateCleaner(_self.filter_data.df)
        _self.date_cleaner.get_clean_date()

        _self.integer_cleaner = IntegerCleaner(_self.date_cleaner.df)
        _self.integer_cleaner.get_clean_integer()

        _self.duplicate_cleaner = DuplicateCleaner(_self.integer_cleaner.df)
        _self.duplicate_cleaner.get_clean_duplicates()

        # _self.categorical_cleaner = CategoricalCleaner(_self.duplicate_cleaner.df)
        # _self.categorical_cleaner.get_clean_categorical()

        return _self.df
    
