import numpy as np
import pandas as pd
import netCDF4
from netCDF4 import Dataset
from dataclasses import dataclass
import dateutil.parser as dparser
import datetime
from operator import itemgetter

@dataclass
class multiVarNCSet:
    path: str
    vars: dict()
    def __post_init__(self):

        data_grp = Dataset(self.path, 'r')
        self.lats = data_grp.variables['lat'][:]
        self.lons = data_grp.variables['lon'][:]
        self.t = []
        self.data = dict()
        datestr = []

        for n, elem in enumerate(data_grp.variables['time'][:]):

            dayn = int(np.floor(elem))
            self.t.append(datetime.timedelta(days=dayn) + datetime.date(year=1850, month=1, day=1))
            datestr.append(self.t[n].strftime('%Y-%m-%d'))


        self.slider_dict = dict(zip(self.t, list(range(len(self.t)))))
        # self.slider_dict = dict(zip(list(range(len(self.t))), self.t))

        df = pd.DataFrame(pd.to_datetime(self.t), index=range(len(self.t)), columns=['dati'])
        df['my'] = df['dati'].dt.strftime("%b-%Y")
        self.slider_marks = dict(zip(df.groupby('my').head(1)['my'].index, df.groupby('my').head(1)['my']))

        for _, var_name in list(self.vars.items()):

            self.data[var_name] = data_grp.variables[var_name][:]

        data_grp.close()

    def flatten_at_single_time(self, var_name, selected_date=None):
        if selected_date is None:
            print(f'No time given, defaulting to {self.t[0]} instead!')
            #selected_date = self.t[0]
            selected_date = self.t[0]

        date_indx = self.slider_dict[selected_date]

        single_slice = pd.DataFrame(self.data[self.vars[var_name]][date_indx, :, :], index=self.lats, columns=self.lons)

        return single_slice

    def flatten_to_latlons(self, var_name, selected_date=None):
        if selected_date is None:
            print(f'No time given, defaulting to {next(iter(self.slider_dict))} instead!')
            selected_date = next(iter(self.slider_dict))

        time_indx = self.slider_dict[selected_date]
        # time_indx = int(np.where(self.t == selected_date)[0][0])

        dt = self.data[self.vars[var_name]][time_indx, :, :]

        XX, YY = np.meshgrid(np.arange(dt.shape[1]), np.arange(dt.shape[0]))
        table = np.vstack((dt.ravel(), XX.ravel(), YY.ravel())).T
        #table = np.delete(table, np.where(table[:, 0] == np.nan), axis=0)
        table = table[~np.isnan(table).any(axis=1)]
        table[:, 0] = np.round(table[:, 0], 3)
        table[:, 1] = (table[:, 1]/2) - 180
        table[:, 2] = (table[:, 2]/2) - 90

        return table

    def ret_time_series(self, var_name, lon, lat):

        dat = pd.DataFrame(self.data[self.vars[var_name]][:, np.where(self.lats == lat)[0][0], np.where(self.lons == lon)[0][0]], columns=['dat'])
        dat['5day'] = dat['dat'].rolling(5, min_periods=1).mean()
        dat['14day'] = dat['dat'].rolling(14, min_periods=1).mean()

        return dat


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

    def ret_time_series(self, lon, lat):

        dat = pd.DataFrame(self.data[:, np.where(self.lats == lat)[0][0], np.where(self.lons == lon)[0][0]], columns=['dat'])
        dat['5day'] = dat['dat'].rolling(5, min_periods=1).mean()
        dat['14day'] = dat['dat'].rolling(14, min_periods=1).mean()

        return dat