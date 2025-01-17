import time
import sqlite3

from os.path import join

import numpy as np

from pytest  import fixture
from pytest  import mark

from . import load_db as DB


def test_sipm_pd(db):
    """Check that we retrieve the correct number of SiPMs."""
    sipms = DB.DataSiPM(db.detector, conf_label=db.conf_label)
    columns = ['SensorID', 'CardID', 'TofpetID', 'ChannelID', 'Active', 'X', 'Y', 'Z', 'adc_to_pes', 'Sigma']
    assert columns == list(sipms)
    assert sipms.shape[0] == db.nsipms


def test_sipm_pd_sim_only(db_sim_only):
    """Check that we retrieve the correct number of SiPMs for the full-body configuration."""
    sipms = DB.DataSiPMsim_only(db_sim_only.detector, conf_label=db_sim_only.conf_label)
    columns = ['SensorID', 'X', 'Y', 'Z', 'adc_to_pes', 'Sigma', 'PhiNumber', 'ZNumber']
    assert columns == list(sipms)
    assert sipms.shape[0] == db_sim_only.nsipms


def test_mc_runs_equal_data_runs(db):
    db1 = DB.DataSiPM(db.detector, -3550, conf_label=db.conf_label).values
    db2 = DB.DataSiPM(db.detector,  3550, conf_label=db.conf_label).values
    assert (db1 == db2).all()
