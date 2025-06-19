import pandas as pd
import json

class DataSaver:
    def __init__(self, csv_file, json_file):
        self.csv_file = csv_file
        self.json_file = json_file

    def save(self, data):
        try:
            df = pd.DataFrame(data)
            df.to_csv(self.csv_file, index=False, encoding="utf-8-sig")
            with open(self.json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 Data saved to {self.csv_file} & {self.json_file}")
        except Exception as e:
            print(f"❌ Error saving data: {e}")