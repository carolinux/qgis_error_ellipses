import numpy as np
import utm


"""Utilities for creating error ellipses"""

def add_3sigma_ellipses(gps):
    origlon = gps.lon.iloc[0]
    origlat = gps.lat.iloc[0]
    origeast, orignorth, zone, zone_num = utm.from_latlon(origlat, origlon)
    gps["east"] = gps.dx + origeast
    gps["north"] = gps.dy + orignorth
    for i in [1, 2 ,3]: # amount of standard deviations
        gps["ellipse_sigma{}".format(i)] = gps.apply(lambda x: get_ellipse_wkt(
            x["east"], x["north"], get_covariance_matrix(x["sde"], x["sdn"], x["sdne"]), i), axis=1)
    return gps



def ellipse_polyline(ellipse, n=20):
    """Turn an ellipse to a polygon approximation
    Code adapted from: http://stackoverflow.com/questions/15445546/finding-intersection-points-of-two-ellipses-python
    """
    
    t = np.linspace(0, 2*np.pi, n, endpoint=False)
    st = np.sin(t)
    ct = np.cos(t)
    x0, y0, a, b, angle = ellipse
    sa = np.sin(angle)
    ca = np.cos(angle)
    p = np.empty((n, 2))
    p[:, 0] = x0 + a * ca * ct - b * sa * st
    p[:, 1] = y0 + a * sa * ct + b * ca * st
    return p


def get_covariance_matrix(sde, sdn, sdne):
    """ According to the interpretation of the fields in:
    http://www.rtklib.com/prog/manual_2.4.2.pdf"""
    if sdne > 0:
        sign = 1
    else:
        sign = -1
    return np.array([[sde*sde, sign*sdne*sdne],[sign*sdne*sdne, sdn*sdn]])


def eigsorted(cov):
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    return vals[order], vecs[:,order]


def pts_to_wkt(pts):
    pts = np.concatenate((pts, np.array([pts[0]]))) # make it closed
    wkt = "POLYGON (("
    
    wkt = wkt + ",".join(map(lambda pt:"{} {}".format(pt[0], pt[1]), pts))
    wkt+="))"
    return wkt


def get_ellipse_wkt(x0, y0, cov, nstd):
    """ x0, y0 and cov must be in the same metric
    Code adapted from: http://stackoverflow.com/questions/20126061/creating-a-confidence-ellipses-in-a-sccatterplot-using-matplotlib
    """
    vals, vecs = eigsorted(cov)
    angle = np.arctan2(*vecs[:,0][::-1])
    a, b = nstd * np.sqrt(vals)

    ellipse = (x0, y0, a, b, angle)
    polyline = ellipse_polyline(ellipse)
    return pts_to_wkt(polyline)
