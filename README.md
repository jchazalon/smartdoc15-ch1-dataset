# SmartDoc 2015 - Challenge 1 Dataset
Easy to download and parse version of the Smartdoc 2015 - Challenge 1 dataset.

The original version of this dataset can be obtained at http://smartdoc.univ-lr.fr/.

**To download the dataset, you have two options:**
 1. **(easier) use the python wrapper: https://github.com/jchazalon/smartdoc15-ch1-pywrapper**
 2. download the `frames.tar.gz` and the `models.tar.gz` files here: https://github.com/jchazalon/smartdoc15-ch1-dataset/releases


## About SmartDoc 2015 - Challenge 1
The Smartdoc 2015 - Challenge 1 dataset was originally created for the Smartdoc 2015 competition focusing on the evaluation of document image acquisition method using smartphones. The challenge 1, in particular, consisted in detecting and segmenting document regions in video frames extracted from the preview stream of a smartphone. 

The following video shows the ideal segmentation output (in red outline) for the preview phase of some acquisition session.
[![Video of ideal segmentation of a document page during capture preview.](https://img.youtube.com/vi/WNsI0R_rpO0/0.jpg)](https://www.youtube.com/watch?v=WNsI0R_rpO0)

To build our dataset, we took six different document types coming from public databases and we chose five document images per class. We have chosen the different types so that they cover different document layout schemes and contents (either completely textual or having a high graphical content).

Each of these document models was printed using a color laser-jet on A4 format normal paper and we proceeded to capture them using a Google Nexus 7 tablet. We recorded small video clips of around 10 seconds for each of the 30 documents in 5 different background scenarios. The videos were recorded using Full HD 1920x1080 resolution at variable frame-rate. Since we captured the videos by hand-holding and moving the tablet, the video frames present realistic distortions such as focus and motion blur, perspective, change of illumination and even partial occlusions of the document pages. Summarizing, up to now, the database consists of 150 video clips comprising around 24.000 frames.

We ground-truthed this collection by annotating the quadrilateral coordinates of the document position for each frame in the collection.

The associated dataset, like this new version, are licensed under a Creative Commons Attribution 4.0 International License <http://creativecommons.org/licenses/by/4.0/>.

Original author attribution should be given by citing the following conference paper: Jean-Christophe Burie, Joseph Chazalon, Mickaël Coustaty, Sébastien Eskenazi, Muhammad Muzzamil Luqman, Maroua Mehri, Nibal Nayef, Jean-Marc OGIER, Sophea Prum and Marçal Rusinol: “ICDAR2015 Competition on Smartphone Document Capture and OCR (SmartDoc)”, In 13th International Conference on Document Analysis and Recognition (ICDAR), 2015.

## About this new version
This new version contains the same images and the same ground truth, but in a format which makes training and testing algorithms easier. We also tried to better identify the tasks researchers can test their methods against using this dataset. Regarding the format, video files were converted to series of images, and ground truth files were converted to a CSV file. Image for the models were also added.

A Python wrapper to facilitate data loading is also available at https://github.com/jchazalon/smartdoc15-ch1-pywrapper.
**If you use Python, we recommend you check the wrapper's documentation directly to use this dataset.**

## Tasks
Here are the 3 main tasks which you can test your methods against using this dataset:
 1. **Segmentation**: this is the original task.
    Inputs are video frames, and expected output is a composed of the coordinated of the four corners of the document image in each frame (top left, bottom left, bottom right and top right).
    The evaluation is performed by computing the intersection over union ("IoU" or also "Jaccard index") of the expected document region and the found region. The tricky thing is that the coordinates are projected to the document referential in order to allow comparisons between different frames and different document models.
    The original evaluation code is available at https://github.com/jchazalon/smartdoc15-ch1-eval, and the Python wrapper also contains an implementation using the new data format.
 2. **Model classification**: this is a new task.
    Inputs are video frames, and expected output is the identifier of the document model represented in each frame.
    There are 30 models named "datasheet001", "datasheet002", ..., "tax005".
    The evaluation is performed as any multi-class classification task.
 3. **Model type classification**: this is a new task.
    Inputs are video frames, and expected output is the identifier of the document model **type** represented in each frame.
    There are 6 models types, each having 5 members, named "datasheet", "letter", "magazine", "paper", "patent" and "tax".
    The evaluation is performed as any multi-class classification task.
    
We also provide model images to allow researchers to experiment methods with more prior knowledge on the expected document images.

**Warning:** the dataset is not balanced for tasks 2 and 3.

Frame count for each video sample, per background:

    bg_name       background01  background02  background03  background04  background05    All
    model_name
    datasheet001           235           222           215           164            97    933
    datasheet002           199           195           230           168            84    876
    datasheet003           210           201           184           160            94    849
    datasheet004           201           206           185           169            92    853
    datasheet005           235           210           209           143            83    880
    letter001              194           214           192           149            99    848
    letter002              200           192           189           145            97    823
    letter003              206           248           201           149            88    892
    letter004              211           187           176           141            84    799
    letter005              201           217           201           149           100    868
    magazine001            212           206           197           154            90    859
    magazine002            227           200           221           142            82    872
    magazine003            205           187           195           168            80    835
    magazine004            223           226           183           137            81    850
    magazine005            192           168           179           153            87    779
    paper001               197           261           185           123            78    844
    paper002               211           212           192           135            85    835
    paper003               205           214           195           140            79    833
    paper004               204           180           203           119            73    779
    paper005               187           197           199           131            92    806
    patent001              188           164           211           128            91    782
    patent002              193           167           199           126            85    770
    patent003              201           182           196           129            88    796
    patent004              223           210           189           135            80    837
    patent005              200           207           224           135            85    851
    tax001                 206           119           238           112            78    753
    tax002                 209           217           164           111            77    778
    tax003                 200           175           188           102            83    748
    tax004                 163           207           208           125            87    790
    tax005                 242           220           204           127            78    871
    All                   6180          6011          5952          4169          2577  24889

## Content details

This repository contains 3 things:
 1. the code used to generate this new dataset from the original version: it can be cloned from this repository;
 2. a gzipped tar archive containing **video frames and their metadata** (ground truth for each task): it can be downloaded from the "Releases" tab at https://github.com/jchazalon/smartdoc15-ch1-dataset/releases
 3. a gzipped tar archive containing **model images** (original and variants): it can be downloaded from the "Releases" tab at https://github.com/jchazalon/smartdoc15-ch1-dataset/releases

### Code for dataset generation
The code is composed of a simple script: `create_archives.py`.
It is used to produce the `frames.tar.gz` and the `models.tar.gz files`.
It does so by taking as input the path to the original dataset content, with the original author's structure.
It had two mode: `test`, which produces very small archives for testing purpose (used during the development of the Python Wrapper) and `complete`, which produces complete dataset archives.

Please check the integrated documentation of the `create_archives.py` file, or its online help, for more details.

### The `frames.tar.gz` archive
Please see the internal README.md file for more details.

#### Files
The file hierarchy of this archive is:
    
    frames.tar.gz
    ├── README.md
    ├── LICENCE
    ├── VERSION
    ├── original_datasets_files.txt
    ├── metadata.csv.gz
    ├── background01
    │   ├── datasheet001
    │   │   ├── frame_0001.jpeg
    │   │   ├── [...]
    │   │   └── frame_0235.jpeg
    │   ├── datasheet002
    │   │   └── [...]
    │   ├── datasheet003
    │   ├── datasheet004
    │   ├── datasheet005
    │   ├── letter001
    │   ├── letter002
    │   ├── letter003
    │   ├── letter004
    │   ├── letter005
    │   ├── magazine001
    │   ├── magazine002
    │   ├── magazine003
    │   ├── magazine004
    │   ├── magazine005
    │   ├── paper001
    │   ├── paper002
    │   ├── paper003
    │   ├── paper004
    │   ├── paper005
    │   ├── patent001
    │   ├── patent002
    │   ├── patent003
    │   ├── patent004
    │   ├── patent005
    │   ├── tax001
    │   ├── tax002
    │   ├── tax003
    │   ├── tax004
    │   └── tax005
    ├── background02
    │   └── [...]
    ├── background03
    │   └── [...]
    ├── background04
    │   └── [...]
    └── background05
        └── [...]


#### Metadata file `metadata.csv.gz`
The metadata file is a CSV file (separator: `,`, string quoting: None).
It is safe to split on `,` tokens as they do not appear elsewhere in this file.
Each row describes a video frame.
Columns are:
 - `bg_name`: Background name (example: `background01`). There are 5 backgrounds and they are named
   `background00N` with `N` between `1` and `5`.
 - `bg_id`: Background id (example: `0`), 0-indexed.
 - `model_name`: Model name (example: `datasheet001`). There are 30 models. See models description
   for more details.
 - `model_id`: Model id (example: `0`), 0-indexed. Value is between 0 and 29.
 - `modeltype_name`: Model type (example: `datasheet`). There are 6 model types. See models description
   for more details.
 - `modeltype_id`: Model type id (example: `0`), 0-indexed. Value is between 0 and 5.
 - `model_subid`: Model sub-index (example: `0`), 0-indexed. Value is between 0 and 4.
 - `image_path`: Relative path to the frame image (example: `background01/datasheet001/frame_0001.jpeg`)
   under the dataset home directory.
 - `frame_index`: Frame index (example: `1`), **1-indexed** (for compliance with the video version).
 - `model_width`: Width of the model object (example: `2100.0`). The size of the document along with the
   width / height ratio, are used to normalize the segmentation score among different models and frames.
   Here, 1 pixel represents 0.1 mm.
 - `model_height`: Height of the model object (example: `2970.0`).
 - `tl_x`: X coordinate of the top left point of the object in the current frame (example: `698.087`).
 - `tl_y`: Y coordinate of the top left point of the object in the current frame (example: `200.476`).
 - `bl_x`: X coordinate of the bottom left point of the object in the current frame (example: `692.141`).
 - `bl_y`: Y coordinate of the bottom left point of the object in the current frame (example: `891.077`).
 - `br_x`: X coordinate of the bottom right point of the object in the current frame (example: `1253.18`).
 - `br_y`: Y coordinate of the bottom right point of the object in the current frame (example: `869.656`).
 - `tr_x`: X coordinate of the top right point of the object in the current frame (example: `1178.15`).
 - `tr_y`: Y coordinate of the top right point of the object in the current frame (example: `191.515`).

Example of header + a random line:

    bg_name,bg_id,model_name,model_id,modeltype_name,modeltype_id,model_subid,image_path,frame_index,model_width,model_height,tl_x,tl_y,bl_x,bl_y,br_x,br_y,tr_x,tr_y
    background01,0,datasheet001,0,datasheet,0,0,background01/datasheet001/frame_0001.jpeg,1,2100.0,2970.0,698.087,200.476,692.141,891.077,1253.18,869.656,1178.15,191.515


### The `models.tar.gz` archive
Please see the internal README.md file for more details.

**We recommend using the `05-corrected-nexus-scaled33` if you want to use local descriptors to match the document models with their representation in the frames.**

#### Files
The file hierarchy of this archive is:

    models.tar.gz
    ├── README.md
    ├── LICENCE
    ├── VERSION
    ├── correct_perspective.m
    ├── original_datasets_files.txt
    ├── metadata.csv.gz
    ├── 01-original
    │   ├── datasheet001.png
    │   ├── [...]
    │   └── tax005.png
    ├── 02-edited
    │   ├── datasheet001.png
    │   ├── [...]
    │   └── tax005.png
    ├── 03-captured-nexus
    │   ├── datasheet001.jpg # JPG images here
    │   ├── [...]
    │   └── tax005.jpg
    ├── 04-corrected-nexus
    │   ├── datasheet001.png
    │   ├── [...]
    │   └── tax005.png
    └── 05-corrected-nexus-scaled33
        ├── datasheet001.png
        ├── [...]
        └── tax005.png

#### Metadata file `metadata.csv.gz`
The metadata file is a CSV file (separator: `,`, string quoting: None).
It is safe to split on `,` tokens as they do not appear elsewhere in this file.
Each row describes a model image.
Columns are:
 - `model_cat`: Model category (example: `05-corrected-nexus-scaled33`). There are
   5 categories:
   - `01-original`: Original images extracted from the datasets described in `original_datasets_files.txt`.
   - `02-edited`: Edited images so they fit an A4 page and all have the same shape.
   - `03-captured-nexus`: Images captured using a Google Nexus 7 tablet, trying the keep the document
     part as rectangular as possible.
   - `04-corrected-nexus`: Image with perspective roughly corrected by manually selecting the four corners
     and warping the image to the quadrilateral of the edited image using the Matlab script `correct_perspective.m`.
   - `05-corrected-nexus-scaled33`: Corrected images scaled to roughly fit the size under which documents will be
     viewed in a full HD (1080 x 1920) preview frame captured in a regular smartphone.
 - `model_name`: Name of the document (example: `datasheet001`). There are 30 documents, 5 instances of each document
   class (see below for the list of document classes). Documents are named from `001` to `005`.
 - `model_id`: Model id (example: `0`), 0-indexed. Value is between 0 and 29.
 - `modeltype_name`: Document class (example: `datasheet`). There are 6 document classes:
   - `datasheet`
   - `letter`
   - `magazine`
   - `paper`
   - `patent`
   - `tax`
 - `modeltype_id`: Model type id (example: `0`), 0-indexed. Value is between 0 and 5.
 - `model_subid`: Document sub-index (example: `1`).
 - `image_path`: Relative path to the model image (example: `05-corrected-nexus-scaled33/datasheet001.png`)
   under the dataset home directory.

Example of header + a random line:

    model_cat,model_name,model_id,modeltype_name,modeltype_id,model_subid,image_path
    02-edited,paper005,19,paper,3,4,02-edited/paper005.png

## About the version of this dataset
We add a version number to this dataset. We start at the version **2.0.0** because it differs sufficiently from the original one.

We will increase version numbers (in the form MAJOR.MINOR.PATCH) based on the following rules, inspired by http://semver.org/:
 - If the changes do not impact the parsing of the dataset nor the values it contain, but changes only documentation and related files (thus altering the checksum of the archives) then the PATCH number will be increased.
 - If the changes do not impact the parsing of the dataset, but can change the performance evaluation of the methods in a way which make the estimation of the performance closer to the truth (like ground truth fixes), then the MINOR version will be increased and the PATCH version will be reset. This indicates we "narrowed" the confidence intervals of the evaluation.
 - If the changes have an impact on either the parsing of the dataset or its content in a way which add uncertainty to the dataset (like new data), then the MAJOR number will be increased and the MINOR and PATCH number will be reset.
 
 
 
 Note that the version of the code for the generation is tied to the dataset version, and much less important, so Github releases will indicate the **dataset version**.
