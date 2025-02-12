"""
Módulo: data_loader
Responsabilidad: Cargar datos en un DataFrame de pandas
"""

import os
import pandas as pd
from typing import Optional


class DataLoader:
    """
    Clase para cargar datos en un DataFrame de pandas desde fuentes Excel o CSV.

    Atributos:
        file_path (str): Ruta al archivo (CSV o Excel).
        sheet_name (str | None): Nombre de la hoja, si es un archivo Excel.
    """

    def __init__(self, file_path: str, sheet_name: Optional[str] = None):
        """
        Inicializa la clase con la ruta al archivo y un nombre de hoja opcional.

        Args:
            file_path (str): Ruta absoluta o relativa al archivo.
            sheet_name (str | None): Nombre de la hoja de cálculo (opcional).
        """
        self.file_path = file_path
        self.sheet_name = sheet_name

    def load_data(self) -> pd.DataFrame:
        """
        Carga los datos en función de la extensión del archivo.
        - Si es .xlsx o .xls, intentará leer como Excel.
        - Si es .csv, intentará leer como CSV.

        Returns:
            pd.DataFrame: Los datos cargados en un DataFrame.

        Raises:
            ValueError: Si la extensión del archivo no es compatible.
            FileNotFoundError: Si el archivo no existe en la ruta indicada.
            Exception: Para errores inesperados de lectura.
        """
        # Verificar que el archivo existe
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"No se encontró el archivo: {self.file_path}")

        # Obtener la extensión del archivo
        extension = os.path.splitext(self.file_path)[1].lower()

        try:
            if extension in [".xls", ".xlsx"]:
                # Leer archivo Excel
                return self._load_excel()
            elif extension == ".csv":
                # Leer archivo CSV
                return self._load_csv()
            else:
                raise ValueError(f"Extensión de archivo no soportada: {extension}")
        except Exception as e:
            # Podrías capturar errores más específicos o realizar logs
            raise Exception(f"Error al leer el archivo {self.file_path}: {e}")

    def _load_excel(self) -> pd.DataFrame:
        """
        Carga datos desde Excel.
        Utiliza sheet_name si está especificado.
        """
        df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
        return df

    def _load_csv(self) -> pd.DataFrame:
        """
        Carga datos desde CSV.
        """
        df = pd.read_csv(self.file_path, encoding='utf-8')
        return df
