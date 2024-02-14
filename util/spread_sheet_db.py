import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pandas as pd
import os

class SpreadSheetDatabase:
    def __init__(self):

        CREDENTIAL_FILE = os.environ["ST_CREDENTIAL_FILE"]
        SPREADSHEET_KEY = os.environ["ST_SPREADSHEET_KEY"]
        #jsonファイルを使って認証情報を取得
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        c = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_FILE, scope)

        #認証情報を使ってスプレッドシートの操作権を取得
        gs = gspread.authorize(c)
        #共有したスプレッドシートのキー（後述）を使ってシートの情報を取得
        self.ws = gs.open_by_key(SPREADSHEET_KEY).worksheet("Sheet1")

    def get_registered_job_ids(self, since: datetime):
        records = self.ws.get_all_records()
        df = pd.DataFrame.from_records(records)
        df['registered_at'] = pd.to_datetime(df['registered_at'])
        filtered_df = df[df['registered_at'] >= since]
        return filtered_df['job_id'].tolist()

    def insert_df(self, df: pd.DataFrame):
        df_to_insert = df.astype(str)
        list_of_lists = df_to_insert.values.tolist()
        for row in list_of_lists:
            self.ws.append_row(row)

    def insert_data(self, data: list[str]):
        self.ws.append_row(data)