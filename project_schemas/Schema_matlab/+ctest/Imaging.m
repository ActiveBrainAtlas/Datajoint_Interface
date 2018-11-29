%{
# Imaging data associated with a session
->Session
-----
roi_img : longblob #The ROI used for calculating the fluorescence traces
yfp : longblob #The YFP fluorescence trace (dF/F)
cfp : longblob #The CFP fluorescence trace (dF/F)
fret : longblob #The FRET signal (dR/R = yfp/cfp - 1)
thresh : longblob #The reward threshold for the FRET signal
t : longblob #The time from the start of the imaging session
si : longblob #The scanimage property structure
%}

classdef Imaging < dj.Imported

	methods(Access=protected)

		function makeTuples(self, key)
			 pimg = fetch1(ctest.Session & key,'path_to_tiff');
             
             m = cniferObj();
             m.loadimg(pimg);
             
             key.roi_img = m.mask;
             key.yfp = m.mat.traces(:,2) - 1;
             key.cfp = m.mat.traces(:,1) - 1;
             key.fret = m.mat.traces(:,2)./m.mat.traces(:,1) - 1;
             key.fret = key.fret(:);
             key.thresh = m.mat.thresh(:);
             key.t = m.mat.t(:);
             serializedSI = getByteStreamFromArray(m.m.SI);
             key.si = serializedSI;
             
             self.insert(key);
		end
	end

end