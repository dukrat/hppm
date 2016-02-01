Most settings/options can be understood from reading the hppm_py/hppm_proc_py.ini configuration file.  

The Raspberry Pi code only supports LPD8806 at this time.  

hppm_py/ contains python code.  You can push OSC to it or use it alone with the GST module to get frequency data.  It can push via TCP, OSC, or serial.  
hppm_raspi/ contains C code.  It takes TCP input and pushes it to LPD8806 via spidev.  
hppm_ard/ contains Arudino code.  It takes serial input and push it to LPD8806 or WS2801.  
hppm_live/ contains MAX4Live files and a Live project.  It pushes OSC data.  

