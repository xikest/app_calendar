from pathlib import Path
from datetime import date
from tools.web import WebDriver


class Scraper:

    def __init__(self, enable_headless=True, export_prefix: str = "scraper", intput_folder_path=None,
                 output_folder_path=None):
        """
        enable_headless=True,
        export_prefix:str="scaper",
        intput_folder_path = "input",
        output_folder_path="results"
        """
        
        self.intput_folder: Path
        self.output_folder: Path
        self.output_xlsx_name = None

        self.set_data_path(export_prefix=export_prefix, intput_folder_path=intput_folder_path,
                           output_folder_path=output_folder_path)
        self.web_driver = WebDriver(headless=enable_headless)
        self.wait_time = 1

    def set_data_path(self, export_prefix: str = None, intput_folder_path: str = None, output_folder_path: str = None):
        if intput_folder_path is not None:
            self.intput_folder = Path(intput_folder_path)  # 폴더 이름을 지정
            if not self.intput_folder.exists():
                self.intput_folder.mkdir(parents=True)

        if output_folder_path is not None:
            self.output_folder = Path(output_folder_path)
            if not self.output_folder.exists():
                self.output_folder.mkdir(parents=True, exist_ok=True)
            if export_prefix is not None:
                self.output_xlsx_name = self.output_folder / f"{export_prefix}{date.today().strftime('%Y-%m-%d')}.xlsx"
            else:
                self.output_xlsx_name = self.output_folder / f"{date.today().strftime('%Y-%m-%d')}.xlsx"
