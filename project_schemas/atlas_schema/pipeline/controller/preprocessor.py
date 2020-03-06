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
        self.animal = animal
        self.session = session
        self.scan_ids = [scan.id for scan in self.animal.scan_runs]
                
        self.CZI_FOLDER = os.path.join(DATA_ROOT, self.animal.prep_id, CZI)
        self.TIF_FOLDER = os.path.join(DATA_ROOT, self.animal.prep_id, TIF)
        
        
    def process_czi_dir(self):
        scan_id = max(self.scan_ids)
        self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).delete(synchronize_session=False)
        self.session.commit()
        
        try:
            czi_files = os.listdir(self.CZI_FOLDER)
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
            slide.file_size = os.path.getsize(os.path.join(self.CZI_FOLDER, czi_file))
            slide.file_name = czi_file
            slide.created = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(self.CZI_FOLDER, czi_file)))
            self.session.add(slide)
            self.session.flush()
            
            # Get metadata from the czi file
            czi_file_path = os.path.join(self.CZI_FOLDER, czi_file)
            metadata_dict = get_czi_metadata(czi_file_path)
            series = get_fullres_series_indices(metadata_dict)
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
        
        try:
            files = os.listdir(self.TIF_FOLDER)
        except OSError as e:
            print(e)
            sys.exit()
            
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
        for slide in slides:
            for tif in slide.slide_czi_tifs:
                tif.file_size = os.path.getsize(os.path.join(self.TIF_FOLDER, tif.file_name))
                self.session.merge(tif)
        self.session.commit()
        
    def process_czi(self):
        """
        CZI to Tiff - LZW compression. Controls are about the same size Tiff as CZI (factor of 1 or 2). 
        Add feedback to user after Big Table is populated.
        """
        try:
            files_in_dir = os.listdir(self.CZI_FOLDER)
        except OSError as e:
            print(e)
            sys.exit()
                
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).filter(Slide.processed==False).all()
        for slide in slides:
            start = time.time()
            czi_file = os.path.join(self.CZI_FOLDER, slide.file_name)
            metadata_dict = get_czi_metadata(czi_file)
            series = get_fullres_series_indices(metadata_dict)
            
            procs = []
            for j, series_index in enumerate(series):
                scene_number = series.index( series_index )
                channels = range(metadata_dict[scene_number]['channels'])
                for channel in channels:                
                    newtif = os.path.splitext(slide.file_name)[0]
                    newtif = '{}_S{}_C{}.tif'.format(slide.file_name, scene_number, channel)
                    newtif = newtif.replace('.czi','')
                    tif_file = os.path.join(self.TIF_FOLDER, newtif)
                
                    command = ['/usr/local/share/bftools/bfconvert', '-bigtiff', '-compression', 'LZW', '-separate', 
                              '-series', str(series_index), '-channel', str(channel), '-nooverwrite', czi_file, tif_file]
                    cli = " ".join(command)
                    print(cli)
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

    def compare_tif(self):
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
            slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
        except (NoResultFound):
            print('No slides found for prep_id: {}.'.format(prep_id))

        try: 
            slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
            slides_ids = [slide.id for slide in slides]
            tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(slides_ids))
            print('Found {} tifs'.format(tifs.count()))
        except (NoResultFound):
            print('No tifs found for prep_id: {}.'.format(prep_id))

def lognorm(img):
    lxf = np.log(img + 0.005)
    lxf = np.where(lxf < 0, 0, lxf)
    xmin = min(lxf.flatten()) 
    xmax = max(lxf.flatten())
    return -lxf*255/(xmax-xmin) + xmax*255/(xmax-xmin) #log of data and stretch 0 to 255

def linnorm(img):
    flat = img.flatten()
    hist,bins = np.histogram(flat,256)
    cdf = hist.cumsum() #cumulative distribution function
    cdf = 255 * cdf / cdf[-1] #normalize
    #use linear interpolation of cdf to find new pixel values
    img_norm = np.interp(flat,bins[:-1],cdf)
    img_norm = np.reshape(img_norm, img.shape)
    img_norm = 255 - img_norm
    return img_norm

def make_thumbnail(prep_id, tif):
    io.use_plugin('tifffile')
    INPUT = os.path.join(DATA_ROOT, prep_id, TIF)
    OUTPUT = os.path.join(DATA_ROOT, prep_id, THUMBNAIL)
    input_tif = os.path.join(INPUT, tif)
    output_tif = os.path.join(OUTPUT, tif)
    status = "Thumbnail created"
    
    try:
        img = io.imread(input_tif)
    except:
        return 'Bad file size'
        
    # convert to 8bit
    img = (img/256).astype('uint8')
    img = np.rot90(img, 1)
    img = np.fliplr(img)
    scale = (1/float(32))
    try:        
        #img_tb = cv.resize(img, dim, interpolation = cv.INTER_AREA)
        img = img[::int(1./scale), ::int(1./scale)]
    except:
        return "Could not scale"
    
    if '_C0' in input_tif:
        img = linnorm(img)
        status += " linear equalization on C0"
    else:
        img = lognorm(img)
        status += " log norm equalization on C1,2"
    #io.imsave(output_tif, img.astype('uint8'), check_contrast=False)
    #scale = 1 / float(32) # percent of original size
    #width = int(img.shape[1] * scale)
    #height = int(img.shape[0] * scale)
    #dim = (width, height)
    
        
    base = os.path.splitext(tif)[0]
    output_png = os.path.join(OUTPUT, base + '.png')
    try:
        io.imsave(output_png, img, check_contrast=False)
    except:
        print('Could not save {}'.format(output_png))

    return " Thumbnail created"    

def thumbnail(prep_id, tif):
    INPUT = os.path.join(DATA_ROOT, prep_id, NORMALIZED)
    OUTPUT = os.path.join(DATA_ROOT, prep_id, THUMBNAIL)
    scale = 1 / float(32) # percent of original size
    input_tif = os.path.join(INPUT, tif)
    try:
        img = io.imread(input_tif)
    except:
        return
        
    width = int(img.shape[1] * scale)
    height = int(img.shape[0] * scale)
    dim = (width, height)
    
    try:        
        img_tb = cv.resize(img, dim, interpolation = cv.INTER_AREA)
        #img_tb = img[::int(1./scale), ::int(1./scale)]
    except:
        return
        
    base = os.path.splitext(tif)[0]
    output_png = os.path.join(OUTPUT, base + '.png')
    #print('output png', base)
    try:
        io.imsave(output_png, img_tb, check_contrast=False)
    except:
        print('Could not save {}'.format(output_png))

    return " Thumbnail created"