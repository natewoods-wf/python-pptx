# encoding: utf-8

"""
Image part objects, including _Image
"""

import hashlib
import os
import posixpath

try:
    from PIL import Image as PIL_Image
except ImportError:
    import Image as PIL_Image

from StringIO import StringIO

from pptx.part import _BasePart
from pptx.spec import default_content_types
from pptx.util import Px


class _Image(_BasePart):
    """
    Return new Image part instance. *file* may be |None|, a path to a file (a
    string), or a file-like object. If *file* is |None|, no image is loaded
    and :meth:`_load` must be called before using the instance. Otherwise, the
    file referenced or contained in *file* is loaded. Corresponds to package
    files ppt/media/image[1-9][0-9]*.*.
    """
    def __init__(self, file=None):
        super(_Image, self).__init__()
        self.__filepath = None
        self.__ext = None
        if file is not None:
            self.__load_image_from_file(file)

    @property
    def ext(self):
        """
        Return file extension for this image. Includes the leading dot, e.g.
        ``'.png'``.
        """
        assert self.__ext, "_Image.__ext referenced before assigned"
        return self.__ext

    @property
    def _desc(self):
        """
        Return filename associated with this image, either the filename of the
        original image file the image was created with or a synthetic name of
        the form ``image.ext`` where ``.ext`` is appropriate to the image file
        format, e.g. ``'.jpg'``.
        """
        if self.__filepath is not None:
            return os.path.split(self.__filepath)[1]
        # return generic filename if original filename is unknown
        return 'image%s' % self.ext

    def _scale(self, width, height):
        """
        Return scaled image dimensions based on supplied parameters. If
        *width* and *height* are both |None|, the native image size is
        returned. If neither *width* nor *height* is |None|, their values are
        returned unchanged. If a value is provided for either *width* or
        *height* and the other is |None|, the dimensions are scaled,
        preserving the image's aspect ratio.
        """
        native_width_px, native_height_px = self._size
        native_width = Px(native_width_px)
        native_height = Px(native_height_px)

        if width is None and height is None:
            width = native_width
            height = native_height
        elif width is None:
            scaling_factor = float(height) / float(native_height)
            width = int(round(native_width * scaling_factor))
        elif height is None:
            scaling_factor = float(width) / float(native_width)
            height = int(round(native_height * scaling_factor))
        return width, height

    @property
    def _sha1(self):
        """Return SHA1 hash digest for image"""
        return hashlib.sha1(self._blob).hexdigest()

    @property
    def _size(self):
        """
        Return *width*, *height* tuple representing native dimensions of
        image in pixels.
        """
        image_stream = StringIO(self._blob)
        width_px, height_px = PIL_Image.open(image_stream).size
        image_stream.close()
        return width_px, height_px

    @property
    def _blob(self):
        """
        For an image, _blob is always _load_blob, image file content is not
        manipulated.
        """
        return self._load_blob

    def _load(self, pkgpart, part_dict):
        """Handle aspects of loading that are particular to image parts."""
        # call parent to do generic aspects of load
        super(_Image, self)._load(pkgpart, part_dict)
        # set file extension
        self.__ext = posixpath.splitext(pkgpart.partname)[1]
        # return self-reference to allow generative calling
        return self

    @staticmethod
    def __image_ext_content_type(ext):
        """Return the content type corresponding to filename extension *ext*"""
        if ext not in default_content_types:
            tmpl = "unsupported image file extension '%s'"
            raise TypeError(tmpl % (ext))
        content_type = default_content_types[ext]
        if not content_type.startswith('image/'):
            tmpl = "'%s' is not an image content type; ext '%s'"
            raise TypeError(tmpl % (content_type, ext))
        return content_type

    @staticmethod
    def __ext_from_image_stream(stream):
        """
        Return the filename extension appropriate to the image file contained
        in *stream*.
        """
        ext_map = {'GIF': '.gif', 'JPEG': '.jpg', 'PNG': '.png',
                   'TIFF': '.tiff', 'WMF': '.wmf'}
        stream.seek(0)
        format = PIL_Image.open(stream).format
        if format not in ext_map:
            tmpl = "unsupported image format, expected one of: %s, got '%s'"
            raise ValueError(tmpl % (ext_map.keys(), format))
        return ext_map[format]

    def __load_image_from_file(self, file):
        """
        Load image from *file*, which is either a path to an image file or a
        file-like object.
        """
        if isinstance(file, basestring):  # file is a path
            self.__filepath = file
            self.__ext = os.path.splitext(self.__filepath)[1]
            self._content_type = self.__image_ext_content_type(self.__ext)
            with open(self.__filepath, 'rb') as f:
                self._load_blob = f.read()
        else:  # assume file is a file-like object
            self.__ext = self.__ext_from_image_stream(file)
            self._content_type = self.__image_ext_content_type(self.__ext)
            file.seek(0)
            self._load_blob = file.read()
