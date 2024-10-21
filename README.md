# scale-app

Scale-app is a core infrasturcture in DE Lab. It will read RFID from each animal, load BW from a connected scale and then upload the BW into lab database and/or start training session for the given animal based on trianing schedule.

![scale_app_overall_framework](docs/scale_app_framework.png)

## How it works

![scale-app_logic_flow](docs/scale_app_main_logic_flow.png)

The scale app will take initlize itself first (connect to db, load functions and modules), and then user can connect it to the scale and choose their own name as exper. 

After that it will enter idle mode, waiting for the input from RFID scanner. User need to press on the RFID input box to activate RFID input, and then after animal got scanner, the scale app will check the training schedule and if the animal is on the scehdule of this room, will give people two option to run the trianing session or just take a weight. Otherwise people will only have the `weight only` button.

After people hit the button, the scale app will start to read from the output of the scale in real time. Animals (especially rats) usually move a lot on the scale, we need to check whether we got a stable weight in real time. After it reach stable output (less than 5% flactuation in 500ms), the scale-app will take the average of that stable reading window and upload that weight.
![stable_threshold](docs/scale_app_BW_stable_output.png)

If user hit the `RUN` button, the scale app will send ZMQ message to start the training session for the given animal for its rig based on schedule.

If a TimeOut was reached (10 secs) and the scale-app still haven't got a stable input, it will ask people to reweight this animal.

## Hardware
+ a desktop computer (usually intel NUC) that connect to SWC ethernet, with Ubuntu 20.04
+ touch screen monitor [iiyama 22" T2252MSC-B2 Projective Capacitive Touch Screen Monitor](https://www.scan.co.uk/products/215-iiyama-t2252msc-b2-projective-capacitive-touchscreen-monitor-ips-5ms-1920x1080-10001-250cd-m2-dp)
+ a scale that can have serial output for weight readings. (for mouse, we use [MULTICOMP PRO MP700630](https://uk.farnell.com/multicomp-pro/mp700630/compact-balance-2000g-0-1g/dp/3583605?ost=3583605), for rats, we use KERN scales)
+ USB-Serial(RS232) cable to connect scale with a computer: [RS PRO RS232 USB A Male to DB-9 Male Converter Cable](https://uk.rs-online.com/web/p/interface-adapters-converters/1445699)
+ RFID scanner that fupport FDX-B ISO-11784/5 standard and USB output (as keyboard): [an example scanner from AMAZON](https://www.amazon.co.uk/Smoostart-Microchip-Scanner-134-2kHz-ISO11784/dp/B091FHNL1Y/ref=sxin_15_pa_sp_search_thematic_sspa?content-id=amzn1.sym.6f7c69df-26f6-4832-9363-65afabd498ba%3Aamzn1.sym.6f7c69df-26f6-4832-9363-65afabd498ba&crid=2QSTSBOYQYGNX&cv_ct_cx=pet+RFID+reader&dib=eyJ2IjoiMSJ9.gqArNnogChv8gujl6GzIZQKUgHVrR9N_D-CPN0FIZ8jKRzH_dI7rs6I_vFx8t0uASmmgF_3l7GCRF8xfr7j_bg.8H7sT1k5WkrTmaCkoXiBWZ4fsvc1BrGN9mVE0nmGEPQ&dib_tag=se&keywords=pet+RFID+reader&pd_rd_i=B091FHNL1Y&pd_rd_r=bbb7a311-6470-4410-ad91-9f6e3b8ab5bb&pd_rd_w=Oaunh&pd_rd_wg=gAlA2&pf_rd_p=6f7c69df-26f6-4832-9363-65afabd498ba&pf_rd_r=CRS6SBX433627BYM43C4&qid=1712533411&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D&sprefix=pet+rfid+reader%2Caps%2C70&sr=1-2-ad3222ed-9545-4dc8-8dd8-6b2cb5278509-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9zZWFyY2hfdGhlbWF0aWM&psc=1)


## requirement
+ pysql
+ pyserial
+ pandas
+ streamlit
+ [helpers](https://gitlab.com/sainsbury-wellcome-centre/erlichlab/helpers)
+ pyzmq stuff


## Run
to run this, you call
`python3 -m streamlit run scale-app/scale-scanner-cp.py`

## installation
### install conda stuff
+  install [Miniconda](https://docs.conda.io/en/latest/miniconda.html):1) download `Miniconda3 Linux 64-bit` 2) do [insall](https://conda.io/projects/conda/en/latest/user-guide/install/linux.html) by calling `bash Miniconda3-latest-Linux-x86_64.sh`
+ restart terminal, then install mamba `conda install -n base -c conda-forge mamba`

### dbconf
+ `cd`
+ `nano .dbconf`
```bash
[client]
user = derig
passwd = ASK JINGJIE/JEFF
host = db.deneuro.org

[zmq]
pushport = 7002
subport = 7001
url = tcp://127.0.0.1

[scale]
ver = rat #(or, ver = mouse)
```
### do git stuff
+ `sudo apt install git`
+ `cd; mkdir repos; cd repos`
+ `git clone https://derig:password_ask_labmember@gitlab.com/sainsbury-wellcome-centre/delab/devops/scale-app.git`
+ `git clone https://derig:password_ask_labmember@gitlab.com/sainsbury-wellcome-centre/delab/devops/zmq-proxy.git`
+ `git clone https://derig:password_ask_labmember@gitlab.com/sainsbury-wellcome-centre/erlichlab/helpers.git`


### create conda env for scale-app
+ `cd ~/repos/scale-app`
+ `export PYTHONPATH=~/repos`
+ `git checkout jingjie_Dev`
+ `mamba env create -f env.yml`


### run scale-app
+ `cd ~/repos/scale-app`
+ `conda activate scale`
+ `streamlit run scale-scanner-cp.py `



# setup a scale computer
+ install ubuntu 20.04, better to have a touch screen monitor for this computer
+ `sudo adduser $USER dialout`
+ `sudo usermod -a -G tty $USER`
+ `sudo usermod -a -G dialout $USER`
+ reboot (steps above granted permission for accessing the serial port)
+ install serial port monitor app for debugging `sudo apt install cutecom`
+ connect the scale with the computer with a USB-RS232 convertor
+ Setup the scale to be the proper output (check the next section for scale set-up)
+ open `cutecom` to check the serial weight info printing
+ install the scale-app as instructed previously
+ `sudo apt-get install chrome-gnome-shell`
+ disable touchscreen using `https://extensions.gnome.org/extension/3222/block-caribou-36/` (install the firefor extension as instruction on this page, and turn on this blocker)
+ install chrome, and put chrome broswer as the default broswer
+ using chrome broswer for the scale-app

## disable soft keyboard
+ install [flatpak](https://flathub.org/setup/Ubuntu)
+ install and run this [extension_manager](https://flathub.org/apps/com.mattjakeman.ExtensionManager)
+ run the extension manager, install the extension: block_caribou_36

# set up the scale
## rat scale: KERN FKB
+ see manual page 21 (English) for basic configration concept
+ press TARE long to enter the menu page
+ go to the unit page make sure it's in gram
+ exit the application menu page (see page 30 in the manual), entering the set-up menu
+ in communication (com) page, set to rs232, baud=9600, 
+ go back to data output page(print), interface-RS232,add-up mode-off,print note->manual->off,cont(continuous data output)->on, thenspeed-> set to 50(50ms)
+ open cutecom, set baud rate to 9600, connect to the tty, you should see the output is like this: ![rat scale example](examples/kern_rat_scale_example_output.png). Otherwise set output format to short (see manual 14.5)

