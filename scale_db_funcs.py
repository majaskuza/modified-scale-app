import time
import helpers.DBUtilsClass as db
from helpers.net import getIP
import datetime as dt
import numpy as np

Z_SCORE_CUTOFF = 3.5

def userList(dbc):
    sqlstr = 'select experid,Firstname from experimenters where active=1 and tech=1'
    sqlo = dbc.query(sqlstr)
    return sqlo

def rankExp(dbc):
    sqlstr = 'select distinct experid from mass order by massid desc'
    sqlo = dbc.query(sqlstr)
    return sqlo

def whichRoom(dbc):
    IPaddr = getIP()
    sqlstr = 'select roomid from computers where IP=%s'
    roomid = dbc.query('select roomid from computers where IP=%s', (IPaddr,))[0][0]
    return roomid

def selectCage(dbc, IPaddr):
    '''which room is the rig in and select all the cage in this room'''
    roomid = dbc.query('select roomid from computers where IP=%s', (IPaddr,))[0][0]
    #Maja removed the specifying of mice vs rat
    species = 'rat'
    sqlstr = 'select distinct(cageid) from animals where species=%s and cageid is not null and status <> "dead" order by cageid'
    sqlo = dbc.query(sqlstr, (species,))
    return sqlo

def selectAnimal(dbc, cageid):
    '''select animal info'''
    sqlstr = """
        select distinct animalid, subjid, status, strain, iacucprotocol, expgroupid, rfid, rigid 
        from animals a left join schedule_today s using (subjid) 
        where a.cageid=%s;
        """
    sqlo = dbc.query(sqlstr, (cageid,))
    return sqlo

def getAnimalInfo(dbc,rfid):
    sqlstr = ('select subjid,pyratid,cageid,expgroup,owner from animals where rfid = "' + rfid + '"')
    sqlo = dbc.query(sqlstr)
    return sqlo

def whichRig(dbc,subjid):
    sqlstr = ('select rigid from schedule_today where subjid = "' + subjid + '"')
    sqlo = dbc.query(sqlstr)
    return sqlo
def expDescription(dbc, expgroupid):
    sqlstr = 'select description from met.expgroups where expgroupid=%s'
    sqlo = dbc.query(sqlstr, (expgroupid,))
    return sqlo
def massToDB(dbc, mass, subjid, experid):
    ''' save mass to DB'''
    dbc.call('met.addMassReading(%s, %s, %s)', (subjid, float(mass), experid))
    dbc.commit()
    #sqlstr = 'insert into mass(mass,animalid,experid) values(%s,%s,%s)'
    #dbc.execute(sqlstr, (mass, subjid, experid))
def runSubject(dbc, subjid):
    dbc.call('met.runSubject(%s)', (subjid,))
    dbc.commit()

def selectMass(dbc,animalid):
    sqlstr = 'select mass from mass where subjid=%s'
    sqlo = dbc.query(sqlstr, (animalid,))
    return sqlo

def verify_weight(dbc,subjid:str = None,weight_reading:float = 0) -> bool:
    '''
    This function will check if the current weight just measured is within acceptable 
    window (z-score checking)

    adapted from : https://gitlab.com/sainsbury-wellcome-centre/delab/devops/bpodautopy/-/blob/main/bpodautopy/weight_alarm.py#L111
    '''
    if weight_reading<5:
        return False
        # This is almost certainly not needed, but left here for backwards compatibility

    assert subjid != None, "Subject Id not there"

    # fit the weights from past 10 days and check the z score
    # get data from last 10 days
    ten_days_mass_list = dbc.query(f"select mass from met.mass where subjid = '{subjid}' and CAST(mdate AS DATE) > DATE(NOW() - INTERVAL 11 DAY) order by mdate desc")

    if len(ten_days_mass_list) <= 5:
        # we only do mass check if we have enough data
        return True

    latest_mass = ten_days_mass_list[0][0]
    past_mass = ten_days_mass_list[1:]
    mass_std = np.std(past_mass)
    if mass_std > 0: #do we want to ignore small std here?
        z_score = (latest_mass - np.mean(past_mass))/mass_std
    else:
        z_score = 0

    return True
    #return abs(z_score) < Z_SCORE_CUTOFF
