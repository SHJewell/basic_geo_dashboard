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
        self.t = data_grp.variables['time'][:]
        self.data = data_grp.variables[self.var_name][:].filled(fill_value=np.nan)

        if "tas" in self.var_name:
            self.data = self.data - 273.15

        date_start = dparser.parse(self.path[-20:-12])
        #date_end = dparser.parse(self.path[-11:-3])

        dt = pd.date_range(date_start, periods=len(self.t))
        # self.dates = pd.DataFrame([dt, dt.strftime('%Y-%m-%d')]).T
        self.dates = pd.DataFrame([dt, dt.astype('int')]).T
        self.dates.columns = ['dt', 'epoch_dt']
        self.dates.index = self.t.astype(int)
        data_grp.close()

    def flatten_at_single_time(self, selected_date=None):
        if selected_date is None:
            print(f'No time given, defaulting to {self.t[0]} instead!')
            selected_date = self.t[0]

        time_indx = int(np.where(np.abs(self.t-selected_date) <= 1)[0][0])

        single_slice = pd.DataFrame(self.data[time_indx, :, :], index=self.lats, columns=self.lons)

        return single_slice

    def flatten_to_latlons(self, selected_date=None):
        if selected_date is None:
            print(f'No time given, defaulting to {self.t[0]} instead!')
            selected_date = self.t[0]

        time_indx = int(np.where(self.t == selected_date)[0][0])

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

        temp = self.dates['dt'].dt.year.drop_duplicates(keep='first')

        return dict(zip(temp.index.astype('str'), temp.astype('str').to_list()))

    def ret_time_series(self, lon, lat):

        dat = pd.DataFrame(self.data[:, np.where(self.lats == lat)[0][0], np.where(self.lons == lon)[0][0]], columns=['dat'])
        dat['5day'] = dat['dat'].rolling(5, min_periods=1).mean()
        dat['14day'] = dat['dat'].rolling(14, min_periods=1).mean()

        return dat

    def export_nc(self, data, var, exp_path):

        ds = netCDF4.Dataset(exp_path, data)
        t = ds.createDimension('time', len(self.t))
        lat = ds.createDimension('lat', len(self.lats))
        lon = ds.createDimension('lon', len(self.lons))
        value