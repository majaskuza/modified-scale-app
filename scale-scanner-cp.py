'''
scale-scanner-cp-main.py # main page, can select the experimenter
└─── pages/
  └─── scale-scanner-cp-auto.py # automatically start subj based on rfid scan
  └───scale-scanner-cp-manual.py # manually choose a subject to weight by selecting cage number and subjid
'''
import numpy as np
import pandas as pd
import streamlit as st
import scale_conn as sc
import messenger as msg
from scale_db_funcs import *
import helpers.DBUtilsClass as db
import datetime as DT

st.title("Animal Weighting and Running Controller")

if 'msg' not in st.session_state:
  st.session_state.msg = msg.zmq_messenger()
  st.session_state.msg.getPusherConnection()

DB_NAME = 'met'
if 'db_conn' not in st.session_state:
  st.session_state.db_conn = False

if st.session_state.db_conn == False:
  dbc = db.Connection()
  dbc.use(DB_NAME)
  st.write('Database connection OK')
  st.session_state.db_conn = True
  st.session_state.dbc = dbc
  st.session_state.room = whichRoom(dbc)
else:
  try:
    dbc = st.session_state.dbc
    dbc.use(DB_NAME)
    st.write('Database connection OK')
    st.session_state.db_conn = True
    st.session_state.room = whichRoom(dbc)
  except:
    st.session_state.db_conn = False
    st.write('Error while trying db connection, re-trying')
    dbc = db.Connection()
    dbc.use(DB_NAME)
    st.write('Database re-connection OK')
    st.session_state.db_conn = True
    st.session_state.dbc = dbc
    st.session_state.room = whichRoom(dbc)


col1_usr, col2_usr, col3_usr = st.columns(3)
run_subj_button = False
if 'current_user' not in st.session_state:
  st.session_state.current_user = False
  run_subj_button = True
elif len(st.session_state.current_user_name)<1:
  run_subj_button = True
else:
  run_subj_button = False

if run_subj_button:
  current_user_name = ''
  current_experid = 0
  userinfo = userList(dbc)

  users = {}
  for i in enumerate(userinfo):
      users[i[1][1]] = i[1][0]
  userlist = users.keys()

  st.write('Please select user')

  user_num = len(userlist)

  for i, x in enumerate(userlist):
    with col1_usr:
      if i%3 == 0:
        if st.button(list(userlist)[i]):
          current_experid = users[x]
          current_user_name = list(userlist)[i]
          st.write('user selected for '+str(current_user_name)+' id: '+ str(current_experid))
    with col2_usr:
      if i%3 == 1:
        if st.button(list(userlist)[i]):
          current_experid = users[x]
          current_user_name = list(userlist)[i]
          st.write('user selected for '+str(current_user_name)+' id: '+ str(current_experid))

    with col3_usr:
      if i%3 == 2:
        if st.button(list(userlist)[i]):
          current_experid = users[x]
          current_user_name = list(userlist)[i]
          st.write('user selected for '+str(current_user_name)+' id: '+ str(current_experid))
  st.session_state.current_experid = current_experid
  st.session_state.current_user_name = current_user_name
else:
  if st.button('deselect user ' + st.session_state.current_user_name):
    run_subj_button = True
    st.session_state.current_experid = 0
    st.session_state.current_user_name = ''
  current_experid = st.session_state.current_experid
  current_user_name = st.session_state.current_user_name

st.write('Scale connection')
if 'scale_conn' not in st.session_state:
  st.session_state.scale_conn = False

if st.session_state.scale_conn == False:
  scale_port_name = st.text_input('Using serial port ', '/dev/ttyUSB0')
  st.write('The scale is using serial port: ', scale_port_name)
  scale_ctx = sc.scale_serial_conn()
  scale_ctx.update_timeout(20)#update a longer timeout
  if st.button('connect with the scale'):
    try:
      scale_ctx.getConnection()
    finally:
      if scale_ctx.conn == 1:
        st.write('Scale connected!')
        st.session_state.scale_conn = True
        st.session_state.scale_ctx = scale_ctx
      else:
        st.write('Please check/retry scale conn')
else:
  scale_ctx = st.session_state.scale_ctx
  if st.button('disconnect scale at: ' + scale_ctx.serial_port_name):
    scale_ctx.close_conn()
    st.session_state.scale_conn = False

#read RFID feom keyboard input (UID scan devices)
if 'allow_rfid_read' not in st.session_state:
  st.session_state.allow_rfid_read = True

RFID_text = st.text_input(label='You can type or scan the RFID here', value='',key="rfid_text_input")   #for example: 71F7BF77 
def clear_text():
    st.session_state["rfid_text_input"] = ""

if len(RFID_text)>14:
  #st.session_state.allow_rfid_read = False
  RFID_text = RFID_text[0:15] #only read first 15 digit
  animal_info = getAnimalInfo(dbc,RFID_text)
  if animal_info:
    subjid = animal_info[0][0]
    pyratid = animal_info[0][1]
    cageid = animal_info[0][2]
    expgroup = animal_info[0][3]
    animal_owner = animal_info[0][4]
    d = {'subjid': [subjid], 'pyratid': [pyratid],'cageid': [cageid],'expgroup': [expgroup],'owner':[animal_owner]}
    df = pd.DataFrame(data=d)
    st.table(df)
    st.session_state.current_subjid = subjid
    st.session_state.current_rigid = 0

    rig_info = whichRig(dbc,subjid)
    if len(rig_info)>0:
      rigid = rig_info[0][0]
      rig_room = str(rigid)[0:3]
      if rig_room==st.session_state.room:
        st.info(f'this animal will be trained in rig {rigid} in this room')
        st.session_state.current_rigid = rigid
      else:
        st.warning(f'This animal need to be trained in ROOM {rig_room}')
        rigid = ''
    else:
      st.warning(f'This animal is not on training schedule')
      rigid = ''


  else:
    subjid = 0
    st.session_state.current_subjid = subjid
    st.session_state.current_rigid = 0
    st.error('Wrong RFID, Please Check!')

  if scale_ctx.conn == 1:
    scale_ctx.serial_port_clx.flushInput()#flush current data and waiti to get new data

if 'current_subjid' not in st.session_state:
  subjid = 0
  st.session_state.current_subjid = 0
  st.session_state.current_rigid = 0
else:
  subjid = st.session_state.current_subjid
  rigid = st.session_state.current_rigid

display_success = None
if subjid != 0:
  if scale_ctx.conn == 1:
    col1_run, col2_weight = st.columns(2)
    if rigid>0:
      with col1_run:
        if st.button('RUN',on_click=clear_text):
          st.write('Please put animal on the scale and wait for a reading')
          weight_reading = scale_ctx.read_scale_based_on_setting()
          st.write(f'Weight is {weight_reading:.2f}g')
          # do something to run animal
          if verify_weight(dbc,subjid,weight_reading): #otherwise need to re-weight
            massToDB(dbc, weight_reading, subjid, current_experid)
            # run_subj_in_rig(subjid,rigid)
            # submit animal weight
            st.session_state.msg.start_session(subjid,rigid) # send start message
            st.session_state.allow_rfid_read = True
            display_success = f'Running animal {subjid} in rig {rigid}'

          else:
            st.write('This weight is unexpected, please re-weigh the animal')

          st.session_state.current_subjid = 0
          st.session_state.current_rigid = 0

      with col2_weight:
        if st.button('WEIGHT ONLY',on_click=clear_text):
          st.write('Please put animal on the scale and wait for a reading')
          weight_reading = scale_ctx.read_scale_based_on_setting()
          st.write(f'Weight is {weight_reading:.2f}g')
          # submit animal weight
          if verify_weight(dbc,subjid,weight_reading): #otherwise need to re-weight
            massToDB(dbc, weight_reading, subjid, current_experid)
            display_success = f'Weight for {subjid} saved to database'
            st.session_state.allow_rfid_read = True
            st.session_state.current_subjid = 0
            st.session_state.current_rigid = 0
          else:
            st.write('This weight is unexpected, please re-weigh the animal')
    else:  #if not runable, put weight only button on the run side to reduce coginitive laod
      with col1_run:
        if st.button('WEIGHT ONLY',on_click=clear_text):
          st.write('Please put animal on the scale and wait for a reading')
          weight_reading = scale_ctx.read_scale_based_on_setting()
          st.write(f'current using weight {weight_reading:.2f}g')
          # submit animal weight
          if verify_weight(dbc,subjid,weight_reading): #otherwise need to re-weight
            display_success = f'Weight for {subjid} saved to database'
            massToDB(dbc, weight_reading, subjid, current_experid)
            st.session_state.allow_rfid_read = True
            st.session_state.current_subjid = 0
            st.session_state.current_rigid = 0
          else:
            st.write('This weight is unexpected, please re-weigh the animal')
    
  else:
    st.write('please connect the scale first')
    st.write('or you can run this animal without weighting')

    col1_run, col2_weight = st.columns(2)
    if rigid>0:
      with col1_run:
        if st.button('RUN WITHOUT WEIGHT',on_click=clear_text):
          # do something to run animal
          # rigid = get_subj_rigid(subjid)
          # run_subj_in_rig(subjid,rigid)
          display_success = f'running animal {subjid} in rig {rigid}'
          st.session_state.msg.start_session(subjid,rigid) # send start message
          st.session_state.allow_rfid_read = True
          st.session_state.current_subjid = 0
          st.session_state.current_rigid = 0
    with col2_weight:
      if st.button('Next, do nothing',on_click=clear_text):
          # do nothing here but re-set rfid read allowance
          st.session_state.allow_rfid_read = True
          st.session_state.current_subjid = 0
          st.session_state.current_rigid = 0


if display_success is not None:
  st.success(display_success)