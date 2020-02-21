from model.slide import Slide
import os, sys, subprocess, time
from .bioformats_utilities import get_czi_metadata, get_fullres_series_indices


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
            slide.processed = False
            slide.file_size = os.path.getsize(os.path.join(INPUT, file))
            self.session.merge(slide)
        self.session.commit()
        
    def process_czi(self):
        """
        CZI to Tiff - LZW compression. Controls are about the same size Tiff as CZI (factor of 1 or 2). 
        Add feedback to user after Big Table is populated.
        """
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
                
        self.slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).filter(Slide.processed==False).all()
                
        for slide in self.slides:
            start = time.time()
            czi_file = os.path.join(INPUT, slide.slides_path)
            metadata_dict = get_czi_metadata(czi_file)
            #print(metadata_dict)
            #print()
            series = get_fullres_series_indices(metadata_dict)
            for j, series_index in enumerate(series):
                iterative_section_num = series.index( series_index )
                for channel in range(metadata_dict[iterative_section_num]['channels']):                
                    procs = []
                    newtif = os.path.splitext(slide.slides_path)[0]
                    newtif = '{}_S{}_C{}.tif'.format(slide.slides_path, iterative_section_num, channel)
                    newtif = newtif.replace('.czi','')
                    tif_file = os.path.join(OUTPUT, newtif)
                
                    command = ['/usr/local/share/bftools/bfconvert', '-bigtiff', '-compression', 'LZW', '-separate', 
                              '-series', str(series_index), '-channel', str(channel), '-nooverwrite', czi_file, tif_file]
                    #cli = " ".join(command)
                    #print(cli)
                    proc = subprocess.Popen(command, shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
                    procs.append(proc)
            proc = procs[0]
            proc.wait()
            print('Finished proc.')
            end = time.time()
            slide.processed  = True
            slide.processing_duration = end - start
            self.session.merge(slide)
        self.session.commit()
            
                    
    def scale_tiff(self, channel):
        """
        Make downsampled images
        Add the ability to view each Tiff as a thumbnail in a table by clicking on name of Tiff file.
        """
        pass
    
    def process_counterstatin(self):
        """
        To counterstained sections - Channel 1
        Linear normalization
        Section-to-section
        Make, inspect and change Masks
        Adaptive normalization
        Gamma inversion (optional)
        """
        pass
    
    def process_other_channels(self):
        """
        To labeled sections - Channel 2,3,4
        Set intensity values < min to 0.5 and to > max to 0.5.
        Take logarithm
        Linear Stretch from 0 to 255
        """
        pass
    

    def precompute_tiffs(self):
        """
        Get tiffs ready for neuroglancer
        """
        pass