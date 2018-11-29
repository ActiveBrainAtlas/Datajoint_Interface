%GUI for connecting and logging in to the datajoint database.
classdef connpropGUI < handle
    properties
        gui
        data
    end
    
    methods
        function obj = connpropGUI()
            obj.gui.f = figure('MenuBar','none','Toolbar','none');
            obj.gui.f.Position = [300,100,250,150];
            
            obj.gui.usertext = uicontrol('Style','text','String','Username','Position',[10,115,230,25]);
            obj.gui.user = uicontrol('Style','edit','String','','Position',[10,100,230,25],'Callback',{@obj.unset});
            
            obj.gui.passtext = uicontrol('Style','text','String','Password','Position',[10,55,230,25]);
            obj.gui.pass = uicontrol('Style','edit','String','','Position',[10,40,230,25],'Callback',{@obj.pwset});
            
            obj.data.hasUser = 0;
            obj.data.hasPW = 0;
            obj.data.isConnected = 0;
            
            obj.gui.login = uicontrol('Style','pushbutton','String','Login','Position',[90,10,70,25],'Callback',{@obj.login});
            obj.gui.login.Enable = 'off';
        end
        
        function unset(obj,src,evt)
            setenv('DJ_USER',obj.gui.user.Value);
            obj.data.hasUser = 1;
            
            if obj.data.hasUser && obj.data.hasPW
                obj.gui.login.Enable = 'on';
            end
        end
        
        function pwset(obj,src,evt)
            setenv('DJ_PASS',obj.gui.pass.Value);
            obj.data.hasPW = 1;
            
            if obj.data.hasUser && obj.data.hasPW
                obj.gui.login.Enable = 'on';
            end
        end
        
        function login(obj,src,evt)
            setenv('DJ_HOST','ucsd-demo-db.datajoint.io');
            dj.conn();
            
            obj.data.isConnected = 1;
         
            close(obj.gui.f);
        end
    end
end