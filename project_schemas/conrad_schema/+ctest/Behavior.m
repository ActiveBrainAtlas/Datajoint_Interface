%{
# Behavioral data (licking, running) associated with session
->Session
-----
lick_freq : longblob #The frequency of licks (Hz)
ang_vel : longblob #The angular velocity of running (deg/s)
t : longblob #The time from start of imaging session (s)
%}

classdef Behavior < dj.Imported

	methods(Access=protected)

		function makeTuples(self, key)
             pimg = fetch1(ctest.Session & key,'path_to_tiff');
             plab = fetch1(ctest.Session & key,'path_to_adi');
             
             disp(pimg);
             disp(plab);
             
             m = cniferObj();
             m.loadimg(pimg);
             m.loadlab(plab,fetch1(ctest.Session & key,'adi_trial_num'));
             m.analyzeLabchart([]);
             
             key.lick_freq = m.lab.lick;
             key.ang_vel = m.lab.vel;
             key.t = m.lab.t;
             
			 self.insert(key)
		end
	end

end