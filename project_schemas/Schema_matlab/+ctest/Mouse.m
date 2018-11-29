%{
# Mouse in the lab
mouse_id                    : char(8)                       # unique mouse id - CF_Sensor_number
---
dob                         : date                          # Date of birth
iacuc_barcode               : bigint unsigned               # The IACUC barcode on the cage
sex="M"                     : enum('M','F')                 # The mouse gender
genotype="C57/Bl6"          : varchar(1000)                 # The mouse strain
%}


classdef Mouse < dj.Manual
end