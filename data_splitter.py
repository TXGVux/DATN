import pandas as pd
class DataSplitter:
    '''
    (Tuỳ chọn) Tách thành từng bản nhỏ và lưu thành file. 
    Mục đích: lần sau không cần đọc và xử lý lại dữ liệu thô
    '''

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def split_by_column(self, column: str, output_dir: str):
        pass
