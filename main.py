import pandas as pd

from ellipses import add_3sigma_ellipses
from sqlite import df_to_sqlite

df = pd.read_csv("./20160303_Session1_2_gps.csv")
dfe = add_3sigma_ellipses(df)

dfe = dfe[["timestamp","lon","lat","ellipse_sigma1","ellipse_sigma2","ellipse_sigma3"]]
dfe.to_csv("20160303_Session1_2_gps_with_ellipses.csv",index=False)

# 32632 -> the UTM Zone for Switzerland: https://epsg.io/32632
geom_columns = [("ellipse_sigma1","POLYGON", 32632), ("ellipse_sigma2","POLYGON", 32632), ("ellipse_sigma3","POLYGON", 32632)]
df_to_sqlite(dfe, "20160303_Session1_2_gps_with_ellipses.sqlite", "gps", index_col="timestamp", geom_columns=geom_columns)
