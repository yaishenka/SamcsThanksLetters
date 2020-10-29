from oauth2client.service_account import ServiceAccountCredentials
import gspread
from settings import account_credentials_file


class GoogleSheetsReader:
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(account_credentials_file, scope)
    gc = gspread.authorize(credentials)

    @staticmethod
    def get_all_records(table_url, sheet=0):
        sht = GoogleSheetsReader.gc.open_by_url(table_url)
        worksheet = sht.get_worksheet(sheet)
        return worksheet.get_all_records()
