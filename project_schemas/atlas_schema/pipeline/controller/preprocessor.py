from sqlalchemy.orm.exc import NoResultFound
import os, sys, subprocess, time, datetime
import cv2 as cv
from skimage import io
import numpy as np
from .bioformats_utilities import get_czi_metadata, get_fullres_series_indices
from model.animal import Animal
from model.histology import Histology
from model.scan_run import ScanRun
from model.slide import Slide
from model.slide_czi_to_tif import SlideCziTif
from prompt_toolkit import output



DATA_ROOT = '/net/birdstore/Active_Atlas_Data/data_root/pipeline_data'
CZI = 'czi'
TIF = 'tif'
MASKED = 'masked'
NORMALIZED = 'normalized'
PRECOMPUTED = 'precomputed'
PREPS = 'preps'
THUMBNAIL = 'thumbnail'


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
        
        
    def process_czi_dir(self):
        
        scan_id = max(self.scan_ids)
        print(self.scan_ids)
        #self.session.(Slide).__table__.delete().where( Slide.scan_run_id.in_(self.scan_ids) )
        self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).delete(synchronize_session=False)
        self.session.commit()
        
        INPUT = os.path.join(DATA_ROOT, self.brain, CZI)
        try:
            os.listdir(INPUT)
        except OSError as e:
            print(e)
            sys.exit()
        try:
            czi_files = os.listdir(INPUT)
        except OSError as e:
            print(e)
            sys.exit()
            
        for i, czi_file in enumerate(czi_files):
            slide = Slide()
            slide.scan_run_id = scan_id
            slide.slide_physical_id = i
            slide.rescan_number = ''
            slide.scene_qc_1 = ''
            slide.scene_qc_2 = ''
            slide.scene_qc_3 = ''
            slide.scene_qc_4 = ''
            slide.scene_qc_5 = ''
            slide.scene_qc_6 = ''            
            slide.processed = False
            slide.processing_duration = 0
            slide.file_size = os.path.getsize(os.path.join(INPUT, czi_file))
            slide.file_name = czi_file
            dt = os.path.getmtime(os.path.join(INPUT, czi_file))
            dt = datetime.datetime.fromtimestamp(dt)
            slide.created = dt
            self.session.add(slide)
            self.session.flush()
            czi_file_path = os.path.join(INPUT, czi_file)
            metadata_dict = get_czi_metadata(czi_file_path)
            series = get_fullres_series_indices(metadata_dict)
            #print(series)            
            for j, series_index in enumerate(series):
                scene_number = series.index( series_index )
                channels = range(metadata_dict[scene_number]['channels'])
                width = metadata_dict[series_index]['width']
                height = metadata_dict[series_index]['height']
                #print(metadata_dict[scene_number]['channels'])
                for channel in channels:                
                    newtif = os.path.splitext(czi_file)[0]
                    newtif = '{}_S{}_C{}.tif'.format(czi_file, scene_number, channel)
                    newtif = newtif.replace('.czi','')
                    tif = SlideCziTif()
                    tif.slide_id = slide.id
                    tif.scene_number = series_index 
                    tif.channel = channel
                    tif.file_name = newtif
                    tif.file_size = 0
                    tif.width = width
                    tif.height = height
                    tif.created = time.strftime('%Y-%m-%d %H:%M:%S')
                    print('{}\t{}\t{}\t{}\t{}\t{}'.format(newtif, tif.slide_id, tif.scene_number, tif.channel, width, height))
                    self.session.add(tif)
            
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
            for tif in slide.slide_czi_tifs:
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
                
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).filter(Slide.processed==False).all()
                
        for slide in slides:
            start = time.time()
            czi_file = os.path.join(INPUT, slide.file_name)
            metadata_dict = get_czi_metadata(czi_file)
            #print(metadata_dict)
            series = get_fullres_series_indices(metadata_dict)
            #print(series)
            
            procs = []
            for j, series_index in enumerate(series):
                scene_number = series.index( series_index )
                channels = range(metadata_dict[scene_number]['channels'])
                #print(metadata_dict[scene_number]['channels'])
                for channel in channels:                
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
            proc = procs[-1]
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
    
    def depth8_rotate_flip(self):
        """
        To counterstained sections - Channel 1
        Linear normalization
        Section-to-section
        Make, inspect and change Masks
        Adaptive normalization
        Gamma inversion (optional)
        """
        INPUT = os.path.join(DATA_ROOT, self.brain, TIF)
        OUTPUT = os.path.join(DATA_ROOT, self.brain, DEPTH8_FLIP_ROTATE)
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids))
        slide_ids = [slide.id for slide in slides]
        print(self.scan_ids)
        print(slide_ids)
        tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(slide_ids))
        for tif in tifs:
            input_tif = os.path.join(INPUT, tif.file_name)
            output_tif = os.path.join(OUTPUT, tif.file_name)
            print(input_tif)
            img16 = io.imread(input_tif)
            img8 = (img16/256).astype('uint8')
            img = np.rot90(img8, 3)
            img = np.flipud(img)
            io.imsave(output_tif, img, check_contrast=False)
            
        print('Finished processing tifs to depth 8.')

    def lognorm(self, img):
        img = (img/256).astype('uint8')
        lxf = np.log(img + 0.005)
        lxf = np.where(lxf < 0, 0, lxf)
        xmin = min(lxf.flatten()) 
        xmax = max(lxf.flatten())
        return -lxf*255/(xmax-xmin) + xmax*255/(xmax-xmin) #log of data and stretch 0 to 255
    
    def linnorm(self, img):
        img = (img/256).astype('uint8')
        flat = img.flatten()
        hist,bins = np.histogram(flat,256)
        cdf = hist.cumsum() #cumulative distribution function
        cdf = 255 * cdf / cdf[-1] #normalize
        #use linear interpolation of cdf to find new pixel values
        img_norm = np.interp(flat,bins[:-1],cdf)
        img_norm = np.reshape(img_norm, red.shape)
        img_norm = 255 - img_norm
        return img_norm
            
    def norm_file(self):
        """
        To counterstained sections - Channel 1
        Linear normalization
        Section-to-section
        Make, inspect and change Masks
        Adaptive normalization
        Gamma inversion (optional)
        """
        io.use_plugin('tifffile')
        INPUT = os.path.join(DATA_ROOT, self.brain, TIF)
        OUTPUT = os.path.join(DATA_ROOT, self.brain, NORMALIZED)
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids))
        slide_ids = [slide.id for slide in slides]
        print(self.scan_ids)
        print(slide_ids)
        tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(slide_ids))
        for tif in tifs:
            input_tif = os.path.join(INPUT, tif.file_name)
            print('working on',input_tif)
            output_tif = os.path.join(OUTPUT, tif.file_name)

            img = io.imread(input_tif)
            if '_C0_' in input_tif:
                img = self.linnorm(img)
            else:
                img = self.lognorm(img)
            io.imsave(output_tif, img.astype('uint8'), check_contrast=False)
            #cv.imwrite(output_tif, img)
    
    def scale(self):
        INPUT = os.path.join(DATA_ROOT, self.brain, NORMALIZED)
        OUTPUT = os.path.join(DATA_ROOT, self.brain, SCALED)
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids))
        slide_ids = [slide.id for slide in slides]
        print(self.scan_ids)
        print(slide_ids)
        tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(slide_ids))
        scale_percent = 1 / float(32) # percent of original size
        for tif in tifs:
            input_tif = os.path.join(INPUT, tif.file_name)
            print('working on',input_tif)
            output_tif = os.path.join(OUTPUT, tif.file_name)
            img = io.imread(input_tif)
            
            
            width = int(img.shape[1] * scale_percent)
            height = int(img.shape[0] * scale_percent)
            dim = (width, height)
            # resize image
            xf = cv.resize(img, dim, interpolation = cv.INTER_AREA)
            #io.imsave(output_tif, xf, check_contrast=False)
            cv.imwrite(output_tif, xf)
    
    def make_thumbnails(self):
        INPUT = os.path.join(DATA_ROOT, self.brain, SCALED)
        OUTPUT = os.path.join(DATA_ROOT, self.brain, THUMBNAIL)
        if not os.path.exists(OUTPUT):
            os.makedirs(OUTPUT)
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids))
        slide_ids = [slide.id for slide in slides]
        tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(slide_ids))
        for tif in tifs:
            input_tif = os.path.join(INPUT, tif.file_name)
            img = io.imread(input_tif)
            base = os.path.splitext(tif.file_name)[0]
            output_png = os.path.join(OUTPUT, base + '.png')
            cv.imwrite(output_png, img)
    
    def compare(self):
        INPUT = os.path.join(DATA_ROOT, self.brain, TIF)
        
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids))
        slide_ids = [slide.id for slide in slides]
        tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(slide_ids))
        for tif in tifs:
            input_tif = os.path.join(INPUT, tif.file_name)
            img = io.imread(input_tif)
            print(img.shape)
            print(tif.width, tif.height)
            if img.shape[3] != tif.height or img.shape[4] != tif.width:
                print(f'The information about {tif.file_name} is inconsistent')

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
            
