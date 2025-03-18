import plotly.express as px

class Visualization:
    @staticmethod
    def histogram(df, column, nbins=15):
        """Crea un histograma de una columna"""
        return px.histogram(df, x=column, nbins=nbins)

    @staticmethod
    def boxplot(df, x_col, y_col):
        """Crea un boxplot comparando una variable categórica y una numérica"""
        return px.box(df, x=x_col, y=y_col)
