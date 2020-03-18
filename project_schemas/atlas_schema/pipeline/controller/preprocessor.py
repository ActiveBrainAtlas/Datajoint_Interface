"""
Working with OpenCV
It is possible that you may need to use an image created using skimage with OpenCV or vice versa. 
OpenCV image data can be accessed (without copying) in NumPy (and, thus, in scikit-image). 
OpenCV uses BGR (instead of scikit-image’s RGB) for color images, and its dtype is 
uint8 by default (See Image data types and what they mean). BGR stands for Blue Green Red.
"""

from sqlalchemy.orm.exc import NoResultFound
import os, sys, subprocess, time, datetime
import cv2 as cv
from skimage import io
from skimage.util import img_as_uint
import numpy as np
from .bioformats_utilities import get_czi_metadata, get_fullres_series_indices
from model.animal import Animal
from model.histology import Histology
from model.scan_run import ScanRun
from model.slide import Slide
from model.slide_czi_to_tif import SlideCziTif



DATA_ROOT = '/net/birdstore/Active_Atlas_Data/data_root/pipeline_data'
CZI = 'czi'
TIF = 'tif'
ROTATED = 'rotated'
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
            czi_files = sorted(os.listdir(self.CZI_FOLDER))
        except OSError as e:
            print(e)
            sys.exit()
        section_number = 1
        for i, czi_file in enumerate(czi_files):
            slide = Slide()
            slide.scan_run_id = scan_id
            slide.slide_physical_id = i
            slide.rescan_number = "1"
            slide.slide_status = 'Good'
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
                #j += 1
                scene_number = series.index( series_index )
                channels = range(metadata_dict[scene_number]['channels'])
                width = metadata_dict[series_index]['width']
                height = metadata_dict[series_index]['height']
                #print(metadata_dict[scene_number]['channels'])
                for channel in channels:                
                    newtif = os.path.splitext(czi_file)[0]
                    newtif = '{}_S{}_C{}.tif'.format(czi_file, j, channel)
                    newtif = newtif.replace('.czi','')
                    tif = SlideCziTif()
                    tif.slide_id = slide.id
                    tif.section_number = section_number
                    tif.scene_number = j 
                    tif.channel = channel
                    tif.file_name = newtif
                    tif.file_size = 0
                    tif.width = width
                    tif.height = height
                    tif.created = time.strftime('%Y-%m-%d %H:%M:%S')
                    print('{}\t{}\t{}\t{}\t{}\t{}'.format(newtif, tif.slide_id, tif.scene_number, tif.channel, width, height))
                    self.session.add(tif)
                section_number += 1

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
                input_tif = os.path.join(self.TIF_FOLDER, tif.file_name)
                if os.path.exists(input_tif):
                    tif.file_size = os.path.getsize(input_tif)
                    self.session.merge(tif)
        self.session.commit()
        
    def get_slide_status(self, slide, series):
        bad_slides = []
        if slide.scene_qc_1 is not None:
            bad_slides.append(series[0])
        if slide.scene_qc_2 is not None:
            bad_slides.append(series[1])
        if slide.scene_qc_3 is not None:
            bad_slides.append(series[2])
        if slide.scene_qc_4 is not None:
            bad_slides.append(series[3])
        if slide.scene_qc_5 is not None and len(series) > 4:
            bad_slides.append(series[4])
        if slide.scene_qc_6 is not None and len(series) > 5:
            bad_slides.append(series[5])
        return bad_slides
    
        
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
                
        slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).filter(Slide.processed==False).filter(Slide.slide_status=='Good').all()
        for slide in slides:
            start = time.time()
            czi_file = os.path.join(self.CZI_FOLDER, slide.file_name)
            metadata_dict = get_czi_metadata(czi_file)
            #print(metadata_dict)
            series = get_fullres_series_indices(metadata_dict)
            badslides = self.get_slide_status(slide,series)
            series = [i for i in series if i not in badslides]
            procs = []
            for j, series_index in enumerate(series):
                channels = range(metadata_dict[series_index]['channels'])
                for channel in channels:                
                    newtif = os.path.splitext(slide.file_name)[0]
                    newtif = '{}_S{}_C{}.tif'.format(slide.file_name, j, channel)
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
            print('No results found for prep_id: {}.'.format(self.prep_id))

        try: 
            histology = self.session.query(Histology).filter(Histology.prep_id == self.animal.prep_id).all()
        except (NoResultFound):
            print('No histology results found for prep_id: {}.'.format(self.prep_id))

        try: 
            scan_runs = self.session.query(ScanRun).filter(ScanRun.prep_id == self.animal.prep_id).all()
        except (NoResultFound):
            print('No scan run results found for prep_id: {}.'.format(self.prep_id))

        try:
            slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
        except (NoResultFound):
            print('No slides found for prep_id: {}.'.format(self.prep_id))

        try: 
            slides = self.session.query(Slide).filter(Slide.scan_run_id.in_(self.scan_ids)).all()
            slides_ids = [slide.id for slide in slides]
            tifs = self.session.query(SlideCziTif).filter(SlideCziTif.slide_id.in_(slides_ids))
            print('Found {} tifs'.format(tifs.count()))
        except (NoResultFound):
            print('No tifs found for prep_id: {}.'.format(self.prep_id))

def everything(img, rotation):
    scale = 1 / float(32)
    two_16 = 2**16
    img = np.rot90(img, rotation)
    img = np.fliplr(img)
    img = img[::int(1./scale), ::int(1./scale)]
    flat = img.flatten()
    hist,bins = np.histogram(flat,two_16)
    cdf = hist.cumsum() #cumulative distribution function
    cdf = two_16 * cdf / cdf[-1] #normalize
    #use linear interpolation of cdf to find new pixel values
    img_norm = np.interp(flat,bins[:-1],cdf)
    img_norm = np.reshape(img_norm, img.shape)
    img_norm = two_16 - img_norm
    return img_norm.astype('uint16')
                                                
            
            
def lognorm(img, limit):
    lxf = np.log(img + 0.005)
    lxf = np.where(lxf < 0, 0, lxf)
    xmin = min(lxf.flatten()) 
    xmax = max(lxf.flatten())
    return -lxf*limit/(xmax-xmin) + xmax*limit/(xmax-xmin) #log of data and stretch 0 to 255

def linnorm(img, limit):
    flat = img.flatten()
    hist,bins = np.histogram(flat,limit + 1)
    cdf = hist.cumsum() #cumulative distribution function
    cdf = limit * cdf / cdf[-1] #normalize
    #use linear interpolation of cdf to find new pixel values
    img_norm = np.interp(flat,bins[:-1],cdf)
    img_norm = np.reshape(img_norm, img.shape)
    img_norm = limit - img_norm
    return img_norm

def flip_rotate(prep_id, tif):
    io.use_plugin('tifffile')
    INPUT = os.path.join(DATA_ROOT, prep_id, TIF)
    OUTPUT = os.path.join(DATA_ROOT, prep_id, ROTATED)
    input_tif = os.path.join(INPUT, tif)
    output_tif = os.path.join(OUTPUT, tif)
    status = "Image rotated"
    
    try:
        img = io.imread(input_tif)
    except:
        return 'Bad file size'
        
    # convert to 8bit
    #img = (img/256).astype('uint8')
        
    try:
        img = np.rot90(img, 1)
    except:
        print('could not rotate',tif)
        
    try:
        img = np.fliplr(img)
    except:
        print('could not flip',tif)
        
    try:
        img = img_as_uint(img)
    except:
        print('could not convert to 16bit',tif)
    
    try:
        io.imsave(output_tif, img)
    except:
        print('Could not save {}'.format(output_tif))

    return " Flipped and rotated"    



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
        
    """
    scale = (1/float(32))
    try:        
        #img_tb = cv.resize(img, dim, interpolation = cv.INTER_AREA)
        img = img[::int(1./scale), ::int(1./scale)]
    except:
        return "Could not scale"
    
    two_16 = 2**16
    if '_C0' in input_tif:
        img = linnorm(img, two_16)
        status += " linear equalization on C0"
    else:
        img = lognorm(img, two_16)
        status += " log norm equalization on C1,2"    
    """
    img = everything(img, 1)
    base = os.path.splitext(tif)[0]
    output_png = os.path.join(OUTPUT, base + '.png')
    try:
        io.imsave(output_png, img, check_contrast=False)
    except:
        status += " Could not save"

    return " Thumbnail created"    

