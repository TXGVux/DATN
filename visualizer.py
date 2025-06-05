import pandas as pd
# nếu dùng công cụ khác thì không cần
class Visualizer:
    '''
        Lớp trực quan hóa dữ liệu
    '''
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def plot_histogram(self, column: str):
        pass

    def plot_time_series(self, x: str, y: str):
        pass

    def plot_correlation_matrix(self):
        pass
