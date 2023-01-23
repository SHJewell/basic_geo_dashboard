import numpy as np
import pandas as pd
from netCDF4 import Dataset
from dataclasses import dataclass

@dataclass
class NCSet:
    path: str
    var_name: str

    def __post_init__(self):

        data_grp = Dataset(self.path)

        self.lats = data_grp.variables['lat'][:]
        self.lons = data_grp.variables['lon'][:]
        self.time = data_grp.variables['time'][:]
        self.data = data_grp.variables[self.var_name][:].filled(fill_value=np.nan)

        # self.min = data.min(axis=0)
        # self.max = data.max(axis=0)
        # self.median = np.ma.median(data, axis=0)
        # self.var = data.var(axis=0)

        data_grp.close()

    def flatten_at_single_time(self, selected_date=None):
        if selected_date is None:
            print(f'No time given, defaulting to {self.time[0]} instead!')
            selected_date = self.time[0]

        time_indx = int(np.where(self.time == selected_date)[0][0])

        single_slice = pd.DataFrame(self.data[time_indx, :, :], index=self.lats, columns=self.lons)

        return single_slice

    def flatten_to_latlons(self, selected_date=None):
        if selected_date is None:
            print(f'No time given, defaulting to {self.time[0]} instead!')
            selected_date = self.time[0]

        time_indx = int(np.where(self.time == selected_date)[0][0])

        dt = self.data[time_indx, :, :]

        XX, YY = np.meshgrid(np.arange(dt.shape[1]), np.arange(dt.shape[0]))
        table = np.vstack((dt.ravel(), XX.ravel(), YY.ravel())).T
        #table = np.delete(table, np.where(table[:, 0] == np.nan), axis=0)
        table = table[~np.isnan(table).any(axis=1)]
        table[:, 1] = (table[:, 1]/2) - 180
        table[:, 2] = (table[:, 2]/2) - 90

        return table