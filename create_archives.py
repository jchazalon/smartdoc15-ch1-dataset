#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script automatically builds dataset archives (one for the frames, one for the models)
from the original dataset structure of the authors. It can also produce small sample
archives for testing purpose.

The authors' dataset structure is as follows:
    /data/competitions/2015-ICDAR-smartdoc/challenge1/
    ├── [...]
    ├── 02-test_set
    │   ├── background01
    │   │   ├── datasheet001.avi
    │   │   ├── [...]
    │   │   └── tax005.avi
    │   ├── background02
    │   │   └── [...]
    │   ├── background03
    │   │   └── [...]
    │   ├── background04
    │   │   └── [...]
    │   └── background05
    │       └── [...]
    ├── 02-test_set_frames
    │   ├── background01
    │   │   ├── datasheet001
    │   │   │   ├── frame_0001.jpeg
    │   │   │   ├── [...]
    │   │   │   └── frame_0235.jpeg
    │   │   ├── [...]
    │   │   └── tax005
    │   │       └── [...]
    │   ├── [...]
    │   └── background05
    │       └── [...]
    ├── 04-ground_truth
    │   ├── background01
    │   │   ├── datasheet001.gt.xml
    │   │   ├── [...]
    │   │   └── tax005.gt.xml
    │   ├── background02
    │   ├── [...]
    │   └── background05
    │       └── [...]
    ├── 99-computable-version-2017-test
    │   └── >> output of this script goes here <<
    ├── models
    │   ├── 01-original
    │   │   ├── datasheet001.png
    │   │   ├── [...]
    │   │   └── tax005.png
    │   ├── 02-edited
    │   │   ├── datasheet001.png
    │   │   ├── [...]
    │   │   └── tax005.png
    │   ├── 03-captured-nexus
    │   │   ├── datasheet001.jpg # JPG images here
    │   │   ├── [...]
    │   │   └── tax005.jpg
    │   ├── 04-corrected-nexus
    │   │   ├── datasheet001.png
    │   │   ├── [...]
    │   │   └── tax005.png
    │   ├── 05-corrected-nexus-scaled33
    │   │   ├── datasheet001.png
    │   │   ├── [...]
    │   │   └── tax005.png
    │   ├── correct_perspective.m
    │   └── original_datasets_files.txt
    └── [...]



The frame images were produced using the following commands:
    cd /data/competitions/2015-ICDAR-smartdoc/challenge1/02-test_set/
    find . -iname "*.avi" | \
        parallel  "mkdir -p ../02-test_set_frames/{.} ; ffmpeg -i {} -f image2 ../02-test_set_frames/{.}/frame_%04d.jpeg"

where `parallel` calls GNU Parallel.

SAMPLE INVOCATION
-----------------
    python create_archives.py test \
        /data/competitions/2015-ICDAR-smartdoc/challenge1/ \
        /data/competitions/2015-ICDAR-smartdoc/challenge1/99-computable-version-2017-test/
"""
from __future__ import print_function, absolute_import, division
import six

import os
import argparse
import glob
import re
import tarfile
from itertools import product
import datetime

import lxml.etree as etree  # import xml.etree as etree
import lxml.sax   as sax  # import xml.sax   as sax
from xml.dom.pulldom import SAX2DOM
import dexml
from dexml import fields
import pandas as pd


# Constants
# ##############################################################################
MODEL_CATEGORIES = [
    "01-original",
    "02-edited",
    "03-captured-nexus",
    "04-corrected-nexus",
    "05-corrected-nexus-scaled33"]

MODELTYPE_NAME2ID = {
    "datasheet":0,
    "letter":1,
    "magazine":2,
    "paper":3,
    "patent":4,
    "tax":5 }

MODEL_NAME2ID = {
    "datasheet001": 0, "datasheet002": 1, "datasheet003": 2, "datasheet004": 3, "datasheet005": 4,
    "letter001": 5, "letter002": 6, "letter003": 7, "letter004": 8, "letter005": 9,
    "magazine001": 10, "magazine002": 11, "magazine003": 12, "magazine004": 13, "magazine005": 14,
    "paper001": 15, "paper002": 16, "paper003": 17, "paper004": 18, "paper005": 19,
    "patent001": 20, "patent002": 21, "patent003": 22, "patent004": 23, "patent005": 24,
    "tax001": 25, "tax002": 26, "tax003": 27, "tax004": 28, "tax005": 29 }

BACKGROUND_NAME2ID = {
    'background01': 0,
    'background02': 1,
    'background03': 2,
    'background04': 3,
    'background05': 4 }

BACKGROUNDS = sorted(six.iterkeys(BACKGROUND_NAME2ID))

DOCUMENTS = sorted(six.iterkeys(MODEL_NAME2ID))


# Classes for XML parsing of the ground truth
# ##############################################################################

# dexml extensions
# ------------------------------------------------------------------------------
class RestrictedString(fields.Value):
    """Field representing a string value which is restricted 
    to a set a legal values.
    """

    class arguments(fields.Value.arguments):
        case_sensitive = False

    def __init__(self, *legal_values, **kwds):
        super(RestrictedString,self).__init__(**kwds)
        self.legal_values = []
        for lv in legal_values:
            if not self.case_sensitive:
                lv = str(lv).lower()
            self.legal_values.append(lv)


    def _check_restrictions(self, val):
        testval = val
        if not self.case_sensitive:
            testval = testval.lower()
        return testval in self.legal_values

    def __set__(self,instance,value):
        if not self._check_restrictions(value):
            raise ValueError("Illegal value '%s' for restricted string (%s)." 
                             % (value, self.legal_values))
        instance.__dict__[self.field_name] = value

    def parse_value(self,val):
        if not self._check_restrictions(val):
            raise dexml.ParseError("Illegal value '%s' for restricted string (%s)." 
                             % (val, self.legal_values))
        return val


# GENERAL components
# ------------------------------------------------------------------------------
class Software(dexml.Model):
    """Describe the software used to produce a file."""
    class meta:
        tagname = "software_used"
    name    = fields.String()
    version = fields.String()

class Size(dexml.Model):
    """Simple size abstraction. Floats used, beware!"""
    width  = fields.Float()
    height = fields.Float()

class MainModel(dexml.Model):
    """Basis for main models. Manages automatically the generation timestamp.
    Version "number" and optionnal software information are still to provide."""
    version   = fields.String()
    generated = fields.String() # Could be a date object at some point
    software_used  = fields.Model(Software, required=False)

    def __init__(self,**kwds):
        super(MainModel, self).__init__(**kwds)
        self.version   = "0.3"
        self.generated = datetime.datetime.now().isoformat() # warning: no TZ info here

    def exportToFile(self, filename, pretty_print=False):
        out_str = self.render(encoding="utf-8") # no pretty=pretty_print here, done by lxml
        if pretty_print:
            # lxml pretty print should be way faster than the minidom one used in dexml
            root = etree.fromstring(out_str)
            out_str = etree.tostring(root, xml_declaration=True, encoding='utf-8', pretty_print=True)
        # print "Output file's content:\n%s" % out_str
        with open(os.path.abspath(filename), "wb") as out_f:
            out_f.write(out_str)

    @classmethod 
    def loadFromFile(cls, filename):
        path_file = os.path.abspath(filename)
        if not os.path.isfile(path_file):
            err = "Error: '%s' does not exist or is not a file." % filename
            print(err)
            raise Exception(err)

        # Note: parsing a file directly with dexml/minidom is supposedly slower, si I used lxml one, 
        #       but I did not benchmark it.
        tree = etree.parse(path_file)
        handler = SAX2DOM()
        sax.saxify(tree, handler)
        dom = handler.document

        # In case, you can pass the filename to parse() here to skip lxml
        mdl = cls.parse(dom)
        return mdl

    # def __repr__(self):
    #     return "%s(%r)" % (self.__class__, self.__dict__)

# Sample
# ------------------------------------------------------------------------------
class FrameSize(Size):
    class meta:
        tagname = "frame_size"

class Frame(dexml.Model):
    """Store information about a frame to process: index in original stream, filename of extracted version, etc."""
    class meta:
        tagname = "frame"
    index     = fields.Integer(required=False)
    time      = fields.Float(required=False)
    filename  = fields.String() # can be relative to root given to a tool on command line

class Sample(MainModel):
    """Main model for raw test samples (sequences of frames) used to benchmark tools."""
    class meta:
        tagname = "sample"
    frame_size = fields.Model(FrameSize)
    frames     = fields.List(Frame, tagname="frames")


# SegResult
# ------------------------------------------------------------------------------
class Pt(dexml.Model):
    """Simple point class."""
    class meta:
        tagname = "point"
    name = RestrictedString("tl","bl","br","tr")
    x = fields.Float()
    y = fields.Float()

class FrameSegResult(dexml.Model):
    """Tracker output for a given frame. Only 1 object can be detected for now."""
    class meta:
        tagname = "frame"
    index     = fields.Integer(required=False)
    rejected  = fields.Boolean()
    points    = fields.Dict(Pt, key='name', unique=True)


class SegResult(MainModel):
    """Main model for tracker output when run on a sample."""
    class meta:
        tagname = "seg_result"
    # FIXME relative or absolute? Should be **relative** to dataset root
    source_sample_file   = fields.String(tagname="source_sample_file")
    segmentation_results = fields.List(FrameSegResult, tagname="segmentation_results")


# GroundTruth
# ------------------------------------------------------------------------------
class ObjectShape(Size):
    class meta:
        tagname = "object_shape"


class GroundTruth(SegResult):
    """Main model for ground truthing tool output when run on a sample.
    Like segResult, but with a reference object to facilitate evaluation."""
    class meta:
        tagname = "ground_truth"
    object_shape = fields.Model(ObjectShape)



# Naive logging helpers
# ##############################################################################
def __logmsg(lvl, msg):
    print("%s: %s" % (lvl, msg))
def __info(msg):
    __logmsg("INFO", msg)
def __warn(msg):
    __logmsg("WARNING", msg)
def __err(msg, exception=Exception):
    __logmsg("ERROR", msg)
    raise exception(msg)


# Other helpers
# ##############################################################################
def _find_image_files(path):
    patterns = ['*.jpg', '*.png']
    results = []
    for pattern in patterns:
        results.extend(glob.glob(os.path.join(path, pattern)))
        # variant with filename only
        # full_paths = glob.glob(os.path.join(path, pattern))
        # results.extend([p[len(path):] for p in full_paths])
    return sorted(results)

def _check_existing_dir(path):
    if not os.path.isdir(path):
        __err("ERROR: '%s' does not exist or is not a directory." % (path, ), ValueError)

def _check_existing_or_creatable_dir(path):
    if os.path.exists(path):
        if not os.path.isdir(path):
            __err("ERROR: '%s' is not a directory." % (path, ), ValueError)
    else:
        __info("Creating output directory '%s'." % (path, ))
        os.makedirs(path)

def tar_reset_filter(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo

# MAIN
# ##############################################################################
def main():
    parser = argparse.ArgumentParser(description=__doc__, 
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('mode', choices=["test", "complete"],
        help="Creation mode. 'test': produce a subset; 'complete': full export.")
    parser.add_argument('dataset_home', help="Path to dataset home (authors structure).")
    parser.add_argument('output_dir', help="Path to output directory.")
    args = parser.parse_args()
    # -----------------------------------------------------------------------------
    __info("Starting up")

    # Check parameters
    _check_existing_dir(args.dataset_home)
    _check_existing_or_creatable_dir(args.output_dir)

    # Try create tmp dir for metadata files
    tmp_out_dir = os.path.join(args.output_dir, "_tmp")
    _check_existing_or_creatable_dir(tmp_out_dir)

    # Generate metadata for models
    # -----------------------------------------------------------------------------
    __info("Preparing metadata for models.")

    # Get file names
    model_files = []
    for cat in MODEL_CATEGORIES:
        model_files.extend(_find_image_files(os.path.join(args.dataset_home, "models", cat)))

    # Generate metadata structure
    path_parser = re.compile(r'.*/(\d+-\S+)/(\D+)(\d+)\.(png|jpg)')
    model_resources = []
    for path in model_files:
        try:
            model_cat, modeltype_name, model_subid1, ext = path_parser.match(path).groups()
        except:
            __err("Cannot parse path '%s'" % (path, ), ValueError)
        else:
            model_name = "%s%s"%(modeltype_name, model_subid1)
            model_resources.append((
                model_cat, 
                model_name, 
                MODEL_NAME2ID[model_name], 
                modeltype_name, 
                MODELTYPE_NAME2ID[modeltype_name], 
                int(model_subid1)-1, 
                '%s/%s.%s'%(model_cat, model_name, ext)
            ))

    df = pd.DataFrame(model_resources)
    df.columns = ["model_cat", "model_name", "model_id", "modeltype_name", "modeltype_id", "model_subid", "image_path"]
    df.sort_values(by=["model_cat", "model_id"], inplace=True)
    df.reset_index(inplace=True)
    df.drop(columns=["index"], inplace=True)
    mdl_metadata_output = os.path.join(tmp_out_dir, "model_metadata.csv.gz")

    if args.mode == "test":
        df = df[df.model_id == 3]

    df.to_csv(mdl_metadata_output, index=False, compression='gzip')
    __info("Wrote model metadata to '%s'." % (mdl_metadata_output, ))

    # Create tar file for models
    # -----------------------------------------------------------------------------
    __info("Creating tar file for models.")
    model_tar_path = os.path.join(args.output_dir, "models.tar.gz")
    with tarfile.open(model_tar_path, "w:gz") as tar:
        # add images
        for name in df["image_path"]:
            # print(name)
            real_path = os.path.join(args.dataset_home, "models", name)
            tar.add(real_path, arcname=name, filter=tar_reset_filter)

        # extra files (if they exist)
        for name in ["correct_perspective.m", "README.md", "README", "LICENCE", "VERSION", "original_datasets_files.txt"]:
            real_path = os.path.join(args.dataset_home, "models", name)
            if os.path.exists(real_path):
                tar.add(real_path, arcname=name, filter=tar_reset_filter)

        # metadata
        tar.add(mdl_metadata_output, arcname="metadata.csv.gz", filter=tar_reset_filter)
    __info("Wrote model tar file to '%s'." % (model_tar_path, ))


    # Generate metadata for frames
    # -----------------------------------------------------------------------------
    __info("Preparing metadata for frames.")
    gt_files = [
            os.path.join(args.dataset_home, "04-ground_truth", bg, doc+".gt.xml") 
            for bg, doc in product(BACKGROUNDS, DOCUMENTS)]

    filename_parser = re.compile(r'background(\d+)/(\D+)(\d+)')
    frame_resources = []
    for gt_file in gt_files:
        gt_vid = GroundTruth.loadFromFile(gt_file)
        bg_id1, modeltype_name, model_subid1 = filename_parser.match(gt_vid.source_sample_file).groups()
    #     date_generated = gt_vid.generated[0:10]
        model_width = gt_vid.object_shape.width
        model_height = gt_vid.object_shape.height
        for frame_info in gt_vid.segmentation_results:
            frame_index = frame_info.index
            rejected = frame_info.rejected
            points = frame_info.points
            tl_x, tl_y = points['tl'].x, points['tl'].y
            bl_x, bl_y = points['bl'].x, points['bl'].y
            br_x, br_y = points['br'].x, points['br'].y
            tr_x, tr_y = points['tr'].x, points['tr'].y
            image_path = "background%s/%s%s/frame_%04d.jpeg"%(bg_id1, modeltype_name, model_subid1, frame_index)
            bg_name = "background%s"%(bg_id1)
            model_name = "%s%s"%(modeltype_name, model_subid1)
            type_id = MODELTYPE_NAME2ID[modeltype_name]
            
            frame_resources.append((
                bg_name,
                int(bg_id1)-1,
                model_name,
                MODEL_NAME2ID[model_name],
                modeltype_name,
                MODELTYPE_NAME2ID[modeltype_name],
                int(model_subid1)-1, 
                image_path,
                frame_index,  # /!\ 1-indexed /!\
                model_width, model_height,
                tl_x, tl_y, bl_x, bl_y, br_x, br_y, tr_x, tr_y))

    df = pd.DataFrame(frame_resources)
    df.columns = [
            'bg_name', 'bg_id', 'model_name', 'model_id', 'modeltype_name', 'modeltype_id', "model_subid", 
            'image_path',
            'frame_index',
            'model_width', 'model_height',
            'tl_x', 'tl_y', 'bl_x', 'bl_y', 'br_x', 'br_y', 'tr_x', 'tr_y']

    df.sort_values(by=['bg_id', 'model_id', 'frame_index'], inplace=True)
    df.reset_index(inplace=True)
    df.drop(columns=["index"], inplace=True)
    frames_metadata_output = os.path.join(tmp_out_dir, "frames_metadata.csv.gz")

    if args.mode == "test":
        df = df.sample(50)

    df.to_csv(frames_metadata_output, index=False, compression='gzip')
    __info("Wrote frames metadata to '%s'." % (frames_metadata_output, ))

    # Summary about dataset content
    ptbl = df.pivot_table(values='frame_index', index='model_name', columns='bg_name', aggfunc='count', margins=True)
    __info("Frames per model and per background:")
    __info("\n" + ptbl.to_string())


    # Create tar file for frames
    # -----------------------------------------------------------------------------
    __info("Creating tar file for frames.")
    frames_tar_path = os.path.join(args.output_dir, "frames.tar.gz")
    with tarfile.open(frames_tar_path, "w:gz") as tar:
        total = len(df)
        # add images
        for counter, name in enumerate(df["image_path"], start=1):
            if (counter - 1) % 100 == 0 or counter == total:
                __info("Read file %d/%d ('%s')." % (counter, total, name))
            real_path = os.path.join(args.dataset_home, "02-test_set_frames", name)
            tar.add(real_path, arcname=name, filter=tar_reset_filter)

        # extra files (if they exist)
        for name in ["README.md", "README", "LICENCE", "VERSION", "original_datasets_files.txt"]:
            real_path = os.path.join(args.dataset_home, "models", name)
            if os.path.exists(real_path):
                tar.add(real_path, arcname=name, filter=tar_reset_filter)

        # metadata
        tar.add(frames_metadata_output, arcname="metadata.csv.gz", filter=tar_reset_filter)
    __info("Wrote frames tar file to '%s'." % (frames_tar_path, ))


    # Hash files
    # -----------------------------------------------------------------------------
    os.system("cd %s && sha256sum models.tar.gz frames.tar.gz > sha256.chksum" % (args.output_dir, ))
    __info("Wrote checksums.")

    __warn("UPDATE THE CHECKSUMS IN smartdoc_loader.py!")

    # -----------------------------------------------------------------------------
    __info("All done.")
# // main


# ##############################################################################
# ##############################################################################
if __name__ == "__main__":
    try:
        main()
    except:
        __warn("THERE WERE SOME ERRORS.\n")
        raise
