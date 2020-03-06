import os, sys
import subprocess
from utilities.utilities2015 import *
from utilities.registration_utilities import *
from utilities.annotation_utilities import *
from utilities.metadata import *
from utilities.data_manager_v2 import DataManager
from utilities.a_driver_utilities import *

from a_GUI_utilities_pipeline_status import *

import time
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *

def format_grid_button_initial( button ):
    button.setDefault( True )
    button.setEnabled(True)
    button.setStyleSheet('QPushButton { \
                          background-color: #FDB0B0; \
                          color: black; \
                          border-radius: 15px; \
                          font-size: 26px;}')
    button.setMinimumSize(QSize(150, 150))
    
def format_grid_button_cantStart( button ):
    button.setEnabled(False)
    button.setStyleSheet('QPushButton { \
                          background-color: #868686; \
                          color: black; \
                          border-radius: 15px; \
                          font-size: 26px;}')

def format_grid_button_completed( button ):
    button.setEnabled(False)
    button.setStyleSheet('QPushButton { \
                          background-color: #B69696; \
                          color: black; \
                          border-radius: 15px; \
                          font-size: 26px;}')

class init_GUI(QWidget):
    def __init__(self, parent = None):
        super(init_GUI, self).__init__(parent)
        self.font1 = QFont("Arial",16)
        self.font2 = QFont("Arial",12)

        # Stack specific info, determined from dropdown menu selection
        self.stack = ""
        self.stain = ""
        self.detector_id = ""
        self.img_version_1 = ""
        self.img_version_2 = ""
        
        self.curr_step = ""
        
        self.initial_bottom_text = "Push `Finished` to exit the GUI"

        self.initUI()

    def initUI(self):
        # Set Layout and Geometry of Window
        self.grid_top = QGridLayout()
        self.grid_buttons = QGridLayout()
        self.grid_bottom = QGridLayout()
        
        #self.setFixedSize(1000, 450)
        self.resize(1000, 450)

        ### Grid Top (1 row) ###
        # Static Text Field
        self.e1 = QLineEdit()
        self.e1.setValidator( QIntValidator() )
        self.e1.setMaxLength(6)
        self.e1.setAlignment(Qt.AlignRight)
        self.e1.setFont( self.font1 )
        self.e1.setReadOnly( True )
        self.e1.setText( "Stack:" )
        self.e1.setFrame( False )
        self.grid_top.addWidget( self.e1, 0, 0)
        # Dropbown Menu (ComboBox) for selecting Stack
        self.cb = QComboBox()
        self.cb.addItems( all_stacks )
        self.cb.setFont( self.font1 )
        self.cb.currentIndexChanged.connect( self.newDropdownSelection )
        self.grid_top.addWidget(self.cb, 0, 1)
        # Static Text Field
        self.e2 = QLineEdit()
        self.e2.setValidator( QIntValidator() )
        self.e2.setMaxLength(6)
        self.e2.setAlignment(Qt.AlignRight)
        self.e2.setFont( self.font1 )
        self.e2.setReadOnly( True )
        self.e2.setText( "Stain:" )
        self.e2.setFrame( False )
        self.grid_top.addWidget( self.e2, 0, 2)
        # Static Text Field
        self.e3 = QLineEdit()
        self.e3.setValidator( QIntValidator() )
        self.e3.setMaxLength(9)
        self.e3.setAlignment(Qt.AlignLeft)
        self.e3.setFont( self.font1 )
        self.e3.setReadOnly( True )
        self.e3.setText( "" )
        self.e3.setFrame( False )
        self.grid_top.addWidget( self.e3, 0, 3)
        # Button Text Field
        self.b_refresh = QPushButton("Refresh")
        self.b_refresh.setDefault(True)
        self.b_refresh.clicked.connect(lambda:self.button_push(self.b_refresh))
        self.grid_top.addWidget( self.b_refresh, 0, 4)

        ### Grid Buttons ###
        # Button
        self.b_setup = QPushButton("Setup")
        format_grid_button_initial( self.b_setup )
        self.b_setup.clicked.connect( lambda:self.button_grid_push(self.b_setup) )
        self.grid_buttons.addWidget( self.b_setup, 0, 0)
        # Button
        self.b_align = QPushButton("Align")
        format_grid_button_initial( self.b_align )
        self.b_align.clicked.connect( lambda:self.button_grid_push(self.b_align) )
        self.grid_buttons.addWidget( self.b_align, 0, 1)
        # Button
        self.b_mask = QPushButton("Mask")
        format_grid_button_initial( self.b_mask )
        self.b_mask.clicked.connect( lambda:self.button_grid_push(self.b_mask) )
        self.grid_buttons.addWidget( self.b_mask, 0, 2)
        # Button
        self.b_crop = QPushButton("Crop")
        format_grid_button_initial( self.b_crop )
        self.b_crop.clicked.connect( lambda:self.button_grid_push(self.b_crop) )
        self.grid_buttons.addWidget( self.b_crop, 1, 0)
        # Button
        self.b_globalFit = QPushButton("Rough Atlas Fit")
        format_grid_button_initial( self.b_globalFit )
        self.b_globalFit.clicked.connect( lambda:self.button_grid_push(self.b_globalFit) )
        self.grid_buttons.addWidget( self.b_globalFit, 1, 1)
        # Button
        self.b_localFit = QPushButton("Local Atlas Fit")
        format_grid_button_initial( self.b_localFit )
        self.b_localFit.clicked.connect( lambda:self.button_grid_push(self.b_localFit) )
        self.grid_buttons.addWidget( self.b_localFit, 1, 2)
        
        ### Grid Bottom ###
        # Button Text Field
        self.b_newBrain = QPushButton("New Brain")
        self.b_newBrain.setDefault(True)
        self.b_newBrain.clicked.connect(lambda:self.button_push(self.b_newBrain))
        self.grid_bottom.addWidget(self.b_newBrain, 0, 1)
        # Button Text Field
        self.b_prevStep = QPushButton("Go to Previous Step")
        self.b_prevStep.setDefault(True)
        self.b_prevStep.clicked.connect(lambda:self.button_push(self.b_prevStep))
        self.grid_bottom.addWidget(self.b_prevStep, 0, 2)
        # Button Text Field
        self.b_neuroglancer = QPushButton("Neuroglancer Utilities")
        self.b_neuroglancer.setDefault(True)
        self.b_neuroglancer.clicked.connect(lambda:self.button_push(self.b_neuroglancer))
        self.grid_bottom.addWidget(self.b_neuroglancer, 0, 3)
        # Button Text Field
        self.b_datajoint = QPushButton("Datajoint Utilities")
        self.b_datajoint.setDefault(True)
        self.b_datajoint.clicked.connect(lambda:self.button_push(self.b_datajoint))
        self.grid_bottom.addWidget(self.b_datajoint, 0, 4)
        # Button Text Field
        self.b_exit = QPushButton("Exit")
        self.b_exit.setDefault(True)
        self.b_exit.clicked.connect(lambda:self.button_push(self.b_exit))
        self.grid_bottom.addWidget(self.b_exit, 0, 5)

        #self.grid_buttons.setColumnStretch(1, 3)
        #self.grid_buttons.setRowStretch(1, 2)

        ### SUPERGRID ###
        self.supergrid = QGridLayout()
        self.supergrid.addLayout( self.grid_top, 0, 0)
        self.supergrid.addLayout( self.grid_buttons, 1, 0)
        self.supergrid.addLayout( self.grid_bottom, 2, 0)

        # Set layout and window title
        self.setLayout( self.supergrid )
        self.setWindowTitle("Align to Active Brainstem Atlas - Main Page")

        # Update interactive windows
        self.updateFields()
        
        # Center the GUI
        self.center()
            
    def updateFields(self, update_dropdown=True):
        # Get dropdown selection
        dropdown_selection = self.cb.currentText()
        dropdown_selection_str = str(dropdown_selection.toUtf8())
        
        # Set stack-specific variables
        self.stack = dropdown_selection_str
        try:
            self.stain = stack_metadata[ self.stack ]['stain']
            self.detector_id = stain_to_metainfo[ self.stain.lower() ]['detector_id']
            self.img_version_1 = stain_to_metainfo[ self.stain.lower() ]['img_version_1']
            self.img_version_2 = stain_to_metainfo[ self.stain.lower() ]['img_version_1']
            # Update "stain" field to self.stack's stain
            self.e3.setText( self.stain )
            # Check the brains_info/STACK_progress.ini file for which step we're on
            self.curr_step = get_current_step_from_progress_ini( self.stack )
            # Disable all grid buttons except for the one corresponding to our current step
            self.format_grid_buttons()
            
            if update_dropdown:
                # Update the dropdown stack list in case there's a new stack
                # Recursion error if combobox callback activates this so it is behind an if statement
                self.updateStackDropdownMenu()
            
        # If there are no stacks/brains that have been started
        except KeyError:
            for grid_button in [self.b_setup, self.b_align, self.b_mask, self.b_crop, 
                            self.b_globalFit, self.b_localFit]:
                format_grid_button_cantStart( grid_button )
                
    def newDropdownSelection(self):
        self.updateFields( update_dropdown=False )
    
    def updateStackDropdownMenu(self):
        new_stacks = []
        if os.path.exists( BRAINS_INFO_DIR ):
            for brain_ini in os.listdir( BRAINS_INFO_DIR ):
                # Two kinds of brain_ini files: 'progress' and 'metadata'
                if 'progress' in brain_ini:
                    continue

                brain_name = os.path.splitext(brain_ini)[0].replace('_metadata', '')
                if brain_name in all_stacks:
                    continue
                # Add a brain to "new_stack" list if it is found and is not a part of "all_stacks"
                new_stacks.append( brain_name )
                
        if not new_stacks==[]:
            self.cb.clear( )
            self.cb.addItems( all_stacks + new_stacks )
        
    def format_grid_buttons(self):
        """
        Locates where you are in the pipeline by reading the brains_info/STACK_progress.ini
        
        Buttons corresponding to previous steps are marked as "completed", buttons corresponding
        to future steps are marked as "unpressable" and are grayed out.
        """
        curr_step = self.curr_step
        
        if 'setup' in curr_step:
            # Done-ish
            active_button = self.b_setup
        elif 'align' in curr_step:
            active_button = self.b_align
        elif 'mask' in curr_step:
            active_button = self.b_mask
        elif 'crop' in curr_step:
            active_button = self.b_crop
        elif 'fit_atlas_global' in curr_step:
            active_button = self.b_globalFit
        elif 'fit_atlas_local' in curr_step:
            active_button = self.b_localFit
        else:
            print(curr_step)
            
        passed_curr_step = False
        for grid_button in [self.b_setup, self.b_align, self.b_mask, self.b_crop, 
                            self.b_globalFit, self.b_localFit]:
            if not passed_curr_step and grid_button != active_button:
                format_grid_button_completed( grid_button )
            elif grid_button == active_button:
                passed_curr_step = True
                format_grid_button_initial(active_button)
            elif passed_curr_step and grid_button != active_button:
                format_grid_button_cantStart( grid_button )
                        
    def button_grid_push(self, button):
        """
        If any of the "grid" buttons are pressed, this is the callback function.
        
        In this case, "grid" buttons have a one-to_one correspondance to the steps in the pipeline.
        The completion of each step means you move onto the next one.
        """
        # 1) Setup
        # Runs preprocessing script 1 & 2
        if button == self.b_setup:
            if self.curr_step == '1-1_setup_metadata': 
                subprocess.call(['python','a_GUI_setup_newBrainMetadata.py'])
            else: 
                subprocess.call(['python','a_GUI_setup_main.py', self.stack])
                
        # 2) Align slices
        elif button == self.b_align:
            try:
                subprocess.call(['python','a_GUI_align_main.py', self.stack])
            except Exception as e:
                sys.stderr.write( e )
                
        # 3) Mask
        # Runs preprocessing script 3 & 4 & 5
        elif button == self.b_mask:
            try:
                subprocess.call(['python','a_GUI_mask_main.py', self.stack])
            except Exception as e:
                sys.stderr.write( e )
        
        # 4) Crop
        # Runs preprocessing script 
        elif button == self.b_crop:
            try:
                subprocess.call(['python','a_GUI_crop_main.py', self.stack])
            except Exception as e:
                sys.stderr.write( e )
        
        # 5) Fit atlas global
        elif button == self.b_globalFit:
            try:
                subprocess.call(['python','a_GUI_atlas_global_main.py', self.stack])
            except Exception as e:
                sys.stderr.write( e )
        
        # 6) Fit atlas local
        elif button == self.b_localFit:
            try:
                subprocess.call(['python','a_GUI_atlas_local_main.py', self.stack])
                
                #QMessageBox.about(self, "Popup Message", "The GUI window is not completely finished. A classifier will be chosen automatically and all local alignment scripts will be run. This will take a long time.")
                
                #detector = stain_to_metainfo[self.stain.lower()]["detector_id"]
                #subprocess.call(['python','a_script_processing.py', str(self.stack), str(self.stain), str(detector) ])
                
            except Exception as e:
                sys.stderr.write( str(e) )
        
        self.format_grid_buttons()
            
    def button_push(self, button):
        """
        Secondary button callback function
        """
        if button == self.b_exit:
            #close_main_gui( ex, reopen=False )
            #close_main_gui( app, reopen=False )
            sys.exit( app.exec_() )
        elif button==self.b_prevStep:
            subprocess.call(['python','a_GUI_prev_step.py', str(self.stack) ])
        
            # Update interactive windows
            self.updateFields()
        elif button == self.b_neuroglancer:
            pass
        elif button == self.b_datajoint:
            pass
        elif button == self.b_newBrain:
            subprocess.call(['python','a_GUI_setup_newBrainMetadata.py'])
        elif button == self.b_refresh:
            self.updateFields()
     
    def center(self):
        """
        This function simply aligns the GUI to the center of your monitor.
        """
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber( QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
            
    def mousePressEvent(self, event):
        self.updateFields()
        
    def mouseMoveEvent(self, event):
        self.updateFields()
        
    def closeEvent(self, event):
        #close_main_gui( app, reopen=True )
        sys.exit( app.exec_() )
        
def main():
    global app 
    app = QApplication( sys.argv )
    
    global ex
    ex = init_GUI()
    ex.show()
    sys.exit( app.exec_() )

if __name__ == '__main__':
    main()
