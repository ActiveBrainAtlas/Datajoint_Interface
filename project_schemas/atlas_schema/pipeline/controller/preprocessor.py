"""
Working with OpenCV
It is possible that you may need to use an image created using skimage with OpenCV or vice versa. 
OpenCV image data can be accessed (without copying) in NumPy (and, thus, in scikit-image). 
OpenCV uses BGR (instead of scikit-image’s RGB) for color images, and its dtype is 
uint8 by default (See Image data types and what they mean). BGR stands for Blue Green Red.
"""

from sqlalchemy.orm.exc import NoResultFound
import os, sys, subprocess, time, datetime
from matplotlib import pyplot as plt
from skimage import io
from skimage.util import img_as_uint
import numpy as np
from .bioformats_utilities import get_czi_metadata, get_fullres_series_indices
from model.animal import Animal
from model.histology import Histology as AlcHistology
from model.scan_run import ScanRun as AlcScanRun
from model.slide import Slide as AlcSlide
from model.slide_czi_to_tif import SlideCziTif as AlcSlideCziTif
from sql_setup import dj, database


DATA_ROOT = '/net/birdstore/Active_Atlas_Data/data_root/pipeline_data'
CZI = 'czi'
TIF = 'tif'
HIS = 'histogram'
ROTATED = 'rotated'
MASKED = 'masked'
NORMALIZED = 'normalized'
PRECOMPUTED = 'precomputed'
PREPS = 'preps'
THUMBNAIL = 'thumbnail'
schema = dj.schema(database)


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
        self.session.query(AlcSlide).filter(AlcSlide.scan_run_id.in_(self.scan_ids)).delete(synchronize_session=False)
        self.session.commit()
        
        try:
            czi_files = sorted(os.listdir(self.CZI_FOLDER))
        except OSError as e:
            print(e)
            sys.exit()
            
        section_number = 1
        #czi_files = ['DK43_slide060_2020_01_23__8024.czi']
        slide_counter = 0
        for i, czi_file in enumerate(czi_files):
            slide_counter += 1
            slide = AlcSlide()
            slide.scan_run_id = scan_id
            slide.slide_physical_id = slide_counter
            slide.rescan_number = "1"
            slide.slide_status = 'Good'
            slide.processed = False
            slide.file_size = os.path.getsize(os.path.join(self.CZI_FOLDER, czi_file))
            slide.file_name = czi_file
            slide.created = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(self.CZI_FOLDER, czi_file)))
            self.session.add(slide)
            self.session.flush()
            
            # Get metadata from the czi file
            czi_file_path = os.path.join(self.CZI_FOLDER, czi_file)
            metadata_dict = get_czi_metadata(czi_file_path)
            series = get_fullres_series_indices(metadata_dict)
            scene_counter = 0
            for j, series_index in enumerate(series):
                scene_counter += 1
                channels = range(metadata_dict[series_index]['channels'])
                channel_counter = 0
                width = metadata_dict[series_index]['width']
                height = metadata_dict[series_index]['height']
                for channel in channels:
                    channel_counter += 1
                    newtif = os.path.splitext(czi_file)[0]
                    newtif = '{}_S{}_C{}.tif'.format(czi_file, scene_counter, channel_counter)
                    newtif = newtif.replace('.czi','')
                    tif = AlcSlideCziTif()
                    tif.slide_id = slide.id
                    tif.section_number = section_number
                    tif.scene_number = scene_counter
                    tif.channel = channel_counter
                    tif.file_name = newtif
                    tif.file_size = 0
                    tif.active = 1
                    tif.width = width
                    tif.height = height
                    tif.channel_index = channel
                    tif.scene_index = series_index
                    tif.processing_duration = 0
                    tif.created = time.strftime('%Y-%m-%d %H:%M:%S')
                    print('{}\t{}\t{}\t{}\t{}\t{}'.format(newtif, tif.slide_id, tif.scene_number, tif.channel, width, height))
                    self.session.add(tif)
                section_number += 1

            self.session.commit()


    def compare_tif(self):
        INPUT = os.path.join(DATA_ROOT, self.brain, TIF)
        
        slides = self.session.query(AlcSlide).filter(AlcSlide.scan_run_id.in_(self.scan_ids))
        slide_ids = [slide.id for slide in slides]
        tifs = self.session.query(AlcSlideCziTif).filter(AlcSlideCziTif.slide_id.in_(slide_ids))
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
            print('No results found for prep_id: {}.'.format(animal.prep_id))

        try: 
            self.session.query(AlcHistology).filter(AlcHistology.prep_id == animal.prep_id).all()
        except (NoResultFound):
            print('No histology results found for prep_id: {}.'.format(animal.prep_id))

        try: 
            self.session.query(AlcScanRun).filter(AlcScanRun.prep_id == animal.prep_id).all()
        except (NoResultFound):
            print('No scan run results found for prep_id: {}.'.format(animal.prep_id))

        try:
            self.session.query(AlcSlide).filter(AlcSlide.scan_run_id.in_(self.scan_ids)).all()
        except (NoResultFound):
            print('No slides found for prep_id: {}.'.format(animal.prep_id))

        try: 
            slides = self.session.query(AlcSlide).filter(AlcSlide.scan_run_id.in_(self.scan_ids)).all()
            slides_ids = [slide.id for slide in slides]
            tifs = self.session.query(AlcSlideCziTif).filter(AlcSlideCziTif.slide_id.in_(slides_ids))
            print('Found {} tifs'.format(tifs.count()))
        except (NoResultFound):
            print('No tifs found for prep_id: {}.'.format(animal.prep_id))





# End of table definitions


def make_thumbnail(prep_id, file_name):
    io.use_plugin('tifffile')

    OUTPUT = os.path.join(DATA_ROOT, prep_id, THUMBNAIL)
    input_tif = os.path.join(DATA_ROOT, prep_id, TIF, file_name)

    try:
        img = io.imread(input_tif)
    except:
        return 0

    img = everything(img, 1)
    base = os.path.splitext(file_name)[0]
    output_png = os.path.join(OUTPUT, base + '.png')
    try:
        io.imsave(output_png, img, check_contrast=False)
        del img
    except:
        return 0

    return 1

def make_histogram(session, prep_id, file_id):
    tif = session.query(AlcSlideCziTif).filter(AlcSlideCziTif.id==file_id).one()
    HIS_FOLDER = os.path.join(DATA_ROOT, prep_id, HIS)
    TIF_FOLDER = os.path.join(DATA_ROOT, prep_id, TIF)
    input_tif = os.path.join(TIF_FOLDER, tif.file_name)
    base = os.path.splitext(tif.file_name)[0]
    output_png = os.path.join(HIS_FOLDER, base + '.png')
    try:
        img = io.imread(input_tif)
    except:
        return 0

    colors = {1:'b', 2:'r', 3:'g'}
    fig = plt.figure()
    plt.rcParams['figure.figsize'] = [10, 6]
    if img.shape[0] * img.shape[1] > 1000000000:
        scale = 1 / float(2)
        img = img[::int(1. / scale), ::int(1. / scale)]
    try:
        flat = img.flatten()
    except:
        return 0
    del img
    fmax = flat.max()
    plt.hist(flat, fmax, [0, fmax], color=colors[tif.channel])
    plt.style.use('ggplot')
    plt.yscale('log')
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('{} @16bit'.format(tif.file_name))
    fig.savefig(output_png, bbox_inches='tight')
    plt.close()
    del flat
    return 1


def make_tif(session, prep_id, file_id):
    CZI_FOLDER = os.path.join(DATA_ROOT, prep_id, CZI)
    TIF_FOLDER = os.path.join(DATA_ROOT, prep_id, TIF)
    start = time.time()
    tif = session.query(AlcSlideCziTif).filter(AlcSlideCziTif.id==file_id).one()
    slide = session.query(AlcSlide).filter(AlcSlide.id==tif.slide_id).one()
    czi_file = os.path.join(CZI_FOLDER, slide.file_name)
        
    tif_file = os.path.join(TIF_FOLDER, tif.file_name)
    command = ['/usr/local/share/bftools/bfconvert', '-bigtiff', '-compression', 'LZW', '-separate', 
                              '-series', str(tif.scene_index), '-channel', str(tif.channel_index), '-nooverwrite', czi_file, tif_file]
    #cli = " ".join(command)
    #command = ['touch', tif_file]
    subprocess.run(command)
    #print(cli)

    end = time.time()
    if os.path.exists(tif_file):
        tif.file_size = os.path.getsize(tif_file)

    tif.processing_duration = end - start
    session.merge(tif)
    session.commit()

    #session.commit()
    return 1


def everything(img, rotation):
    scale = 1 / float(32)
    two_16 = 2 ** 16
    img = np.rot90(img, rotation)
    img = np.fliplr(img)
    img = img[::int(1. / scale), ::int(1. / scale)]
    flat = img.flatten()
    hist, bins = np.histogram(flat, two_16)
    cdf = hist.cumsum()  # cumulative distribution function
    cdf = two_16 * cdf / cdf[-1]  # normalize
    # use linear interpolation of cdf to find new pixel values
    img_norm = np.interp(flat, bins[:-1], cdf)
    img_norm = np.reshape(img_norm, img.shape)
    img_norm = two_16 - img_norm
    return img_norm.astype('uint16')


def lognorm(img, limit):
    lxf = np.log(img + 0.005)
    lxf = np.where(lxf < 0, 0, lxf)
    xmin = min(lxf.flatten())
    xmax = max(lxf.flatten())
    return -lxf * limit / (xmax - xmin) + xmax * limit / (xmax - xmin)  # log of data and stretch 0 to 255


def linnorm(img, limit):
    flat = img.flatten()
    hist, bins = np.histogram(flat, limit + 1)
    cdf = hist.cumsum()  # cumulative distribution function
    cdf = limit * cdf / cdf[-1]  # normalize
    # use linear interpolation of cdf to find new pixel values
    img_norm = np.interp(flat, bins[:-1], cdf)
    img_norm = np.reshape(img_norm, img.shape)
    img_norm = limit - img_norm
    return img_norm


def flip_rotate(prep_id, tif):
    io.use_plugin('tifffile')
    INPUT = os.path.join(DATA_ROOT, prep_id, TIF)
    OUTPUT = os.path.join(DATA_ROOT, prep_id, ROTATED)
    input_tif = os.path.join(INPUT, tif)
    output_tif = os.path.join(OUTPUT, tif)

    try:
        img = io.imread(input_tif)
    except:
        return 'Bad file size'

    try:
        img = np.rot90(img, 1)
    except:
        print('could not rotate', tif)

    try:
        img = np.fliplr(img)
    except:
        print('could not flip', tif)

    try:
        img = img_as_uint(img)
    except:
        print('could not convert to 16bit', tif)

    try:
        io.imsave(output_tif, img)
    except:
        print('Could not save {}'.format(output_tif))

    return " Flipped and rotated"

