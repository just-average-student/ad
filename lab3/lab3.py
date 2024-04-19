from spyre import server
import seaborn as sns
import pandas as pd
import urllib.request
import os
import datetime
import matplotlib.pyplot as plt
import re

if not os.path.exists('lab3_data'):
    os.makedirs('lab3_data')
def getting_data(i):
    filename_pattern = f"vhi_id_{i}"
    file_check = [el for el in os.listdir('./lab3_data') if el.startswith(filename_pattern)]
    if file_check:
        return
    url = f'https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={i}&year1=1981&year2=2024&type=Mean'
    vhi_url = urllib.request.urlopen(url)
    now = datetime.datetime.now()
    date_and_time = now.strftime("%d-%m-%Y-%H-%M-%S")
    filename = f'vhi_id_{i}_{date_and_time}.csv'
    file_path = os.path.join('./lab3_data', filename)
    with open(file_path, 'wb') as out:
        out.write(vhi_url.read())
    return f"File {file_path} downloaded"
for i in range(1, 28):
    getting_data(i)
def data_frame(path):
    files = [el for el in os.listdir(path) if el.endswith('.csv')]
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']
    dfs = []
    for file in files:
        file_path = os.path.join(path, file)
        i = int(file.split('_')[2])
        if i == 12 or i == 20:
            continue
        df = pd.read_csv(file_path, header = 1, names = headers)
        df = df.drop(df.loc[df['VHI'] == -1].index)
        df = df.drop('empty', axis=1)
        df.at[0, 'Year'] = df.at[0, 'Year'][9:]
        df = df.drop(df.index[-1])
        df['Year'] = df['Year'].astype(int)
        df['Week'] = df['Week'].astype(int)
        df['area'] = i
        dfs.append(df)
    df_r = pd.concat(dfs).drop_duplicates().reset_index(drop=True)
    return df_r
df = data_frame('./lab3_data')
province_indexes = {1: 22, 2: 24, 3: 23, 4: 25, 5: 3, 6: 4, 7: 8, 8: 19, 9: 20, 10: 21, 11: 9, 13: 10, 14: 11, 15: 12, 16: 13, 17: 14, 18: 15, 19: 16, 21: 17, 22: 18, 23: 6, 24: 1, 25: 2, 26: 7, 27: 5}
df['area'] = df['area'].replace(province_indexes)
regions = {
    1: 'Вінницька', 2: 'Волинська', 3: 'Дніпропетровська', 4: 'Донецька', 5: 'Житомирська',
    6: 'Закарпатська', 7: 'Запорізька', 8: 'Івано-Франківська', 9: 'Київська', 10: 'Кіровоградська',
    11: 'Луганська', 12: 'Львівська', 13: 'Миколаївська', 14: 'Одеська', 15: 'Полтавська',
    16: 'Рівенська', 17: 'Сумська', 18: 'Тернопільська', 19: 'Харківська', 20: 'Херсонська',
    21: 'Хмельницька', 22: 'Черкаська', 23: 'Чернівецька', 24: 'Чернігівська', 25: 'Республіка Крим'
}

class StockExample(server.App):
    title = "NOAA data vizualization"

    inputs = [{
                "type": 'dropdown',
                "label": 'NOAA data dropdown',
                "options": [{"label": "VCI", "value": "VCI"},
                            {"label": "TCI", "value": "TCI"},
                            {"label": "VHI", "value": "VHI"}],
                "key": 'ticker',
                "action_id": "update_data"
            },
            {
                "type": 'dropdown',
                "label": 'Region',
                "options": [{"label": f"{regions[i]} region", "value": i} for i in range(1, 26)],
                "key": 'region',
                "action_id": "update_data"
            },
            {
                "type": 'text',
                "label": 'Weeks range, correct format: "[1-52]-[1-52]", where the second number isn`t less than the first',
                "value": '1-52',
                "key": 'range',
                "action_id": "update_data"
            }]

    controls = [{"type" : "button", "label": "Update", "id" : "update_data"}]

    tabs = ["Table", "Plot"]

    outputs = [{"type": "table", "id": "table", "control_id": "update_data", "tab": "Table", "on_page_load": True},
               {"type": "plot", "id": "plot", "control_id": "update_data", "tab": "Plot"}]

    def getData(self, params):
        pattern = r'\d+-\d+$'
        if not re.match(pattern, params['range']):
            return pd.DataFrame()
        self.ticker = params['ticker']
        self.region = int(params['region'])
        self.range = params['range'].split('-')
        if self.ticker == "VCI":
            columns = ['Year', 'Week', 'VCI']
        elif self.ticker == "VHI":
            columns = ['Year', 'Week', 'VHI']
        elif self.ticker == "TCI":
            columns = ['Year', 'Week', 'TCI']
        data = df[(df['area'] == self.region) & (df['Week'] >= int(self.range[0])) & (df['Week'] <= int(self.range[1]))][columns]
        return data
    
    def getPlot(self, params):
        data_for_plot = self.getData(params)
        if data_for_plot.empty:
            return plt.gcf()
        plt.figure(figsize=(20, 10)) 
        plt.title(f'{self.ticker} values for {regions[self.region]} region')
        sns.heatmap(data_for_plot.pivot(index="Week", columns="Year", values=self.ticker), cmap="Greens", annot=True)
        return plt.gcf()

app = StockExample()
app.launch()
