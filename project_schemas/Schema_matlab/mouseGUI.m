classdef mouseGUI < handle
    properties
        gui
        data
    end
    
    methods
        function obj = mouseGUI()
            obj.gui.f = figure('Toolbar','none','MenuBar','none');
            obj.gui.f.Position = [600,100,670,500];
            
            obj.gui.mousetitle = uicontrol('Style','text','Position',[10,460,315,25],'String','List of mice');
            obj.gui.mouselist = uicontrol('Style','listbox','Position',[10,50,315,400]);
            obj.gui.addmouse = uicontrol('Style','pushbutton','Position',[135,10,70,25],'String','Add mouse');
            
            obj.gui.sessiontitle = uicontrol('Style','text','Position',[345,460,315,25],'String','List of sessions');
            obj.gui.sessionlist = uicontrol('Style','listbox','Position',[345,50,315,400]);
            
            obj.gui.mdata.p = uimenu(obj.gui.f,'Label','File');
            obj.gui.mdata.fopen = uimenu(obj.gui.mdata.p,'Label','Connect');
            obj.gui.mdata.fconn = uimenu(obj.gui.mdata.p,'Label','Properties');
        end
    end
end