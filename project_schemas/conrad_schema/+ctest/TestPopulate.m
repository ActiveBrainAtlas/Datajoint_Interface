%{
# Test of populate from manual data
->Session
-----
# add additional attributes
expmt_type : varchar(1000) #Just returns the session number
%}

classdef TestPopulate < dj.Imported

	methods(Access=protected)

		function makeTuples(self, key)
		%!!! compute missing fields for key here
            p = fetch1(ctest.Session & key,'type'); 
            key.expmt_type = p;
			self.insert(key)
		end
	end

end