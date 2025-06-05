import pandas as pd
import re

class DataCleaner:
    '''
        Lớp xử lý làm sạch, ép kiểu dữ liệu cho DataFrame bất động sản
    '''
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def drop_column(self, column_name: str):
        if column_name in self.df.columns:
            self.df.drop(columns=[column_name], inplace=True)

    def split_location_column(self, column: str = 'Vị trí'):
        if column in self.df.columns:
            self.df[['Quận/Huyện', 'Tỉnh']] = self.df[column].str.split(',', expand=True)
            self.df['Quận/Huyện'] = self.df['Quận/Huyện'].str.strip()
            self.df['Tỉnh'] = self.df['Tỉnh'].str.strip()

    def rename_column(self, old_name: str, new_name: str):
        if old_name in self.df.columns:
            self.df.rename(columns={old_name: new_name}, inplace=True)

    def clean_numeric_column(self, column: str, pattern: str = r'(\d+)', fillna_value='0'):
        if column in self.df.columns:
            self.df[column] = self.df[column].fillna(fillna_value)
            self.df[column] = self.df[column].astype(str).str.extract(pattern)
            self.df[column] = pd.to_numeric(self.df[column], errors='coerce')

    def get_clean_data(self) -> pd.DataFrame:
        return self.df
