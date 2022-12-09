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
        self.data = data_grp.variables[self.var_name][:]

        # self.min = data.min(axis=0)
        # self.max = data.max(axis=0)
        # self.median = np.ma.median(data, axis=0)
        # self.var = data.var(axis=0)

        data_grp.close()

    def flatten_at_single_time(self, selected_date):

        time_indx = int(np.where(self.time == selected_date))

        single_slice = pd.DataFrame(self.data[time_indx,:,:], index=self.lats, columns=self.lons)

