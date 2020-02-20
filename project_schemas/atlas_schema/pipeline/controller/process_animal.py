from model.slide import Slide
import os, sys, subprocess
from .a_bioformats_utilities import get_czi_metadata, get_fullres_series_indices


DATA_ROOT = '/net/birdstore/Active_Atlas_Data/data_root/pipeline_data'
CZI = 'czi'
TIF = 'tif'
INVERTED = 'inverted'
MASKED = 'masked'
NORMALIZED = 'normalized'
PRECOMPUTED = 'precomputed'
PREPS = 'preps'
ROTATED = 'rotated'
SCALED = 'scaled'


class SlidesProcessor(object):
    """ Create a class for processing the pipeline,
    """

    def __init__(self, animal, session):
        """ setup the attributes for the SlidesProcessor class
            Args:
                animal: object of animal to process
                session: sql session to run queries
        """
        self.brain = animal.prep_id
        self.animal = animal
        self.scan_ids = [scan.id for scan in self.animal.scan_runs]
        self.slides = session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
        self.czi_files = [slide.slides_path for slide in self.slides]
        self.session = session
        
        
    def insert_czi_data(self):
        
        scan_id = max(self.scan_ids)
        
        stmt = Slide.__table__.delete().where(Slide.scan_run_id == scan_id)
        self.session.commit()
        
        INPUT = os.path.join(DATA_ROOT, self.brain, CZI)
        try:
            os.listdir(INPUT)
        except OSError as e:
            print(e)
            sys.exit()
        try:
            files = os.listdir(INPUT)
        except OSError as e:
            print(e)
            sys.exit()
            
        for i, file in enumerate(files):
            slide = Slide()
            slide.scan_run_id = max(self.scan_ids)
            slide.slides_path = file
            slide.slide_physical_id = i
            self.session.merge(slide)
        self.session.commit()
        
    def process_czi(self):
        INPUT = os.path.join(DATA_ROOT, self.brain, CZI)
        OUTPUT = os.path.join(DATA_ROOT, self.brain, TIF)
        try:
            files_in_dir = os.listdir(INPUT)
        except OSError as e:
            print(e)
            sys.exit()
        try:
            os.listdir(INPUT)
        except OSError as e:
            print(e)
            sys.exit()
        try:
            os.listdir(OUTPUT)
        except OSError as e:
            print(e)
            sys.exit()
        
        if len(files_in_dir) != len(self.czi_files):
            self.insert_czi_data()
        
        
        
        channels = ['0','1','2']
        self.czi_files = ['DK43_slide001_2020_01_27__8081.czi']
        for file in self.czi_files:
            czi_file = os.path.join(INPUT, file)
            metadata_dict = get_czi_metadata(czi_file)
            #print(metadata_dict)
            #print()
            fullres_series_indices = get_fullres_series_indices(metadata_dict)
            print('fullres_series_indices', fullres_series_indices)
            for ii, series_index in enumerate(fullres_series_indices):
                iterative_section_num = fullres_series_indices.index( series_index )
                for channel in range(metadata_dict[iterative_section_num]['channels']):                
                    procs = []
                    newtif = os.path.splitext(file)[0]
                    newtif = '{}_S{}_C{}.tif'.format(file, iterative_section_num, channel)
                    newtif = newtif.replace('.czi','')
                    tif_file = os.path.join(OUTPUT, newtif)
                
                    command = ['/usr/local/share/bftools/bfconvert', '-bigtiff', '-compression', 'LZW', '-separate', 
                              '-series', str(iterative_section_num), '-channel', str(channel), czi_file, tif_file]
                    cli = " ".join(command)
                    print(cli)
                
                    subprocess.call(command)
                    proc = subprocess.Popen(command, shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
                    procs.append(proc)
                proc = procs[-1]
                proc.wait()
                print('Waiting for proc.')
            
                    
    def process_tiff(self, channel):
        pass
    
    def rotate_tiff(self):
        pass
    
    def normalize_tiff(self):
        pass
    
    def align_tiff(self):
        pass
    
    def precompute_tiffs(self):
        pass