import numpy as np
import pandas as pd
import netCDF4
from netCDF4 import Dataset
from dataclasses import dataclass
import dateutil.parser as dparser
import datetime

@dataclass
class NCSet:
    path: str
    var_name: str

    def __post_init__(self):

        #self.var_name = self.path[(self.path.rfind('/')+1):self.path.find('_')]

        data_grp = Dataset(self.path)

        self.lats = data_grp.variables['lat'][:]
        self.lons = data_grp.variables['lon'][:]
        etime = data_grp.variables['time'][:]
        self.t = []
        # using a loop to convert the weird time format to datetime
        # there's probably a non-loop way to do this, but I am in a hurry today
        for elem in etime:
            self.t.append(datetime.timedelta(days=round(elem)) + datetime.date(year=1850, month=1, day=1))
        self.data = data_grp.variables[self.var_name][:].filled(fill_value=np.nan)

        if "tas" in self.var_name:
            self.data = self.data - 273.15

        #date_start = dparser.parse(self.path[-20:-12])
        date_start = self.t[0]
        #date_end = dparser.parse(self.path[-11:-3])

        dt = pd.date_range(date_start, periods=len(self.t))
        # self.dates = pd.DataFrame([dt, dt.strftime('%Y-%m-%d')]).T
        self.dates = pd.DataFrame([self.t, dt, dt.astype('int')]).T
        self.dates.columns = ['date', 'dt', 'epoch_dt']
        self.dates.index = range(len(self.t))
        data_grp.close()

    def flatten_at_single_time(self, selected_date=None):
        if selected_date is None:
            print(f'No time given, defaulting to {self.t[0]} instead!')
            #selected_date = self.t[0]
            selected_date = 0

        #time_indx = self.t[selected_date]

        single_slice = pd.DataFrame(self.data[selected_date, :, :], index=self.lats, columns=self.lons)

        return single_slice

    def flatten_to_latlons(self, selected_date=None):
        if selected_date is None:
            print(f'No time given, defaulting to {self.t[0]} instead!')
            selected_date = self.t[0]

        time_indx = selected_date
        # time_indx = int(np.where(self.t == selected_date)[0][0])

        dt = self.data[time_indx, :, :]

        XX, YY = np.meshgrid(np.arange(dt.shape[1]), np.arange(dt.shape[0]))
        table = np.vstack((dt.ravel(), XX.ravel(), YY.ravel())).T
        #table = np.delete(table, np.where(table[:, 0] == np.nan), axis=0)
        table = table[~np.isnan(table).any(axis=1)]
        table[:, 0] = np.round(table[:, 0], 3)
        table[:, 1] = (table[:, 1]/2) - 180
        table[:, 2] = (table[:, 2]/2) - 90

        return table

    def slider_dict(self):

        tdelt = int((self.dates['dt'].max() - self.dates['dt'].min()).days)
        # temp = self.dates['dt'].dt.year.drop_duplicates(keep='first')
        temp = self.dates['dt'].dt.year
        #ticks = dict(zip(self.dates['dt'].astype('str'), temp.astype('str').to_list()))
        ticks = dict(zip(list(range(len(self.dates))), temp.astype('str').to_list()))


        # This will adjust the slider ticks to be days, months or years as is appropriate to the amount of data

        if tdelt < 95:
            temp = [datetime.datetime.strftime(n, '%d/%m') for n in self.dates['dt']]
            ticks = dict(zip(list(range(len(self.dates))), temp))
        elif (tdelt < 1200) and (tdelt >= 95):
            temp = [datetime.datetime.strftime(n, '%Y') for n in self.dates['dt'].dt.month.drop_duplicates(keep='first')]
            ticks = dict(zip(list(range(len(self.dates))), temp))

        return ticks

    def ret_time_series(self, lon, lat):

        dat = pd.DataFrame(self.data[:, np.where(self.lats == lat)[0][0], np.where(self.lons == lon)[0][0]], columns=['dat'])
        dat['5day'] = dat['dat'].rolling(5, min_periods=1).mean()
        dat['14day'] = dat['dat'].rolling(14, min_periods=1).mean()

        return dat