"""
Módulo: data_analyzer
Responsabilidad: Análisis estadístico y generación de salidas (gráficos, resúmenes) a partir de un DataFrame de pandas.
"""

import pandas as pd
import numpy as np
from typing import Optional, List
import plotly.express as px
import plotly.graph_objects as go


class DataAnalyzer:
    """
    Clase para realizar análisis estadístico descriptivo y exploratorio
    sobre un DataFrame ya limpio.

    Atributos:
        df (pd.DataFrame): El DataFrame que se va a analizar.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el DataAnalyzer con un DataFrame a analizar.

        Args:
            df (pd.DataFrame): DataFrame limpio o preprocesado.
        """
        self.df = df.copy()

    def basic_stats(self, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Retorna estadísticas descriptivas básicas (count, mean, std, min, 25%, 50%, 75%, max)
        para las columnas especificadas.
        Si no se proporcionan columnas, usa todas las columnas numéricas.

        Args:
            columns (List[str], opcional): Lista de columnas numéricas.

        Returns:
            pd.DataFrame: DataFrame con estadísticas descriptivas.
        """
        if columns is None:
            # Si no se especifican columnas, detectamos las numéricas
            columns = self.df.select_dtypes(include=[np.number]).columns.tolist()


        return self.df[columns].describe()

    def frequency_table(self, column: str, normalize: bool = True) -> pd.DataFrame:
        """
        Retorna la tabla de frecuencias absolutas y relativas de la columna dada.

        Args:
            column (str): Nombre de la columna para la cual se genera la tabla de frecuencia.
            normalize (bool): Indica si se incluyen frecuencias relativas (proporciones).
                              Por defecto True.

        Returns:
            pd.DataFrame: DataFrame con 'count' y 'proportion' (si normalize = True).
        """
        if column not in self.df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame.")

        counts = self.df[column].value_counts(dropna=False)
        if normalize:
            proportions = round((counts / counts.sum()) * 100, 2)
            freq_df = pd.DataFrame({'count': counts, 'proportion_%': proportions})
        else:
            freq_df = pd.DataFrame({'count': counts})

        freq_df.index.name = column
        freq_df.reset_index(inplace=True)
        return freq_df

    def group_stats(self, group_col: str, agg_col: str, funcs: List[str] = None) -> pd.DataFrame:
        """
        Retorna estadísticas agrupadas (ej. media, mediana, etc.) de 'agg_col' según 'group_col'.

        Args:
            group_col (str): Columna por la que se agrupará.
            agg_col (str): Columna numérica sobre la que se aplicarán las funciones de agregación.
            funcs (List[str], opcional): Lista de funciones de agregación soportadas por pandas
                                         (ej. ["mean", "median", "count"]).

        Returns:
            pd.DataFrame: DataFrame con los resultados de las agregaciones.
        """
        if funcs is None:
            funcs = ["count", "mean", "median", "std"]

        if group_col not in self.df.columns or agg_col not in self.df.columns:
            raise ValueError("Columna de agrupación o de agregación no existe en el DataFrame.")

        grouped = self.df.groupby(group_col)[agg_col].agg(funcs)
        return grouped.reset_index()

    def histogram(self, column: str, nbins: int = 20) -> go.Figure:
        """
        Genera un histograma (usando plotly) de la columna especificada.

        Args:
            column (str): Columna numérica a graficar.
            nbins (int): Número de bins del histograma.

        Returns:
            go.Figure: Objeto de plotly con el histograma.
        """
        if column not in self.df.columns:
            raise ValueError(f"La columna '{column}' no existe en el DataFrame.")

        fig = px.histogram(
            self.df,
            x=column,
            nbins=nbins,
            title=f"Histograma de {column}",
            color_discrete_sequence=["lightblue"]
        )
        fig.update_layout(
            xaxis_title=column,
            yaxis_title="Frecuencia"
        )
        return fig

    def boxplot(self, x_col: Optional[str], y_col: str, color_col: Optional[str] = None) -> go.Figure:
        """
        Genera un boxplot (usando plotly) con la variable dependiente y_col,
        categorizado por x_col (opcional) y coloreado por color_col (opcional).

        Args:
            x_col (str, opcional): Columna categórica para eje X.
            y_col (str): Columna numérica para eje Y.
            color_col (str, opcional): Columna para asignar colores.

        Returns:
            go.Figure: Objeto de plotly con el boxplot.
        """
        if y_col not in self.df.columns:
            raise ValueError(f"La columna '{y_col}' no existe en el DataFrame.")

        fig = px.box(
            self.df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=f"Boxplot de {y_col}" + (f" por {x_col}" if x_col else ""),
            points="outliers"  # Muestra puntos de outliers
        )
        return fig

    def line_chart(self, x_col: str, y_col: str, color_col: Optional[str] = None) -> go.Figure:
        """
        Genera un gráfico de líneas (usando plotly) para ver tendencias a lo largo del tiempo
        (u otra variable).

        Args:
            x_col (str): Columna para el eje X (fecha, semana, etc.).
            y_col (str): Columna numérica para el eje Y.
            color_col (str, opcional): Columna para separar líneas por categoría.

        Returns:
            go.Figure: Objeto de plotly con la línea.
        """
        if x_col not in self.df.columns or y_col not in self.df.columns:
            raise ValueError("x_col o y_col no existen en el DataFrame.")

        fig = px.line(
            self.df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=f"Gráfico de líneas: {y_col} vs. {x_col}"
        )
        return fig

    # Métodos de análisis adicionales
    # ---------------------------------------------------------------------
    # Puedes ir agregando lo que necesites: correlaciones, tablas cruzadas,
    # test estadísticos, etc.

    def get_df(self) -> pd.DataFrame:
        """
        Retorna el DataFrame interno sin modificar.
        (Útil si deseas extraerlo para guardar o continuar análisis en otro módulo).
        """
        return self.df
