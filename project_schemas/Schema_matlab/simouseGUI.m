%GUI for handling new sessions directly from scanimage. Assumes the
%conrad_test schema is located in a package called +ctest.
classdef simouseGUI < handle
    properties
        gui
        data
    end
    
    methods
        function obj = simouseGUI(varargin)
            obj.gui.f = figure('Toolbar','none','MenuBar','none');
            obj.gui.f.Position = [600,100,335,500];
            
            obj.gui.mouselist = uicontrol('Style','popupmenu','Position',[10,470,315,25],'String',{'Add mouse...'},'Callback',{@obj.selectmouse});
            obj.gui.mouselist.Enable = 'off';
            
            obj.gui.sessiontitle = uicontrol('Style','text','Position',[10,445,157,25],'String','Sessions');
            obj.gui.sessionlist = uicontrol('Style','listbox','Position',[10,250,157,200],'Callback',{@obj.loadsession});
            
            obj.gui.mdata.connect = uimenu(obj.gui.f,'Label','Connect...','Callback',{@obj.login});
            obj.gui.mdata.export = uimenu(obj.gui.f,'Label','Export...','Callback',{@obj.export});
            obj.gui.mdata.export.Enable = 'off';
            
            obj.gui.notebox = uicontrol('Style','edit','Position',[10,10,315,200],'HorizontalAlignment','left','Max',5,'Callback',{@obj.addnotes});
            obj.gui.notebox.Enable = 'off';
            obj.gui.notetitle = uicontrol('Style','text','String','Session Notes','Position',[10,210,315,25]);
            
            obj.gui.yoke = uicontrol('Style','checkbox','String','Sync to Scanimage','Position',[187,370,157,25],'Callback',{@obj.synctoggle});
            if nargin > 0
                obj.data.hFB = varargin{1};
            else
                obj.gui.yoke.Enable = 'off';
            end
            
            obj.gui.stype = uicontrol('Style','popupmenu','String',{'Naive','Day 1','Day 2','Post'},'Position',[187,300,140,25]);
            obj.gui.stype.Enable = 'off';
            
            obj.data.tmap = containers.Map();
            obj.data.tmap('naive') = 1; obj.data.tmap('fbd1') = 2; obj.data.tmap('fbd2') = 3; obj.data.tmap('post') = 4;
            obj.data.isNewSession = 0;
        end
        
        function login(obj,src,evt)
            [user,pw] = logindlg;
            setenv('DJ_HOST','ucsd-demo-db.datajoint.io');
            setenv('DJ_USER',user);
            setenv('DJ_PASS',pw);
            
            dj.conn();
            
            obj.data.mice = fetch(ctest.Mouse);
            obj.data.mice = {obj.data.mice.mouse_id};
            
            obj.gui.mouselist.String = [obj.gui.mouselist.String,obj.data.mice];
            obj.gui.mouselist.Enable = 'on';
        end
        
        function selectmouse(obj,src,evt)
            mouseidx = obj.gui.mouselist.Value;
            obj.data.mid = obj.gui.mouselist.String{obj.gui.mouselist.Value};
            
            if mouseidx == 1
                mname = inputdlg({'Enter mouse name:','Date of birth:'},'New Mouse');
                mouse.mouse_id = mname{1};
                try
                    d = datetime(mname{2},'InputFormat','yyyy-MM-dd');
                    mouse.dob = mname{2};
                    mouse.iacuc_barcode = 0;
                    insert(ctest.Mouse,mouse);
                    obj.gui.mouselist.String = [obj.gui.mouselist.String,mname{1}];
                    obj.data.mice = [obj.data.mice, mname{1}];
                catch
                    error('Invalid date of birth.');
                end
            else
                sessions = fetch(ctest.Session & ['mouse_id = "' obj.data.mid '"']);
                
                slist = {};
                for i = 1:length(sessions)
                    slist{i} = num2str(sessions(i).session);
                end
                
                obj.gui.sessionlist.String = slist;
                obj.gui.sessionlist.Max = length(slist);
                
                obj.gui.notebox.String = '';
            end
            
            obj.gui.mdata.export.Enable = 'off';
        end
        
        function loadsession(obj,src,evt)
            if ~isempty(obj.gui.sessionlist.Value)
                sessioncondition = ['session = ' obj.gui.sessionlist.String{obj.gui.sessionlist.Value(1)}];
                for i = 2:length(obj.gui.sessionlist.Value)
                    sessioncondition = [sessioncondition '|| session = ' obj.gui.sessionlist.String{obj.gui.sessionlist.Value(i)}];
                end
                obj.data.session = fetch(ctest.Session & ['mouse_id = "' obj.data.mid '"'] & sessioncondition,'notes','*');
                if length(obj.data.session) < 2
                    obj.gui.notebox.String = obj.data.session.notes;
                    obj.gui.notebox.Enable = 'inactive';
                    obj.gui.stype.Value = obj.data.tmap(obj.data.session.type);
                    obj.gui.stype.Enable = 'inactive';
                end
                
                obj.gui.mdata.export.Enable = 'on';
            else
                obj.gui.mdata.export.Enable = 'off';
            end
        end
        
        function addnotes(obj,src,evt)
            if obj.data.isNewSession
                obj.data.session.notes = obj.gui.notebox.String;
            end
        end
        
        function export(obj,src,evt)
            imout = fetch(ctest.Imaging & obj.data.session,'*');
            bout = fetch(ctest.Behavior & obj.data.session,'*');
            
            for i = 1:length(imout)
                sobj(i).img.fret = imout(i).fret;
                sobj(i).img.t = imout(i).t;
                sobj(i).mat.thresh = imout(i).thresh;
                
                sobj(i).lab.t = bout(i).t(:);
                sobj(i).lab.lick = bout(i).lick_freq;
                sobj(i).lab.vel = bout(i).ang_vel;
                
                a = diff(sobj(i).mat.thresh);
                sobj(i).rewidx = find(a > 0);
            end
            
            assignin('base','sessions',sobj);
        end
        
        function synctoggle(obj,src,evt)
            if obj.gui.yoke.Value && obj.gui.yoke.Value ~= obj.data.isNewSession
                obj.data.session = [];

                obj.gui.stype.Value = 1;
                obj.gui.stype.Enable = 'on';

                obj.gui.notebox.String = '';
                obj.gui.notebox.Enable = 'on';
            end
            obj.data.isNewSession = obj.gui.yoke.Value;
        end
        
        function commitSession(obj)
            obj.data.hFB;
        end
    end
end