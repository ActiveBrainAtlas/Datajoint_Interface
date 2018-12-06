classdef sessionGUI < handle
    properties
        gui;
        data;
    end
    
    methods
        function obj = sessionGUI(mouse_id)
            obj.gui.f = figure('Toolbar','none','MenuBar','none');
            obj.gui.f.Position = [600,100,350,200];

            obj.gui.tifbox = uicontrol('Style','text','Position',[10,155,250,25],'String','Tiff path...');
            obj.gui.tifbutton = uicontrol('Style','pushbutton','String','Browse...','Position',[270,155,70,25],'Callback',{@obj.loadtif});

            obj.gui.adibox = uicontrol('Style','text','Position',[10,115,250,25],'String','Adicht path...');
            obj.gui.adibutton = uicontrol('Style','pushbutton','String','Browse...','Position',[270,115,70,25],'Callback',{@obj.loadadi});
            
            obj.gui.adisession = uicontrol('Style','popupmenu','String',{'Load adi file first.'},'Position',[10,40,160,50]);
            obj.gui.adisession.Enable = 'off';
            
            obj.gui.sessiontype = uicontrol('Style','popupmenu','String',{'Naive','Day 1','Day 2','Post'},'Position',[180,40,160,50]);
            
            obj.gui.commit = uicontrol('Style','pushbutton','String','Add session','Position',[112.5,20,140,25],'Callback',{@obj.commitSession});
            obj.gui.commit.Enable = 'off';
            
            obj.data.mouse_id = mouse_id;
            obj.data.hasTif = 0;
            obj.data.hasAdi = 0;
        end
        
         function loadtif(obj,src,evt)
             n = importFile('tif');
             obj.gui.tifbox.String = n;
             obj.data.hasTif = 1;
             
             if obj.data.hasAdi && obj.data.hasTif
                 obj.gui.commit.Enable = 'on';
             end
         end
         
         function loadadi(obj,src,evt)
             obj.gui.adibox.String = importFile('adicht');
             s = adi.readFile(obj.gui.adibox.String);
             for i = 1:s.n_records
                obj.gui.adisession.String{i} = num2str(i);
             end
             obj.gui.adisession.Enable = 'on';
             
             obj.data.hasAdi = 1;
             if obj.data.hasAdi && obj.data.hasTif
                 obj.gui.commit.Enable = 'on';
             end
         end
         
         function commitSession(obj,src,evt)
             sobj.path_to_tiff = obj.gui.tifbox.String;
             sobj.path_to_adi = obj.gui.adibox.String;
             sobj.adi_trial_num = obj.gui.adisession.Value;
             sobj.type = obj.gui.sessiontype.String{obj.gui.sessiontype.Value};
             
             finf = dir(sobj.path_to_tiff);
             [y,m,d] = datevec(finf.datenum);
             sobj.session_date = [num2str(y,'%.4u') '-' num2str(m,'%.2u') '-' num2str(d,'%.2u')];
             
             insert(ctest.Session,sobj);
             
             obj.data.hasTif = 0;
             obj.data.hasAdi = 0;
             obj.gui.tifbox.String = 'Tiff path...';
             obj.gui.adibox.String = 'Adicht path...';
             
             obj.gui.commit.Enable = 'off';
             obj.gui.adisession.Enable = 'off';
             obj.gui.adisession.String = 'Load adi file first.';
         end
    end     
end 