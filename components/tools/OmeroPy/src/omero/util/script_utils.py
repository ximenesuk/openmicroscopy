#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2013 University of Dundee & Open Microscopy Environment.
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""
Utility methods for dealing with scripts.
"""

import logging
import os
import warnings

from struct import unpack

import omero.clients
from omero.rtypes import rdouble
from omero.rtypes import rint
from omero.rtypes import rstring
from omero.rtypes import unwrap
import omero.util.pixelstypetopython as pixelstypetopython

try:
    import hashlib
    hash_sha1 = hashlib.sha1
except:
    import sha
    hash_sha1 = sha.new

# r,g,b,a colours for use in scripts.
COLOURS = {
    'Red': (255, 0, 0, 255),
    'Green': (0, 255, 0, 255),
    'Blue': (0, 0, 255, 255),
    'Yellow': (255, 255, 0, 255),
    'White': (255, 255, 255, 255), }

SU_LOG = logging.getLogger("omero.util.script_utils")


def rmdir_recursive(dir):
    for name in os.listdir(dir):
        full_name = os.path.join(dir, name)
        # on Windows, if we don't have write permission we can't remove
        # the file/directory either, so turn that on
        if not os.access(full_name, os.W_OK):
            os.chmod(full_name, 0600)
        if os.path.isdir(full_name):
            rmdir_recursive(full_name)
        else:
            os.remove(full_name)
    os.rmdir(dir)


def calcSha1(filename):
    """
    Returns a hash of the file identified by filename

    @param  filename:   pathName of the file
    @return:            The hash of the file
    """

    fileHandle = open(filename)
    h = hash_sha1()
    h.update(fileHandle.read())
    hash = h.hexdigest()
    fileHandle.close()
    return hash


def getFormat(queryService, format):
    return queryService.findByQuery(
        "from Format as f where f.value='" + format + "'", None)


def createFile(updateService, filename, mimetype=None, origFilePathName=None):
    """
    Creates an original file, saves it to the server and returns the result

    @param queryService:    The query service  E.g. session.getQueryService()
    @param updateService:   The update service E.g. session.getUpdateService()
    @param filename:        The file path and name (or name if in same folder).
                            String
    @param mimetype:        The mimetype (string) or Format object representing
                            the file format
    @param origFilePathName:       Optional path/name for the original file
    @return:                The saved OriginalFileI, as returned from the
                            server
    """

    originalFile = omero.model.OriginalFileI()
    if(origFilePathName is None):
        origFilePathName = filename
    path, name = os.path.split(origFilePathName)
    originalFile.setName(omero.rtypes.rstring(name))
    originalFile.setPath(omero.rtypes.rstring(path))
    # just in case we are passed a FormatI object
    try:
        v = mimetype.getValue()
        mt = v.getValue()
    except:
        # handle the string we expect
        mt = mimetype
    if mt:
        originalFile.mimetype = omero.rtypes.rstring(mt)
    originalFile.setSize(omero.rtypes.rlong(os.path.getsize(filename)))
    originalFile.setHash(omero.rtypes.rstring(calcSha1(filename)))
    return updateService.saveAndReturnObject(originalFile)


def uploadFile(rawFileStore, originalFile, filePath=None):
    """
    Uploads an OriginalFile to the server

    @param rawFileStore:    The Omero rawFileStore
    @param originalFile:    The OriginalFileI
    @param filePath:    Where to find the file to upload.
                        If None, use originalFile.getName().getValue()
    """
    rawFileStore.setFileId(originalFile.getId().getValue())
    fileSize = originalFile.getSize().getValue()
    increment = 10000
    cnt = 0
    if filePath is None:
        filePath = originalFile.getName().getValue()
    fileHandle = open(filePath, 'rb')
    done = 0
    while(done != 1):
        if(increment + cnt < fileSize):
            blockSize = increment
        else:
            blockSize = fileSize - cnt
            done = 1
        fileHandle.seek(cnt)
        block = fileHandle.read(blockSize)
        rawFileStore.write(block, cnt, blockSize)
        cnt = cnt + blockSize
    fileHandle.close()


def attachFileToParent(updateService, parent, originalFile,
                       description=None, namespace=None):
    """
    Attaches the original file (file) to a Project, Dataset or Image (parent)

    @param updateService:       The update service
    @param parent:              A ProjectI, DatasetI or ImageI to attach
                                the file to
    @param originalFile:        The OriginalFileI to attach
    @param description:         Optional description for the file annotation.
                                String
    @param namespace:           Optional namespace for file annotataion. String
    @return:                    The saved and returned *AnnotationLinkI
                                (* = Project, Dataset or Image)
    """
    fa = omero.model.FileAnnotationI()
    fa.setFile(originalFile)
    if description:
        fa.setDescription(omero.rtypes.rstring(description))
    if namespace:
        fa.setNs(omero.rtypes.rstring(namespace))
    if type(parent) == omero.model.DatasetI:
        l = omero.model.DatasetAnnotationLinkI()
    elif type(parent) == omero.model.ProjectI:
        l = omero.model.ProjectAnnotationLinkI()
    elif type(parent) == omero.model.ImageI:
        l = omero.model.ImageAnnotationLinkI()
    else:
        return
    # use unloaded object to avoid update conflicts
    parent = parent.__class__(parent.id.val, False)
    l.setParent(parent)
    l.setChild(fa)
    return updateService.saveAndReturnObject(l)


def uploadAndAttachFile(queryService, updateService, rawFileStore, parent,
                        localName, mimetype, description=None,
                        namespace=None, origFilePathName=None):
    """
    Uploads a local file to the server, as an Original File and attaches it to
    the parent (Project, Dataset or Image)

    @param queryService:    The query service
    @param updateService:   The update service
    @param rawFileStore:    The rawFileStore
    @param parent:          The ProjectI or DatasetI or ImageI to attach
                            file to
    @param localName:       Full Name (and path) of the file location
                            to upload. String
    @param mimetype:        The original file mimetype. E.g. "PNG". String
    @param description:     Optional description for the file annotation.
                            String
    @param namespace:       Namespace to set for the original file
    @param origFilePathName:    The /path/to/file/fileName.ext you want on the
                                server. If none, use output as name
    @return:                The originalFileLink child. (FileAnnotationI)
    """

    filename = localName
    if origFilePathName is None:
        origFilePathName = localName
    originalFile = createFile(
        updateService, filename, mimetype, origFilePathName)
    uploadFile(rawFileStore, originalFile, localName)
    fileLink = attachFileToParent(
        updateService, parent, originalFile, description, namespace)
    return fileLink.getChild()


def getObjects(conn, params):
    """
    Get the objects specified by the script parameters.
    Assume the parameters contain the keys IDs and Data_Type

    @param conn:            The :class:`omero.gateway.BlitzGateway` connection.
    @param params:          The script parameters
    @return:                The valid objects and a log message
    """

    dataType = params["Data_Type"]
    ids = params["IDs"]
    objects = list(conn.getObjects(dataType, ids))

    message = ""
    if not objects:
        message += "No %s%s found. " % (dataType[0].lower(), dataType[1:])
    else:
        if not len(objects) == len(ids):
            message += "Found %s out of %s %s%s(s). " % (
                len(objects), len(ids), dataType[0].lower(), dataType[1:])

        # Sort the objects according to the order of IDs
        idMap = dict([(o.id, o) for o in objects])
        objects = [idMap[i] for i in ids if i in idMap]

    return objects, message


def readFromOriginalFile(rawFileService, iQuery, fileId, maxBlockSize=10000):
    """
    Read the OriginalFile with fileId and return it as a string.
    @param rawFileService The RawFileService service to read the originalfile.
    @param iQuery The Query Service.
    @param fileId The id of the originalFile object.
    @param maxBlockSize The block size of each read.
    @return The OriginalFile object contents as a string
    """
    fileDetails = iQuery.findByQuery(
        "from OriginalFile as o where o.id = " + str(fileId), None)
    rawFileService.setFileId(fileId)
    data = ''
    cnt = 0
    fileSize = fileDetails.getSize().getValue()
    while(cnt < fileSize):
        blockSize = min(maxBlockSize, fileSize)
        block = rawFileService.read(cnt, blockSize)
        data = data + block
        cnt = cnt + blockSize
    return data[0:fileSize]


def readFileAsArray(rawFileService, iQuery, fileId, row, col, separator=' '):
    """
    Read an OriginalFile with id and column separator
    and return it as an array.
    @param rawFileService The RawFileService service to read the originalfile.
    @param iQuery The Query Service.
    @param fileId The id of the originalFile object.
    @param row The number of rows in the file.
    @param col The number of columns in the file.
    @param sep the column separator.
    @return The file as an NumPy array.
    """
    from numpy import fromstring, reshape
    textBlock = readFromOriginalFile(rawFileService, iQuery, fileId)
    arrayFromFile = fromstring(textBlock, sep=separator)
    return reshape(arrayFromFile, (row, col))


def readFlimImageFile(rawPixelsStore, pixels):
    """
    Read the RawImageFlimFile with fileId and return it as an array [c, x, y]
    @param rawPixelsStore The rawPixelStore service to get the image.
    @param pixels The pixels of the image.
    @return The Contents of the image for z = 0, t = 0, all channels;
    """
    from numpy import zeros
    sizeC = pixels.getSizeC().getValue()
    sizeX = pixels.getSizeX().getValue()
    sizeY = pixels.getSizeY().getValue()
    id = pixels.getId().getValue()
    pixelsType = pixels.getPixelsType().getValue().getValue()
    rawPixelsStore.setPixelsId(id, False)
    cRange = range(0, sizeC)
    stack = zeros(
        (sizeC, sizeX, sizeY), dtype=pixelstypetopython.toNumpy(pixelsType))
    for c in cRange:
        plane = downloadPlane(rawPixelsStore, pixels, 0, c, 0)
        stack[c, :, :] = plane
    return stack


def downloadPlane(rawPixelsStore, pixels, z, c, t):
    """
    Download the plane [z,c,t] for image pixels.
    Pixels must have pixelsType loaded.
    N.B. The rawPixelsStore must have already been initialised by setPixelsId()
    @param rawPixelsStore The rawPixelStore service to get the image.
    @param pixels The pixels of the image.
    @param z The Z-Section to retrieve.
    @param c The C-Section to retrieve.
    @param t The T-Section to retrieve.
    @return The Plane of the image for z, c, t
    """
    from numpy import array
    rawPlane = rawPixelsStore.getPlane(z, c, t)
    sizeX = pixels.getSizeX().getValue()
    sizeY = pixels.getSizeY().getValue()
    pixelType = pixels.getPixelsType().getValue().getValue()
    convertType = '>' + str(sizeX * sizeY) + \
        pixelstypetopython.toPython(pixelType)
    convertedPlane = unpack(convertType, rawPlane)
    numpyType = pixelstypetopython.toNumpy(pixelType)
    remappedPlane = array(convertedPlane, numpyType)
    remappedPlane.resize(sizeY, sizeX)
    return remappedPlane


def getPlaneFromImage(imagePath, rgbIndex=None):
    """
    Reads a local image (E.g. single plane tiff)
    and returns it as a numpy 2D array.

    @param imagePath   Path to image.
    """
    from numpy import asarray
    try:
        from PIL import Image  # see ticket:2597
    except ImportError:
        import Image  # see ticket:2597

    i = Image.open(imagePath)
    a = asarray(i)
    if rgbIndex is None:
        return a
    else:
        return a[:, :, rgbIndex]


def uploadDirAsImages(sf, queryService, updateService,
                      pixelsService, path, dataset=None):
    """
    Reads all the images in the directory specified by 'path' and
    uploads them to OMERO as a single
    multi-dimensional image, placed in the specified 'dataset'
    Uses regex to determine the Z, C, T position of each image by name,
    and therefore determines sizeZ, sizeC, sizeT of the new Image.

    @param path     the path to the directory containing images.
    @param dataset  the OMERO dataset, if we want to put images somewhere.
                    omero.model.DatasetI
    """

    import re
    from numpy import zeros

    regex_token = re.compile(r'(?P<Token>.+)\.')
    regex_time = re.compile(r'T(?P<T>\d+)')
    regex_channel = re.compile(r'_C(?P<C>.+?)(_|$)')
    regex_zslice = re.compile(r'_Z(?P<Z>\d+)')

    # assume 1 image in this folder for now.
    # Make a single map of all images. key is (z,c,t). Value is image path.
    imageMap = {}
    channelSet = set()
    tokens = []

    # other parameters we need to determine
    sizeZ = 1
    sizeC = 1
    sizeT = 1
    zStart = 1      # could be 0 or 1 ?
    tStart = 1

    fullpath = None

    rgb = False
    # process the names and populate our imagemap
    for f in os.listdir(path):
        fullpath = os.path.join(path, f)
        tSearch = regex_time.search(f)
        cSearch = regex_channel.search(f)
        zSearch = regex_zslice.search(f)
        tokSearch = regex_token.search(f)

        if f.endswith(".jpg"):
            rgb = True

        if tSearch is None:
            theT = 0
        else:
            theT = int(tSearch.group('T'))

        if cSearch is None:
            cName = "0"
        else:
            cName = cSearch.group('C')

        if zSearch is None:
            theZ = 0
        else:
            theZ = int(zSearch.group('Z'))

        channelSet.add(cName)
        sizeZ = max(sizeZ, theZ)
        zStart = min(zStart, theZ)
        sizeT = max(sizeT, theT)
        tStart = min(tStart, theT)
        if tokSearch is not None:
            tokens.append(tokSearch.group('Token'))
        imageMap[(theZ, cName, theT)] = fullpath

    colourMap = {}
    if not rgb:
        channels = list(channelSet)
        # see if we can guess what colour the channels should be, based on
        # name.
        for i, c in enumerate(channels):
            if c == 'rfp':
                colourMap[i] = COLOURS["Red"]
            if c == 'gfp':
                colourMap[i] = COLOURS["Green"]
    else:
        channels = ("red", "green", "blue")
        colourMap[0] = COLOURS["Red"]
        colourMap[1] = COLOURS["Green"]
        colourMap[2] = COLOURS["Blue"]

    sizeC = len(channels)

    # use the common stem as the image name
    imageName = os.path.commonprefix(tokens).strip('0T_')
    description = "Imported from images in %s" % path
    SU_LOG.info("Creating image: %s" % imageName)

    # use the last image to get X, Y sizes and pixel type
    if rgb:
        plane = getPlaneFromImage(fullpath, 0)
    else:
        plane = getPlaneFromImage(fullpath)
    pType = plane.dtype.name
    # look up the PixelsType object from DB
    # omero::model::PixelsType
    pixelsType = queryService.findByQuery(
        "from PixelsType as p where p.value='%s'" % pType, None)
    if pixelsType is None and pType.startswith("float"):    # e.g. float32
        # omero::model::PixelsType
        pixelsType = queryService.findByQuery(
            "from PixelsType as p where p.value='%s'" % "float", None)
    if pixelsType is None:
        SU_LOG.warn("Unknown pixels type for: %s" % pType)
        return
    sizeY, sizeX = plane.shape

    SU_LOG.debug("sizeX: %s  sizeY: %s sizeZ: %s  sizeC: %s  sizeT: %s"
                 % (sizeX, sizeY, sizeZ, sizeC, sizeT))

    # code below here is very similar to combineImages.py
    # create an image in OMERO and populate the planes with numpy 2D arrays
    channelList = range(sizeC)
    imageId = pixelsService.createImage(
        sizeX, sizeY, sizeZ, sizeT, channelList,
        pixelsType, imageName, description)
    params = omero.sys.ParametersI()
    params.addId(imageId)
    pixelsId = queryService.projection(
        "select p.id from Image i join i.pixels p where i.id = :id",
        params)[0][0].val

    rawPixelStore = sf.createRawPixelsStore()
    rawPixelStore.setPixelsId(pixelsId, True)
    try:
        for theC in range(sizeC):
            minValue = 0
            maxValue = 0
            for theZ in range(sizeZ):
                zIndex = theZ + zStart
                for theT in range(sizeT):
                    tIndex = theT + tStart
                    if rgb:
                        c = "0"
                    else:
                        c = channels[theC]
                    if (zIndex, c, tIndex) in imageMap:
                        imagePath = imageMap[(zIndex, c, tIndex)]
                        if rgb:
                            SU_LOG.debug(
                                "Getting rgb plane from: %s" % imagePath)
                            plane2D = getPlaneFromImage(imagePath, theC)
                        else:
                            SU_LOG.debug("Getting plane from: %s" % imagePath)
                            plane2D = getPlaneFromImage(imagePath)
                    else:
                        SU_LOG.debug(
                            "Creating blank plane for .",
                            theZ, channels[theC], theT)
                        plane2D = zeros((sizeY, sizeX))
                    SU_LOG.debug(
                        "Uploading plane: theZ: %s, theC: %s, theT: %s"
                        % (theZ, theC, theT))

                    uploadPlane(rawPixelStore, plane2D, theZ, theC, theT)
                    minValue = min(minValue, plane2D.min())
                    maxValue = max(maxValue, plane2D.max())
            pixelsService.setChannelGlobalMinMax(
                pixelsId, theC, float(minValue), float(maxValue))
            rgba = None
            if theC in colourMap:
                rgba = colourMap[theC]
            try:
                renderingEngine = sf.createRenderingEngine()
                resetRenderingSettings(
                    renderingEngine, pixelsId, theC, minValue, maxValue, rgba)
            finally:
                renderingEngine.close()
    finally:
        rawPixelStore.close()

    # add channel names
    pixels = pixelsService.retrievePixDescription(pixelsId)
    i = 0
    # c is an instance of omero.model.ChannelI
    for c in pixels.iterateChannels():
        # returns omero.model.LogicalChannelI
        lc = c.getLogicalChannel()
        lc.setName(rstring(channels[i]))
        updateService.saveObject(lc)
        i += 1

    # put the image in dataset, if specified.
    if dataset:
        link = omero.model.DatasetImageLinkI()
        link.parent = omero.model.DatasetI(dataset.id.val, False)
        link.child = omero.model.ImageI(imageId, False)
        updateService.saveAndReturnObject(link)

    return imageId


def uploadCecogObjectDetails(updateService, imageId, filePath):
    """
    Parses a single line of cecog output and saves as a roi.

    Adds a Rectangle (particle) to the current OMERO image, at point x, y.
    Uses the self.image (OMERO image) and self.updateService
    """

    objects = {}
    roi_ids = []

    import fileinput
    for line in fileinput.input([filePath]):

        theT = None
        x = None
        y = None

        parts = line.split("\t")
        names = ("frame", "objID", "primaryClassLabel", "primaryClassName",
                 "centerX", "centerY", "mean", "sd", "secondaryClassabel",
                 "secondaryClassName", "secondaryMean", "secondarySd")
        values = {}
        for idx, name in enumerate(names):
            if len(parts) >= idx:
                values[name] = parts[idx]

        frame = values["frame"]
        try:
            frame = long(frame)
        except ValueError:
            SU_LOG.debug("Non-roi line: %s " % line)
            continue

        theT = frame - 1
        objID = values["objID"]
        className = values["primaryClassName"]
        x = float(values["centerX"])
        y = float(values["centerY"])

        description = ""
        for name in names:
            description += ("%s=%s\n" % (name, values.get(name, "(missing)")))

        if theT and x and y:
            SU_LOG.debug(
                "Adding point '%s' to frame: %s, x: %s, y: %s"
                % (className, theT, x, y))
            try:
                shapes = objects[objID]
            except KeyError:
                shapes = []
                objects[objID] = shapes
            shapes.append((theT, className, x, y, values, description))

    for object, shapes in objects.items():

        # create an ROI, add the point and save
        roi = omero.model.RoiI()
        roi.setImage(omero.model.ImageI(imageId, False))
        roi.setDescription(omero.rtypes.rstring("objID: %s" % object))

        # create and save a point
        for shape in shapes:

            theT, className, x, y, values, description = shape

            point = omero.model.PointI()
            point.cx = rdouble(x)
            point.cy = rdouble(y)
            point.theT = rint(theT)
            point.theZ = rint(0)  # Workaround for shoola:ticket:1596
            if className:
                point.setTextValue(rstring(className))    # for display only

            # link the point to the ROI and save it
            roi.addShape(point)

        roi = updateService.saveAndReturnObject(point)
        roi_ids.append(roi.id.val)

    return roi_ids


def uploadPlane(rawPixelsStore, plane, z, c, t):
    """
    Upload the plane to the server attching it to the current z,c,t
    of the already instantiated rawPixelStore.
    @param rawPixelsStore The rawPixelStore which is already pointing
                        to the data.
    @param plane The data to upload
    @param z The Z-Section of the plane.
    @param c The C-Section of the plane.
    @param t The T-Section of the plane.
    """
    byteSwappedPlane = plane.byteswap()
    convertedPlane = byteSwappedPlane.tostring()
    rawPixelsStore.setPlane(convertedPlane, z, c, t)


def resetRenderingSettings(renderingEngine, pixelsId, cIndex,
                           minValue, maxValue, rgba=None):
    """
    Simply resests the rendering settings for a pixel set,
    according to the min and max values
    The rendering engine does NOT have to be primed with pixelsId,
    as that is handled by this method.

    @param renderingEngine        The OMERO rendering engine
    @param pixelsId        The Pixels ID
    @param minValue        Minimum value of rendering window
    @param maxValue        Maximum value of rendering window
    @param rgba            Option to set the colour of the channel.
                           (r,g,b,a) tuple.
    """

    renderingEngine.lookupPixels(pixelsId)
    if not renderingEngine.lookupRenderingDef(pixelsId):
        renderingEngine.resetDefaults()
        if rgba is None:
            # probably don't want E.g. single channel image to be blue!
            rgba = COLOURS["White"]

    if not renderingEngine.lookupRenderingDef(pixelsId):
        raise Exception("Still No Rendering Def")

    renderingEngine.load()
    renderingEngine.setChannelWindow(cIndex, float(minValue), float(maxValue))
    if rgba:
        red, green, blue, alpha = rgba
        renderingEngine.setRGBA(cIndex, red, green, blue, alpha)
    renderingEngine.saveCurrentSettings()


def toCSV(list):
    """
    Convert a list to a Comma Separated Value string.
    @param list The list to convert.
    @return See above.
    """
    lenList = len(list)
    cnt = 0
    str = ""
    for item in list:
        str = str + item
        if(cnt < lenList - 1):
            str = str + ","
        cnt = cnt + 1
    return str


def toList(csvString):
    """
    Convert a csv string to a list of strings
    @param csvString The CSV string to convert.
    @return See above.
    """
    list = csvString.split(',')
    for index in range(len(list)):
        list[index] = list[index].strip()
    return list
