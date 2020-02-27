from sqlalchemy.orm.exc import NoResultFound
from model.animal import Animal
from model.histology import Histology
from model.scan_run import ScanRun
from model.slide import Slide
from model.slide_czi_to_tif import SlideCziTif
import os, sys, subprocess, time
import cv2 as cv
import numpy as np
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
DEPTH8 = 'depth8'


class SlideProcessor(object):
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
        self.czi_files = [slide.file_name for slide in self.slides]
        self.slides_ids = []
        self.counter_stains = []
        self.session = session
        
        
    def insert_czi_data(self):
        
        scan_id = max(self.scan_ids)
        
        Slide.__table__.delete().where( Slide.scan_run_id.in_(self.scan_ids) )
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
            slide.rescan_number = 1
            slide.file_name = file
            slide.slide_physical_id = i
            slide.processed = False
            slide.file_size = os.path.getsize(os.path.join(INPUT, file))
            slide.processing_duration = 0
            slide.created = time.strftime('%Y-%m-%d %H:%M:%S')
            self.session.merge(slide)
        self.session.commit()

        
    def update_tif_data(self):
        
        #SlideCziTif.__table__.delete().where(Slide.scan_run_id == scan_id)
        #self.session.commit()
        
        INPUT = os.path.join(DATA_ROOT, self.brain, TIF)
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
            
        for slide in self.slides:
            for tif in slide.slidesCziTifs:
                tif.file_size = os.path.getsize(os.path.join(INPUT, tif.file_name))
                self.session.merge(tif)
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
            czi_file = os.path.join(INPUT, slide.file_name)
            metadata_dict = get_czi_metadata(czi_file)
            #print(metadata_dict)
            #print()
            series = get_fullres_series_indices(metadata_dict)
            #print(series)
            
            for j, series_index in enumerate(series):
                scene_number = series.index( series_index )
                channels = range(metadata_dict[scene_number]['channels'])
                #print(metadata_dict[scene_number]['channels'])
                for channel in channels:                
                    procs = []
                    newtif = os.path.splitext(slide.file_name)[0]
                    newtif = '{}_S{}_C{}.tif'.format(slide.file_name, scene_number, channel)
                    newtif = newtif.replace('.czi','')
                    tif_file = os.path.join(OUTPUT, newtif)
                
                    command = ['/usr/local/share/bftools/bfconvert', '-bigtiff', '-compression', 'LZW', '-separate', 
                              '-series', str(series_index), '-channel', str(channel), '-nooverwrite', czi_file, tif_file]
                    #cli = " ".join(command)
                    #print(cli)
                    proc = subprocess.Popen(command, shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
                    procs.append(proc)
                    tif = SlideCziTif()
                    tif.slide_id = slide.id
                    tif.scene_number = series_index 
                    tif.channel = channel
                    tif.file_name = newtif
                    tif.file_size = 0
                    tif.created = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.session.merge(tif)
                proc = procs[-1]
                proc.wait()
                print('Finished proc.')
            end = time.time()
            slide.processed  = True
            slide.processing_duration = end - start
            self.session.merge(slide)
            
        self.session.commit()
        self.update_tif_data()
        
            
                    
    def scale_tiff(self, channel):
        """
        Make downsampled images
        Add the ability to view each Tiff as a thumbnail in a table by clicking on name of Tiff file.
        """
        pass
    
    def depth8(self):
        """
        To counterstained sections - Channel 1
        Linear normalization
        Section-to-section
        Make, inspect and change Masks
        Adaptive normalization
        Gamma inversion (optional)
        """
        INPUT = os.path.join(DATA_ROOT, self.brain, TIF)
        OUTPUT = os.path.join(DATA_ROOT, self.brain, DEPTH8)
        self.slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids))
        self.slides_ids = [slide.id for slide in self.slides]
        print(self.scan_ids)
        print(self.slides_ids)
        tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(self.slides_ids))
        for tif in tifs:
            input_tif = os.path.join(INPUT, tif.file_name)
            output_tif = os.path.join(OUTPUT, tif.file_name)
            #command = ['/usr/bin/convert', '-depth', '8', input_tif, output_tif]
            #cli = " ".join(command)
            #print(cli)
            #proc = subprocess.Popen(command, shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
            #proc.wait()
            img16 = cv.imread(input_tif)
            img8 = (img16/256).astype('uint8')
            cv.imwrite(output_tif, img8)
            
        print('Finished processing tifs to depth 8.')
    
    def rotate_flip(self):
        """
        To counterstained sections - Channel 1
        Linear normalization
        Section-to-section
        Make, inspect and change Masks
        Adaptive normalization
        Gamma inversion (optional)
        """
        INPUT = os.path.join(DATA_ROOT, self.brain, DEPTH8)
        OUTPUT = os.path.join(DATA_ROOT, self.brain, ROTATED)
        self.slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
        self.slides_ids = [slide.id for slide in self.slides]
        tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(self.slides_ids)).all()
        for tif in tifs:
            input_tif = os.path.join(INPUT, tif.file_name)
            output_tif = os.path.join(OUTPUT, tif.file_name)
            #print(input_tif)
            
            img = cv.imread(input_tif, cv.IMREAD_ANYDEPTH)
            print(type(img))
            img = np.rot90(img, 3)
            img = np.flipud(img)
            cv.imwrite(output_tif, img)
            
        print('Finished proc.')
            
    def linear_norm_counterstain(self):
        """
        To counterstained sections - Channel 1
        Linear normalization
        Section-to-section
        Make, inspect and change Masks
        Adaptive normalization
        Gamma inversion (optional)
        """
        INPUT = os.path.join(DATA_ROOT, self.brain, TIF)
        OUTPUT = os.path.join(DATA_ROOT, self.brain, NORMALIZED)
        self.slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).filter(Slide.processed==True).all()
        self.slides_ids = [slide.id for slide in self.slides]
        self.counter_stains = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(self.slides_ids)).filter(SlideCziTif.channel==0).all()
        for counter_stain in self.counter_stains:
            print(counter_stain.file_name)
            input_tif = os.path.join(INPUT, counter_stain.file_name)
            output_tif = os.path.join(OUTPUT, counter_stain.file_name)
            command = ['/usr/bin/convert', '-normalize', '-depth', '8', input_tif, output_tif]
            #cli = " ".join(command)
            #print(cli)
            proc = subprocess.Popen(command, shell=False, stdin=None, stdout=None, stderr=None, close_fds=True)
            proc.wait()
            print('Finished proc.')
    
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

    def test_tables(self):
            try: 
                animal = self.session.query(Animal).filter(Animal.prep_id == self.animal.prep_id).one()
            except (NoResultFound):
                print('No results found for prep_id: {}.'.format(prep_id))
                
            try: 
                histology = self.session.query(Histology).filter(Histology.prep_id == self.animal.prep_id).all()
            except (NoResultFound):
                print('No histology results found for prep_id: {}.'.format(prep_id))
                
            try: 
                scan_runs = self.session.query(ScanRun).filter(ScanRun.prep_id == self.animal.prep_id).all()
            except (NoResultFound):
                print('No scan run results found for prep_id: {}.'.format(prep_id))
                
            try:
                self.slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
            except (NoResultFound):
                print('No slides found for prep_id: {}.'.format(prep_id))
            
            try: 
                self.slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
                self.slides_ids = [slide.id for slide in self.slides]
                tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(self.slides_ids))
                print('Found {} tifs'.format(tifs.count()))
            except (NoResultFound):
                print('No tifs found for prep_id: {}.'.format(prep_id))
            
