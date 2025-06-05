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

    def clean_numeric_column(self, column: str, pattern: str = r'(\d+(?:\.\d+)?)', fillna_value='0'):
        '''
        Làm sạch dữ liệu số. Nếu cột có đơn vị "triệu", chuyển sang tỷ bằng cách chia 1000.
        Loại bỏ các dòng chứa "giá thỏa thuận" trước khi xử lý.
        '''
        if column in self.df.columns:
            # Loại bỏ các dòng chứa "giá thỏa thuận"
            self.df = self.df[~self.df[column].str.contains('Giá thỏa thuận', case=False, na=False)]

        # Sao lưu dữ liệu gốc để nhận biết đơn vị
        self.df[column + '_raw'] = self.df[column].fillna(fillna_value).astype(str).str.lower()

        # Trích xuất phần số
        self.df[column] = self.df[column + '_raw'].str.extract(pattern)[0]

        # Ép kiểu float
        self.df[column] = pd.to_numeric(self.df[column], errors='coerce')

        # Chuyển triệu sang tỷ nếu có từ "triệu" trong dữ liệu gốc
        self.df[column] = self.df.apply(
            lambda row: row[column] / 1000 if 'triệu' in row[column + '_raw'] else row[column],
            axis=1
        )

        # Xóa cột tạm nếu không cần giữ lại
        self.df.drop(columns=[column + '_raw'], inplace=True)


    def get_clean_data(self) -> pd.DataFrame:
        return self.df


