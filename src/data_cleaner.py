"""
Módulo: data_cleaner
Responsabilidad: Limpiar y preprocesar los datos en un DataFrame de pandas.
"""

import pandas as pd
from typing import List, Optional, Union


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
            & (self.df['Tipo de Caso'] == 'Cerrado') # TODO: Excluir explicitamente NaN
            & (self.df['Estado'] == 'Finalizado')
            & (self.df['Clasificación'] == 'Confirmado LAIN')
            & (self.df['Subclasificacion'].isin(['Con intención suicida', 'Sin intención suicida'])) # TODO: Excluir explicitamente NaN
            & (self.df['Lesion fue Autoinfligida'] == 'Si')
            & (self.df['Lesion fue Intencional'] == 'Si')
            & (self.df['Tuvo intencion de Morir'].isin(['Si', 'No']))
            & (self.df['Region'] == 'REGION DE ANTOFAGASTA') # TODO: Extender el analisis a otras regiones para comparacion
            & (self.df['Edad Paciente'] > 0)
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
