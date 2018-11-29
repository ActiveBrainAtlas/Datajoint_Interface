%{
# 
-> ctest.Mouse
session                     : tinyint unsigned              # The session number
---
path_to_tiff                : varchar(1000)                 # Two photon tiff file
path_to_adi                 : varchar(1000)                 # Labchart file with behavioural data
adi_trial_num               : tinyint                       # The session number in the adicht file associated with this session
session_date                : date                          # The date of the session
type                        : enum('naive','fbd1','fbd2','post')        # The type of experimental trial
notes                       : varchar(10000)                # Notes for the session
%}


classdef Session < dj.Manual
end