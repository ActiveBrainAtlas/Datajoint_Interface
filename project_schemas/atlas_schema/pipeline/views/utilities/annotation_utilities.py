import sys
import os
from collections import defaultdict

import numpy as np
import pandas as pd
from skimage.measure import grid_points_in_poly
from skimage.measure import find_contours
from shapely.geometry import LinearRing

from utilities2015 import crop_and_pad_volume, deprecated, volume_origin_to_bbox
from metadata import (all_landmark_names_unsided,
                      convert_name_to_unsided, convert_to_left_name, convert_to_right_name,
                      convert_to_unsided_label, convert_resolution_string_to_voxel_size, 
                      section_range_lookup,
                      singular_structures)
from data_manager_v2 import CoordinatesConverter, DataManager, metadata_cache



@deprecated
def get_structure_contours_from_structure_volumes(volumes, stack, sections, resolution, level=.5, sample_every=1):
    """

    TODO: replace all use of this function by `get_structure_contours_from_structure_volumes_v4`.

    Re-section atlas volumes and obtain structure contours on each section.
    Resolution of output contours are in volume resolution.

    Args:
        volumes (dict of (3D array, 3-tuple)): {structure: (volume, origin_wrt_wholebrain)}. volume is a 3d array of probability values.
        sections (list of int):
        resolution (int): resolution of input volumes.
        level (float): the cut-off probability at which surfaces are generated from probabilistic volumes. Default is 0.5.

    Returns:
        dict {int: {str: (n,2)-ndarray}}: dict of {section: {name_s: contour vertices}}. The vertex coordinates are wrt wholebrain and in volume resolution.
    """

    from collections import defaultdict

    # xmin_vol_f, ymin_vol_f, zmin_vol_f = volume_origin

    structure_contours = defaultdict(dict)

    for sec in sections:
        sys.stderr.write('Computing structure contours for section %d...\n' % sec)
        for name_s, (vol, origin_wrt_wholebrain_volResol) in volumes.iteritems():

            z = int(DataManager.convert_section_to_z(sec=sec, resolution=resolution, mid=True, stack=stack)) - origin_wrt_wholebrain_volResol[2]
            z = int(np.floor(z))
            if z < 0 or z >= vol.shape[-1]:
                continue

            if np.count_nonzero(vol[..., z]) == 0:
                continue
            sys.stderr.write('Probability mass detected on section %d...\n' % sec)

            cnts_rowcol = find_contours(vol[..., z], level=level)

            if len(cnts_rowcol) == 0:
                sys.stderr.write('Some probability mass of %s are on section %d but no contour is extracted at level=%.2f.\n' % (name_s, sec, level))
            else:
                if len(cnts_rowcol) > 1:
                    sys.stderr.write('%d contours (%s) of %s is extracted at level=%.2f on section %d. Keep only the longest.\n' % (len(cnts_rowcol), map(len, cnts_rowcol), name_s, level, sec))

                best_cnt = cnts_rowcol[np.argmax(map(len, cnts_rowcol))]

                # Address contours with identical first point and last point - remove last point
                if all(np.array(best_cnt[0]) == np.array(best_cnt[-1])):
                    # sys.stderr.write("Detected contour with identical first point and last point. section %d, %s, len %d\n" % (sec, sided_name, len(contour)))
                    best_cnt = best_cnt[:-1]

                contours_wrt_wholebrain_volResol = best_cnt[:, ::-1][::sample_every] + origin_wrt_wholebrain_volResol[:2]
                structure_contours[sec][name_s] = contours_wrt_wholebrain_volResol

    return structure_contours

@deprecated
def get_structure_contours_from_aligned_atlas(volumes, volume_origin, stack, sections, downsample_factor=32, level=.5,
                                              sample_every=1, first_sec=1):
    """
    TODO: replace all use of this function by `get_structure_contours_from_structure_volumes_v4`.

    Re-section atlas volumes and obtain structure contours on each section.

    Args:
        volumes (dict of 3D ndarrays of float): {structure: volume}. volume is a 3d array of probability values.
        volume_origin (tuple): (xmin_vol_f, ymin_vol_f, zmin_vol_f) relative to cropped image volume.
        sections (list of int):
        downsample_factor (int): the downscale factor of input volumes. Output contours are in original resolution.
        first_sec (int): the first section that the beginning of the input volume is at. Default is 1.
        level (float): the cut-off probability at which surfaces are generated from probabilistic volumes. Default is 0.5.

    Returns:
        dict {int: {str: (n,2)-ndarray}}: dict of {section: {name_s: contour vertices}}. The vertex coordinates are relative to cropped image volume and in lossless resolution.
    """

    # from metadata import XY_PIXEL_DISTANCE_LOSSLESS, SECTION_THICKNESS
    from collections import defaultdict

    # estimate mapping between z and section
    # xy_pixel_distance_downsampled = XY_PIXEL_DISTANCE_LOSSLESS * downsample_factor
    # voxel_z_size = SECTION_THICKNESS / xy_pixel_distance_downsampled

    xmin_vol_f, ymin_vol_f, zmin_vol_f = volume_origin

    structure_contours = defaultdict(dict)

    # Multiprocess is not advisable here because volumes must be duplicated across processes which is very RAM heavy.

#     def compute_contours_one_section(sec):
#         sys.stderr.write('Computing structure contours for section %d...\n' % sec)
#         z = int(np.round(voxel_z_size * (sec - 1) - zmin_vol_f))
#         contours_one_section = {}
#         # Find moving volume annotation contours
#         for name_s, vol in volumes.iteritems():
#             cnts = find_contours(vol[..., z], level=level) # rows, cols
#             for cnt in cnts:
#                 # r,c to x,y
#                 contours_one_section[name_s] = cnt[:,::-1] + (xmin_vol_f, ymin_vol_f)
#         return contours_one_section

#     pool = Pool(NUM_CORES/2)
#     structuer_contours = dict(zip(sections, pool.map(compute_contours_one_section, sections)))
#     pool.close()
#     pool.join()

    for sec in sections:
        sys.stderr.write('Computing structure contours for section %d...\n' % sec)
        # z = int(np.round(voxel_z_size * (sec - 1) - zmin_vol_f))
        z = int(DataManager.convert_section_to_z(sec=sec, downsample=downsample_factor, first_sec=first_sec, mid=True, stack=stack)) - zmin_vol_f
        for name_s, vol in volumes.iteritems():
            if np.count_nonzero(vol[..., z]) == 0:
                continue
            sys.stderr.write('Probability mass detected on section %d...\n' % sec)

            cnts_rowcol = find_contours(vol[..., z], level=level)

            if len(cnts_rowcol) == 0:
                sys.stderr.write('Some probability mass of %s are on section %d but no contour is extracted at level=%.2f.\n' % (name_s, sec, level))
            else:
                if len(cnts_rowcol) > 1:
                    sys.stderr.write('%d contours (%s) of %s is extracted at level=%.2f on section %d. Keep only the longest.\n' % (len(cnts_rowcol), map(len, cnts_rowcol), name_s, level, sec))

                best_cnt = cnts_rowcol[np.argmax(map(len, cnts_rowcol))]

                # Address contours with identical first point and last point - remove last point
                if all(np.array(best_cnt[0]) == np.array(best_cnt[-1])):
                    # sys.stderr.write("Detected contour with identical first point and last point. section %d, %s, len %d\n" % (sec, sided_name, len(contour)))
                    best_cnt = best_cnt[:-1]

                contours_on_cropped_tb = best_cnt[:, ::-1][::sample_every] + (xmin_vol_f, ymin_vol_f)
                structure_contours[sec][name_s] = contours_on_cropped_tb * downsample_factor

    return structure_contours

def annotation_volume_to_score_volume(ann_vol, label_to_structure):
    """
    Convert an interger-valued annotation volume to a set of probability-valued score volumes.

    Args:
        ann_vol (3D array of int): the annotation volume in which a voxel is an integer indicating the structure class

    Returns:
        dict of 3D array of float: {structure name: volume}. Each voxel is a probability vector, where exactly one entry is 1.
    """

    all_indices = set(np.unique(ann_vol)) - {0}
    volume = {label_to_structure[i]: np.zeros_like(ann_vol, dtype=np.float16) for i in all_indices}
    for i in all_indices:
        mask = ann_vol == i
        volume[label_to_structure[i]][mask] = 1.
        del mask
    return volume


def contours_to_mask(contours, img_shape):
    """
    img_shape: h,w
    """

    final_masks = []

    for cnt in contours:

        bg = np.zeros(img_shape, bool)
        xys = points_inside_contour(cnt.astype(np.int))
        bg[np.minimum(xys[:,1], bg.shape[0]-1), np.minimum(xys[:,0], bg.shape[1]-1)] = 1

        final_masks.append(bg)

    final_mask = np.any(final_masks, axis=0)
    return final_mask

def get_surround_volume_v3(volume, distance=5, wall_level=0, prob=False, return_origin_instead_of_bbox=True, padding=5):
    """
    Return the volume with voxels surrounding the ``active" voxels in the input volume set to 1 (prob=False) or 1 - vol (prob=True)

    Args:
        volume: (vol, origin)
        wall_level (float): voxels with value above this level are regarded as active.
        distance (int): surrounding voxels are closer than distance (in unit of voxel) from any active voxels.
        prob (bool): if True, surround voxels are assigned 1 - voxel value; if False, surround voxels are assigned 1.
        padding (int): extra zero-padding, in unit of voxels.

    Returns:
        (surround_volume, surround_volume_origin)
    """
    from scipy.ndimage.morphology import distance_transform_edt
    distance = int(np.round(distance))

    # Identify the bounding box for the surrouding area.

    vol, origin = volume

    # if bbox is None:
    bbox = volume_origin_to_bbox(vol > wall_level, origin)

    xmin, xmax, ymin, ymax, zmin, zmax = bbox
    roi_xmin = xmin - distance - padding
    roi_ymin = ymin - distance - padding
    roi_zmin = zmin - distance - padding
    roi_xmax = xmax + distance + padding
    roi_ymax = ymax + distance + padding
    roi_zmax = zmax + distance + padding
    roi_bbox = np.array((roi_xmin,roi_xmax,roi_ymin,roi_ymax,roi_zmin,roi_zmax))
    vol_roi = crop_and_pad_volume(vol, in_bbox=bbox, out_bbox=roi_bbox)

    dist_vol = distance_transform_edt(vol_roi < wall_level)
    roi_surround_vol = (dist_vol > 0) & (dist_vol < distance) # surround part is True, otherwise False.

    if prob:
        surround_vol = np.zeros_like(vol_roi)
        surround_vol[roi_surround_vol] = 1. - vol_roi[roi_surround_vol]
        if return_origin_instead_of_bbox:
            return surround_vol, roi_bbox[[0,2,4]]
        else:
            return surround_vol, roi_bbox
    else:
        if return_origin_instead_of_bbox:
            return roi_surround_vol, roi_bbox[[0,2,4]]
        else:
            return roi_surround_vol, roi_bbox


# @deprecated
# def get_surround_volume_v2(vol, bbox=None, origin=None, distance=5, wall_level=0, prob=False, return_origin_instead_of_bbox=False, padding=5):
#     """
#     Return the (volume, bbox) with voxels surrounding the ``active" voxels in the input volume set to 1 (prob=False) or 1 - vol (prob=True)

#     Args:
#         vol (3D ndarray of float): input volume in bbox.
#         bbox ((6,)-array): bbox
#         origin ((3,)-array): origin
#         wall_level (float):
#             voxels with value above this level are regarded as active.
#         distance (int):
#             surrounding voxels are closer than distance (in unit of voxel) from any active voxels.
#         prob (bool):
#             if True, surround voxels are assigned 1 - voxel value; if False, surround voxels are assigned 1.
#         padding (int): extra zero-padding, in unit of voxels.

#     Returns:
#         (volume, bbox)
#     """
#     from scipy.ndimage.morphology import distance_transform_edt
#     distance = int(np.round(distance))

#     # Identify the bounding box for the surrouding area.

#     if bbox is None:
#         bbox = volume_origin_to_bbox(vol > wall_level, origin)

#     xmin, xmax, ymin, ymax, zmin, zmax = bbox
#     roi_xmin = xmin - distance - padding
#     roi_ymin = ymin - distance - padding
#     roi_zmin = zmin - distance - padding
#     roi_xmax = xmax + distance + padding
#     roi_ymax = ymax + distance + padding
#     roi_zmax = zmax + distance + padding
#     roi_bbox = np.array((roi_xmin,roi_xmax,roi_ymin,roi_ymax,roi_zmin,roi_zmax))
#     vol_roi = crop_and_pad_volume(vol, in_bbox=bbox, out_bbox=roi_bbox)

#     dist_vol = distance_transform_edt(vol_roi < wall_level)
#     roi_surround_vol = (dist_vol > 0) & (dist_vol < distance) # surround part is True, otherwise False.

#     if prob:
#         surround_vol = np.zeros_like(vol_roi)
#         surround_vol[roi_surround_vol] = 1. - vol_roi[roi_surround_vol]
#         if return_origin_instead_of_bbox:
#             return surround_vol, roi_bbox[[0,2,4]]
#         else:
#             return surround_vol, roi_bbox
#     else:
#         if return_origin_instead_of_bbox:
#             return roi_surround_vol, roi_bbox[[0,2,4]]
#         else:
#             return roi_surround_vol, roi_bbox


def points_inside_contour(cnt, num_samples=None):
    xmin, ymin = cnt.min(axis=0)
    xmax, ymax = cnt.max(axis=0)
    h, w = (ymax-ymin+1, xmax-xmin+1)
    inside_ys, inside_xs = np.where(grid_points_in_poly((h, w), cnt[:, ::-1]-(ymin,xmin)))

    if num_samples is None:
        inside_points = np.c_[inside_xs, inside_ys] + (xmin, ymin)
    else:
        n = inside_ys.size
        random_indices = np.random.choice(range(n), min(1000, n), replace=False)
        inside_points = np.c_[inside_xs[random_indices], inside_ys[random_indices]]

    return inside_points


def assign_sideness(label_polygons, landmark_range_limits=None):
    """Assign left or right suffix to a label_polygons object.
    """

    if landmark_range_limits is None:
        landmark_range_limits = get_landmark_range_limits(label_polygons=label_polygons)

    label_polygons_dict = label_polygons.to_dict()
    label_polygons_sideAssigned_dict = defaultdict(dict)

    for name, v in label_polygons_dict.iteritems():
        if name not in singular_structures:
            name_u = convert_name_to_unsided(name)
            for sec, coords in v.iteritems():
                if np.any(np.isnan(coords)): continue

                lname = convert_to_left_name(name)
                rname = convert_to_right_name(name)

                if lname in landmark_range_limits and sec <= landmark_range_limits[lname][1]:
                    label_polygons_sideAssigned_dict[lname][sec] = coords
                elif rname in landmark_range_limits and sec >= landmark_range_limits[rname][0]:
                    label_polygons_sideAssigned_dict[rname][sec] = coords
                else:
                    print(name, sec, landmark_range_limits[lname], landmark_range_limits[rname])
                    raise Exception('label_polygon has structure %s on section %d beyond range limits.' % (name, sec))

        else:
            label_polygons_sideAssigned_dict[name].update({sec:coords for sec, coords in v.iteritems()
                                                           if not np.any(np.isnan(coords))})

    from pandas import DataFrame
    label_polygons_sideAssigned = DataFrame(label_polygons_sideAssigned_dict)
    return label_polygons_sideAssigned


def get_landmark_range_limits_v3(stack=None, label_indices_lookup=None, filtered_labels=None, mid_index=None):
    """
    Identify the index range spanned by each structure.

    Args:
        label_indices_lookup (dict): {label: index list}.
    """

    print('label_indices_lookup:')

    print()
    for label in sorted(label_indices_lookup.keys()):
        print(label, label_indices_lookup[label])
    print

    print('Estimated mid-sagittal image index = %d' % (mid_index))

    landmark_limits = {}

    structures_sided = set(label_indices_lookup.keys())

    if filtered_labels is not None:
        structures_sided = set(label_indices_lookup.keys()) & set(filtered_labels)

    structures_unsided = set(map(convert_to_unsided_label, structures_sided))

    for name_u in structures_unsided:

        if name_u in singular_structures:
            # single
            sections = sorted(label_indices_lookup[name_u]) if name_u in label_indices_lookup else []
            assert len(sections) > 0

            landmark_limits[name_u] = (np.min(sections), np.max(sections))
        else:
            # paired

            lname = convert_to_left_name(name_u)
            rname = convert_to_right_name(name_u)

            confirmed_left_sections = sorted(label_indices_lookup[lname]) if lname in label_indices_lookup else []
            confirmed_right_sections = sorted(label_indices_lookup[rname]) if rname in label_indices_lookup else []
            unconfirmed_side_sections = sorted(label_indices_lookup[name_u]) if name_u in label_indices_lookup else []

            sections = sorted(confirmed_left_sections + confirmed_right_sections + unconfirmed_side_sections)
            assert len(sections) > 0

            # Initialize votes according to whether a section is to the left or right of the mid-sagittal section.
            votes = {sec: 1 if sec > mid_index else -1 for sec in sections}

            if len(sections) == 1:
                sys.stderr.write('Structure %s has a label on only one section. Use its side relative to the middle section.\n' % name_u)
                sec = sections[0]
                if sec < mid_index:
                    landmark_limits[lname] = (sec, sec)
                else:
                    landmark_limits[rname] = (sec, sec)
                continue

            else:
                for sec in confirmed_left_sections:
                    for s in sections:
                        if s <= sec:
                            votes[s] -= 1

                for sec in confirmed_right_sections:
                    for s in sections:
                        if s >= sec:
                            votes[s] += 1

            print(sorted(votes.items()))

            unknown_side_sections = sorted([vote for sec, vote in votes.iteritems() if vote == 0])
            if len(unknown_side_sections) > 0:
                print('unknown_side_sections', unknown_side_sections)

            inferred_left_sections = sorted([sec for sec, vote in votes.iteritems() if vote < 0])
            if len(inferred_left_sections) > 0:
                minL = np.min(inferred_left_sections)
                maxL = np.max(inferred_left_sections)
            else:
                minL = None
                maxL = None

            inferred_right_sections = sorted([sec for sec, vote in votes.iteritems() if vote > 0])
            if len(inferred_right_sections) > 0:
                minR = np.min(inferred_right_sections)
                maxR = np.max(inferred_right_sections)
            else:
                minR = None
                maxR = None

            landmark_limits[lname] = (minL, maxL)
            landmark_limits[rname] = (minR, maxR)

    return landmark_limits

def generate_annotaion_list(stack, username, filepath=None):

    if filepath is None:
        filepath = os.path.join('/oasis/projects/nsf/csd395/yuncong/CSHL_data_labelings_losslessAlignCropped/',
                    '%(stack)s_%(username)s_latestAnnotationFilenames.txt' % {'stack': stack, 'username': username})

    f = open(filepath, 'w')

    fn_list = []

    for sec in range(first_bs_sec, last_bs_sec + 1):

        dm.set_slice(sec)

        ret = dm.load_review_result_path(username, 'latest', suffix='consolidated')
        if ret is not None:
            fn = ret[0]
            # print fn
            fn_list.append(fn)
            f.write(fn + '\n')

    f.close()
    return fn_list

def get_section_contains_labels(label_polygons, filtered_labels=None):

    section_contains_labels = defaultdict(set)

    if filtered_labels is None:
        labels = label_polygons.keys()
    else:
        labels = label_polygons.keys() & set(filtered_labels)

    for l in labels:
        for s in label_polygons[l].dropna().index:
            section_contains_labels[s].add(l)
    section_contains_labels.default_factory = None

    return section_contains_labels


def load_label_polygons_if_exists(stack, username, output_path=None, output=True, force=False,
                                downsample=None, orientation=None, annotation_rootdir=None,
                                side_assigned=False):
    """
    - assign sideness
    """

    if side_assigned:
        label_polygons_path = os.path.join(annotation_rootdir, '%(stack)s_%(username)s_annotation_polygons_sided.h5' % {'stack': stack, 'username': username})
    else:
        label_polygons_path = os.path.join(annotation_rootdir, '%(stack)s_%(username)s_annotation_polygons.h5' % {'stack': stack, 'username': username})

    if os.path.exists(label_polygons_path) and not force:
        label_polygons = pd.read_hdf(label_polygons_path, 'label_polygons')
    else:
        label_polygons = pd.DataFrame(generate_label_polygons(stack, username=username, orientation=orientation, annotation_rootdir=annotation_rootdir, downsample=downsample))

        if side_assigned:
            label_polygons = assign_sideness(label_polygons)

        if output:
            if output_path is None:
                label_polygons.to_hdf(label_polygons_path, 'label_polygons')
            else:
                label_polygons.to_hdf(output_path, 'label_polygons')

    return label_polygons


def generate_label_polygons(stack, username, orientation=None, downsample=None, timestamp='latest', output_path=None,
                            labels_merge_map={'SolM': 'Sol', 'LC2':'LC', 'Pn2': 'Pn', '7n1':'7n', '7n2':'7n', '7n3':'7n'},
                            annotation_rootdir=None, structure_names=None):
    """Read annotation file, and do the following processing:
    - merge labels
    - remove sideness tag if structure is singular
    """

    # dm = DataManager(stack=stack)

    # if structure_names is None:
    #     structure_names = labelMap_unsidedToSided.keys()

    label_polygons = defaultdict(lambda: {})
    section_bs_begin, section_bs_end = section_range_lookup[stack]

    labelings, usr, ts = DataManager.load_annotation_v2(stack=stack, username=username, orientation=orientation, downsample=downsample,
                                                        timestamp=timestamp, annotation_rootdir=annotation_rootdir)

    for sec in range(section_bs_begin, section_bs_end+1):

        # dm.set_slice(sec)
        if sec not in labelings['polygons']:
            sys.stderr.write('Section %d is not in labelings.\n' % sec)
            continue

        for ann in labelings['polygons'][sec]:
            label = ann['label']

            if label in labels_merge_map:
                label = labels_merge_map[label]

            if 'side' not in ann:
                ann['side'] = None

            if label in singular_structures:
                # assert ann['side'] is None, 'Structure %s is singular, but labeling says it has side property.' % label
                if ann['side'] is not None:
                    sys.stderr.write('Structure %s is singular, but labeling says it has side property... ignore side.\n' % label)
            else:
                if ann['side'] is not None:
                    label = label + '_' + ann['side']

            if label not in all_landmark_names_unsided: # 12N_L -> 12N
                sys.stderr.write('Label %s on Section %d is not recognized.\n' % (label, sec))
                    # continue

            label_polygons[label][sec] = np.array(ann['vertices']).astype(np.int)

    label_polygons.default_factory = None

    return label_polygons


def closest_to(point, poly):
    pol_ext = LinearRing(poly.exterior.coords)
    d = pol_ext.project(point)
    p = pol_ext.interpolate(d)
    closest_point_coords = list(p.coords)[0]
    return closest_point_coords


def average_multiple_volumes(volumes, bboxes):
    """
    Args:
        volumes (list of 3D boolean arrays):
        bboxes (list of tuples): each tuple is (xmin, xmax, ymin, ymax, zmin, zmax)

    Returns:
        (3D array, tuple): (averaged volume, bbox of averaged volume)
    """

    overall_xmin, overall_ymin, overall_zmin = np.min([(xmin, ymin, zmin) for xmin, xmax, ymin, ymax, zmin, zmax in bboxes], axis=0)
    overall_xmax, overall_ymax, overall_zmax = np.max([(xmax, ymax, zmax) for xmin, xmax, ymin, ymax, zmin, zmax in bboxes], axis=0)
    overall_volume = np.zeros((overall_ymax-overall_ymin+1, overall_xmax-overall_xmin+1, overall_zmax-overall_zmin+1), np.bool)

    for (xmin, xmax, ymin, ymax, zmin, zmax), vol in zip(bboxes, volumes):
        overall_volume[ymin - overall_ymin:ymax - overall_ymin+1, \
                        xmin - overall_xmin:xmax - overall_xmin+1, \
                        zmin - overall_zmin:zmax - overall_zmin+1] += vol

    return overall_volume, (overall_xmin, overall_xmax, overall_ymin, overall_ymax, overall_zmin, overall_zmax)

def interpolate_contours_to_volume(contours_grouped_by_pos=None, interpolation_direction=None, contours_xyz=None, return_voxels=False,
                                    return_contours=False, len_interval=20, fill=True, return_origin_instead_of_bbox=False):
    """Interpolate a stack of 2-D contours to create 3-D volume.

    Args:
        return_contours (bool): If true, only return resampled contours \{int: (n,2)-ndarrays\}. If false, return (volume, bbox) tuple.
        return_voxels (bool): If true, only return points inside contours.
        fill (bool): If true, the volume is just the shell. Otherwise, the volume is filled.

    Returns:
        If default, return (volume, bbox).
        volume (3d binary array):
        bbox (tuple): (xmin, xmax, ymin, ymax, zmin, zmax)

        If interpolation_direction == 'z', the points should be (x,y)
        If interpolation_direction == 'x', the points should be (y,z)
        If interpolation_direction == 'y', the points should be (x,z)
    """

    if contours_grouped_by_pos is None:
        assert contours_xyz is not None
        contours_grouped_by_pos = defaultdict(list)
        all_points = np.concatenate(contours_xyz)
        if interpolation_direction == 'z':
            for x,y,z in all_points:
                contours_grouped_by_pos[z].append((x,y))
        elif interpolation_direction == 'y':
            for x,y,z in all_points:
                contours_grouped_by_pos[y].append((x,z))
        elif interpolation_direction == 'x':
            for x,y,z in all_points:
                contours_grouped_by_pos[x].append((y,z))
    else:
        # all_points = np.concatenate(contours_grouped_by_z.values())
        if interpolation_direction == 'z':
            all_points = np.array([(x,y,z) for z, xys in contours_grouped_by_pos.iteritems() for x,y in xys])
        elif interpolation_direction == 'y':
            all_points = np.array([(x,y,z) for y, xzs in contours_grouped_by_pos.iteritems() for x,z in xzs])
        elif interpolation_direction == 'x':
            all_points = np.array([(x,y,z) for x, yzs in contours_grouped_by_pos.iteritems() for y,z in yzs])

    xmin, ymin, zmin = np.floor(all_points.min(axis=0)).astype(np.int)
    xmax, ymax, zmax = np.ceil(all_points.max(axis=0)).astype(np.int)

    interpolated_contours = get_interpolated_contours(contours_grouped_by_pos, len_interval)

    if return_contours:

        # from skimage.draw import polygon_perimeter
        # dense_contour_points = {}
        # for i, contour_pts in interpolated_contours.iteritems():
        #     xs = contour_pts[:,0]
        #     ys = contour_pts[:,1]
        #     dense_contour_points[i] = np.array(polygon_perimeter(ys, xs)).T[:, ::-1]
        # return dense_contour_points

        return {i: contour_pts.astype(np.int) for i, contour_pts in interpolated_contours.iteritems()}

    if fill:

        interpolated_interior_points = {i: points_inside_contour(contour_pts.astype(np.int)) for i, contour_pts in interpolated_contours.iteritems()}
        if return_voxels:
            return interpolated_interior_points

        volume = np.zeros((ymax-ymin+1, xmax-xmin+1, zmax-zmin+1), np.bool)
        for i, pts in interpolated_interior_points.iteritems():
            if interpolation_direction == 'z':
                volume[pts[:,1]-ymin, pts[:,0]-xmin, i-zmin] = 1
            elif interpolation_direction == 'y':
                volume[i-ymin, pts[:,0]-xmin, pts[:,1]-zmin] = 1
            elif interpolation_direction == 'x':
                volume[pts[:,0]-ymin, i-xmin, pts[:,1]-zmin] = 1

    else:
        volume = np.zeros((ymax-ymin+1, xmax-xmin+1, zmax-zmin+1), np.bool)
        for i, pts in interpolated_contours.iteritems():
            pts = pts.astype(np.int)
            if interpolation_direction == 'z':
                volume[pts[:,1]-ymin, pts[:,0]-xmin, i-zmin] = 1
            elif interpolation_direction == 'y':
                volume[i-ymin, pts[:,0]-xmin, pts[:,1]-zmin] = 1
            elif interpolation_direction == 'x':
                volume[pts[:,0]-ymin, i-xmin, pts[:,1]-zmin] = 1

    if return_origin_instead_of_bbox:
        return volume, np.array((xmin,ymin,zmin))
    else:
        return volume, np.array((xmin,xmax,ymin,ymax,zmin,zmax))


def get_interpolated_contours(contours_grouped_by_pos, len_interval, level_interval=1):
    """
    Interpolate contours at integer levels.
    Snap minimum z to the minimum integer .
    Snap maximum z to the maximum integer.

    Args:
        contours_grouped_by_pos (dict of (n,2)-ndarrays):
        len_interval (int):

    Returns:
        contours at integer levels (dict of (n,2)-ndarrays):
    """

    contours_grouped_by_adjusted_pos = {}
    for i, (pos, contour) in enumerate(sorted(contours_grouped_by_pos.iteritems())):
        if i == 0:
            contours_grouped_by_adjusted_pos[int(np.ceil(pos))] = contour
        elif i == len(contours_grouped_by_pos)-1:
            contours_grouped_by_adjusted_pos[int(np.floor(pos))] = contour
        else:
            contours_grouped_by_adjusted_pos[int(np.round(pos))] = contour

    zs = sorted(contours_grouped_by_adjusted_pos.keys())
    n = len(zs)

    interpolated_contours = {}

    for i in range(n):
        z0 = zs[i]
        interpolated_contours[z0] = np.array(contours_grouped_by_adjusted_pos[z0])
        if i + 1 < n:
            z1 = zs[i+1]
            interp_cnts = interpolate_contours(contours_grouped_by_adjusted_pos[z0], contours_grouped_by_adjusted_pos[z1], nlevels=z1-z0+1, len_interval_0=len_interval)
            for zi, z in enumerate(range(z0+1, z1)):
                interpolated_contours[z] = interp_cnts[zi+1]

    return interpolated_contours


def resample_polygon(cnt, n_points=None, len_interval=20):

    polygon = Polygon(cnt)

    if n_points is None:
        contour_length = polygon.exterior.length
        n_points = max(3, int(np.round(contour_length / len_interval)))

    resampled_cnt = np.empty((n_points, 2))
    for i, p in enumerate(np.linspace(0, 1, n_points+1)[:-1]):
        pt = polygon.exterior.interpolate(p, normalized=True)
        resampled_cnt[i] = (pt.x, pt.y)
    return resampled_cnt


from shapely.geometry import Polygon


def signed_curvatures(s, d=7):
    """
    https://www.wikiwand.com/en/Curvature
    Return curvature and x prime, y prime along a curve.
    """

    xp = np.gradient(s[:, 0], d)
    xpp = np.gradient(xp, d)
    yp = np.gradient(s[:, 1], d)
    ypp = np.gradient(yp, d)
    curvatures = (xp * ypp - yp * xpp)/np.sqrt(xp**2+yp**2)**3
    return curvatures, xp, yp

def interpolate_contours(cnt1, cnt2, nlevels, len_interval_0=20):
    '''
    Interpolate additional contours between (including) two contours cnt1 and cnt2.

    Args:
        cnt1 ((n,2)-ndarray): contour 1
        cnt2 ((n,2)-ndarray): contour 2
        nlevels (int): number of resulting contours, including contour 1 and contour 2.
        len_interval_0 (int): ?

    Returns:
        contours (list of (n,2)-ndarrays):
            resulting contours including the first and last contours.
    '''

    # poly1 = Polygon(cnt1)
    # poly2 = Polygon(cnt2)
    #
    # interpolated_cnts = np.empty((nlevels, len(cnt1), 2))
    # for i, p in enumerate(cnt1):
    #     proj_point = closest_to(Point(p), poly2)
    #     interpolated_cnts[:, i] = (np.column_stack([np.linspace(p[0], proj_point[0], nlevels),
    #                      np.linspace(p[1], proj_point[1], nlevels)]))
    #
    # print cnt1
    # print cnt2

    l1 = Polygon(cnt1).length
    l2 = Polygon(cnt2).length
    n1 = len(cnt1)
    n2 = len(cnt2)
    len_interval_1 = l1 / n1
    len_interval_2 = l2 / n2
    len_interval_interpolated = np.linspace(len_interval_1, len_interval_2, nlevels)

    # len_interval_0 = 20
    n_points = max(int(np.round(max(l1, l2) / len_interval_0)), n1, n2)

    s1 = resample_polygon(cnt1, n_points=n_points)
    s2 = resample_polygon(cnt2, n_points=n_points)

    # Make sure point sets are both clockwise or both anti-clockwise.

    # c1 = np.mean(s1, axis=0)
    # c2 = np.mean(s2, axis=0)
    # d1 = (s1 - c1)[0]
    # d1 = d1 / np.linalg.norm(d1)
    # d2s = s2 - c2
    # d2s = d2s / np.sqrt(np.sum(d2s**2, axis=1))[:,None]
    # s2_start_index = np.argmax(np.dot(d1, d2s.T))
    # print s2_start_index
    # s2 = np.r_[np.atleast_2d(s2[s2_start_index:]), np.atleast_2d(s2[:s2_start_index])]

    # s2i = np.r_[[s2[0]], s2[1:][::-1]]

    s2i = s2[::-1]

    # curv1, xp1, yp1 = signed_curvatures(s1)
    # curv2, xp2, yp2 = signed_curvatures(s2)
    # curv2i, xp2i, yp2i = signed_curvatures(s2i)

    d = 7
    xp1 = np.gradient(s1[:, 0], d)
    yp1 = np.gradient(s1[:, 1], d)
    xp2 = np.gradient(s2[:, 0], d)
    yp2 = np.gradient(s2[:, 1], d)
    xp2i = np.gradient(s2i[:, 0], d)
    yp2i = np.gradient(s2i[:, 1], d)

    # using correlation over curvature values directly is much better than using correlation over signs
    # sign1 = np.sign(curv1)
    # sign2 = np.sign(curv2)
    # sign2i = np.sign(curv2i)

    # conv_curv_1_2 = np.correlate(np.r_[curv2, curv2], curv1, mode='valid')
    conv_xp_1_2 = np.correlate(np.r_[xp2, xp2], xp1, mode='valid')
    conv_yp_1_2 = np.correlate(np.r_[yp2, yp2], yp1, mode='valid')

    # conv_1_2 = np.correlate(np.r_[sign2, sign2], sign1, mode='valid')

    # top, second = conv_1_2.argsort()[::-1][:2]
    # d2_top = (s2 - c2)[top]
    # d2_top = d2_top / np.linalg.norm(d2_top)
    # d2_second = (s2 - c2)[second]
    # d2_second = d2_second / np.linalg.norm(d2_second)
    # s2_start_index = [top, second][np.argmax(np.dot([d2_top, d2_second], d1))]

    # conv_curv_1_2i = np.correlate(np.r_[curv2i, curv2i], curv1, mode='valid')
    conv_xp_1_2i = np.correlate(np.r_[xp2i, xp2i], xp1, mode='valid')
    conv_yp_1_2i = np.correlate(np.r_[yp2i, yp2i], yp1, mode='valid')

    # conv_1_2i = np.correlate(np.r_[sign2i, sign2i], sign1, mode='valid')
    # top, second = conv_1_2i.argsort()[::-1][:2]
    # if xp1[top] * xp2i[top] + yp1[top] * yp2i[top] > xp1[top] * xp2i[top] + yp1[top] * yp2i[top] :
    #     s2i_start_index = top
    # else:
    #     s2i_start_index = second

    # d2_top = (s2i - c2)[top]
    # d2_top = d2_top / np.linalg.norm(d2_top)
    # d2_second = (s2i - c2)[second]
    # d2_second = d2_second / np.linalg.norm(d2_second)
    # s2i_start_index = [top, second][np.argmax(np.dot([d2_top, d2_second], d1))]

    # if conv_1_2[s2_start_index] > conv_1_2i[s2i_start_index]:
    #     s3 = np.r_[np.atleast_2d(s2[s2_start_index:]), np.atleast_2d(s2[:s2_start_index])]
    # else:
    #     s3 = np.r_[np.atleast_2d(s2i[s2i_start_index:]), np.atleast_2d(s2i[:s2i_start_index])]

    # from scipy.spatial import KDTree
    # tree = KDTree(s1)
    # nn_in_order_s2 = np.count_nonzero(np.diff(tree.query(s2)[1]) > 0)
    # nn_in_order_s2i = np.count_nonzero(np.diff(tree.query(s2i)[1]) > 0)

    # overall_s2 = conv_curv_1_2 / conv_curv_1_2.max() + conv_xp_1_2 / conv_xp_1_2.max() + conv_yp_1_2 / conv_yp_1_2.max()
    # overall_s2i = conv_curv_1_2i / conv_curv_1_2i.max() + conv_xp_1_2i / conv_xp_1_2i.max() + conv_yp_1_2i / conv_yp_1_2i.max()

    # overall_s2 =  conv_xp_1_2 / conv_xp_1_2.max() + conv_yp_1_2 / conv_yp_1_2.max()
    # overall_s2i =  conv_xp_1_2i / conv_xp_1_2i.max() + conv_yp_1_2i / conv_yp_1_2i.max()

    overall_s2 =  conv_xp_1_2 + conv_yp_1_2
    overall_s2i =  conv_xp_1_2i + conv_yp_1_2i

    if overall_s2.max() > overall_s2i.max():
        s2_start_index = np.argmax(overall_s2)
        s3 = np.roll(s2, -s2_start_index, axis=0)
    else:
        s2i_start_index = np.argmax(overall_s2i)
        s3 = np.roll(s2i, -s2i_start_index, axis=0)

    # plt.plot(overall)
    # plt.show();

    interpolated_contours = [(1-r) * s1 + r * s3 for r in np.linspace(0, 1, nlevels)]
    resampled_interpolated_contours = [resample_polygon(cnt, len_interval=len_interval_interpolated[i]) for i, cnt in enumerate(interpolated_contours)]

    return resampled_interpolated_contours

def convert_annotation_v3_original_to_aligned(contour_df, stack):

    filename_to_section, _ = DataManager.load_sorted_filenames(stack)

    # import cPickle as pickle
    Ts = DataManager.load_transforms(stack=stack, downsample_factor=1, use_inverse=True)

    contour_df_out = contour_df.copy()

    for cnt_id, cnt in contour_df[(contour_df['orientation'] == 'sagittal') & (contour_df['resolution'] == 'raw')].iterrows():

        img_name = cnt['filename']
        if img_name not in filename_to_section:
            continue
        sec = filename_to_section[img_name]
        contour_df_out.loc[cnt_id, 'section'] = sec

        Tinv = Ts[img_name]

        n = len(cnt['vertices'])

        vertices_on_aligned_cropped = np.dot(Tinv, np.c_[cnt['vertices'], np.ones((n,))].T).T[:, :2]
        contour_df_out.set_value(cnt_id, 'vertices', vertices_on_aligned_cropped)

        label_position_on_aligned_cropped = np.dot(Tinv, np.r_[cnt['label_position'], 1])[:2]
        contour_df_out.set_value(cnt_id, 'label_position', label_position_on_aligned_cropped)

        print(cnt['label_position'], label_position_on_aligned_cropped, contour_df_out.loc[cnt_id]['label_position'])

    return contour_df_out


def convert_annotation_v3_original_to_aligned_cropped_v2(contour_df, stack, out_resolution, prep_id=2):
    """
    Convert contours defined wrt original reference frame in raw resolution to
    contours defined wrt aligned cropped images in the given `out_resolution`.

    Args:
        out_resolution (float): the output contours are of this resolution.
    """

    contour_df = contour_df.copy()

    # xmin_down32, _, ymin_down32, _, _, _ = DataManager.load_cropbox(stack, prep_id=prep_id)
    xmin_down32, _, ymin_down32, _ = DataManager.load_cropbox_v2(stack, prep_id=prep_id, only_2d=True)

    # Ts_rawResol is a dictionary[filename] containing a 3x3 transformation matrix for each file
    Ts_rawResol = DataManager.load_transforms(stack=stack, resolution='raw', use_inverse=True)

    for cnt_id, cnt in contour_df.iterrows():
        sec = cnt['section']
        if sec not in metadata_cache['valid_sections'][stack]:
            continue
        fn = metadata_cache['sections_to_filenames'][stack][sec]
        contour_df.loc[cnt_id, 'section'] = sec

        Tinv_rawResol = Ts_rawResol[fn]
        
        # Apply Tinv_rawResol 3x3 transformation matrix to the vertices 
        vertices_wrt_alignedCropped_rawResol = np.dot(Tinv_rawResol, np.c_[cnt['vertices'], np.ones((len(cnt['vertices']),))].T).T[:, :2] - (xmin_down32 * 32., ymin_down32 * 32.)
        vertices_wrt_alignedCropped_outResol = vertices_wrt_alignedCropped_rawResol * convert_resolution_string_to_voxel_size(stack=stack, resolution='raw') / convert_resolution_string_to_voxel_size(stack=stack, resolution=out_resolution)
        contour_df.set_value(cnt_id, 'vertices', vertices_wrt_alignedCropped_outResol)
        contour_df.set_value(cnt_id, 'resolution', out_resolution)

        if 'label_position' in cnt and cnt['label_position'] is not None:
            label_position_wrt_alignedCropped_rawResol = np.dot(Tinv_rawResol, np.r_[cnt['label_position'], 1])[:2] - (xmin_down32 * 32., ymin_down32 * 32.)
            label_position_wrt_alignedCropped_outResol = label_position_wrt_alignedCropped_rawResol * convert_resolution_string_to_voxel_size(stack=stack, resolution='raw') / convert_resolution_string_to_voxel_size(stack=stack, resolution=out_resolution)
            contour_df.set_value(cnt_id, 'label_position', label_position_wrt_alignedCropped_outResol)

    return contour_df

convert_annotation_v3_original_to_aligned_cropped = convert_annotation_v3_original_to_aligned_cropped_v2

def convert_annotation_v3_aligned_cropped_to_original_v2(contour_df, stack, resolution='raw', prep_id=2):
    """
    Convert contours defined wrt aligned cropped frame in resolution to
    contours defined wrt orignal unprocessed image frame in the raw resolution.

    Args:
        contour_df (DataFrame): rows are polygon ids, columns are properties.
        resolution (str): resolution of the input contour.

    Returns:
        DataFrame: a DataFrame containing converted polygons.
    """

    _, section_to_filename = DataManager.load_sorted_filenames(stack)

    # xmin_down32, _, ymin_down32, _, _, _ = DataManager.load_cropbox(stack, prep_id=prep_id)
    xmin_down32, _, ymin_down32, _, = DataManager.load_cropbox_v2(stack, prep_id=prep_id, only_2d=True)

    Ts_rawResol = DataManager.load_transforms(stack=stack, resolution='raw', use_inverse=True)

    # cnts = contour_df[(contour_df['orientation'] == 'sagittal') & (contour_df['resolution'] == resolution)]

    for cnt_id, cnt in contour_df.iterrows():
        sec = cnt['section']
        fn = section_to_filename[sec]
        if fn in ['Placeholder', 'Nonexisting', 'Rescan']:
            continue
        contour_df.loc[cnt_id, 'filename'] = fn

        T_rawResol = np.linalg.inv(Ts_rawResol[fn])

        vertices_wrt_alignedUncropped_rawResol = np.array(cnt['vertices']) * \
        convert_resolution_string_to_voxel_size(resolution=resolution, stack=stack) / \
        convert_resolution_string_to_voxel_size(resolution='raw', stack=stack) + (xmin_down32 * 32., ymin_down32 * 32.)
        contour_df.set_value(cnt_id, 'vertices', np.dot(T_rawResol, np.c_[vertices_wrt_alignedUncropped_rawResol, np.ones((len(vertices_wrt_alignedUncropped_rawResol),))].T).T[:, :2])
        contour_df.set_value(cnt_id, 'resolution', 'raw')

        if 'label_position' in cnt and cnt['label_position'] is not None:
            label_position_wrt_alignedUncropped_rawResol = np.array(cnt['label_position']) * \
            convert_resolution_string_to_voxel_size(resolution=resolution, stack=stack) / \
            convert_resolution_string_to_voxel_size(resolution='raw', stack=stack) + (xmin_down32 * 32., ymin_down32 * 32.)
            contour_df.set_value(cnt_id, 'label_position', np.dot(T_rawResol, np.r_[label_position_wrt_alignedUncropped_rawResol, 1])[:2])

    return contour_df



def convert_annotations(contour_df, stack, in_wrt, in_resol, out_wrt, out_resol):
    """
    Args:
        contour_df (DataFrame): rows are polygon ids, columns are properties.
        resolution (str): resolution of the input contour.
        in_wrt (str):
        out_wrt (str):

    Returns:
        DataFrame: a DataFrame containing converted polygons.
    """

    _, section_to_filename = DataManager.load_sorted_filenames(stack)
    # xmin_down32, _, ymin_down32, _, _, _ = DataManager.load_cropbox(stack, prep_id=in_prep_id)

    Ts_rawResol = DataManager.load_transforms(stack=stack, resolution='raw', use_inverse=True)

    for cnt_id, cnt in contour_df.iterrows():
        sec = cnt['section']
        fn = section_to_filename[sec]
        if fn in ['Placeholder', 'Nonexisting', 'Rescan']:
            continue
        contour_df.loc[cnt_id, 'filename'] = fn

        T_rawResol = np.linalg.inv(Ts_rawResol[fn])

        in_vertices = cnt['vertices']
        # vertices_wrt_alignedUncropped_rawResol = np.array(in_vertices) * \
        # convert_resolution_string_to_voxel_size(resolution=resolution, stack=stack) / \
        # convert_resolution_string_to_voxel_size(resolution='raw', stack=stack) + (xmin_down32 * 32., ymin_down32 * 32.)
        # out_vertices = np.dot(T_rawResol, np.c_[vertices_wrt_alignedUncropped_rawResol, np.ones((len(vertices_wrt_alignedUncropped_rawResol),))].T).T[:, :2]

        converter = CoordinatesConverter(stack=stack)

        out_vertices = converter.convert_frame_and_resolution(p=in_vertices, in_wrt=in_wrt, in_resolution=in_resol, out_wrt=out_wrt, out_resolution=out_resol)

        contour_df.set_value(cnt_id, 'vertices', out_vertices)
        contour_df.set_value(cnt_id, 'resolution', 'raw')

        if 'label_position' in cnt and cnt['label_position'] is not None:

            in_label_pos = cnt['label_position']
            out_label_pos = converter.convert_frame_and_resolution(p=in_label_pos, in_wrt=in_wrt, in_resolution=in_resol, out_wrt=out_wrt, out_resolution=out_resol)
            contour_df.set_value(cnt_id, 'label_position', out_label_pos)

            # label_position_wrt_alignedUncropped_rawResol = np.array(cnt['label_position']) * \
            # convert_resolution_string_to_voxel_size(resolution=resolution, stack=stack) / \
            # convert_resolution_string_to_voxel_size(resolution='raw', stack=stack) + (xmin_down32 * 32., ymin_down32 * 32.)
            # contour_df.set_value(cnt_id, 'label_position', np.dot(T_rawResol, np.r_[label_position_wrt_alignedUncropped_rawResol, 1])[:2])

    return contour_df
