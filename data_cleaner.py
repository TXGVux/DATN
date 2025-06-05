# data_cleaner.py
import pandas as pd
class DataCleaner:
    '''
        Lớp xử lý làm sạch, ép kiểu dữ liệu
    '''
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def drop_nulls(self, columns: list = None):
        pass

    def convert_types(self, type_dict: dict):
        pass

    def normalize_column_names(self):
        pass

    def clean_text_columns(self, columns: list):
        pass

    def get_clean_data(self) -> pd.DataFrame:
        return self.df
