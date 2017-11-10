from . import piexif
import os.path
from arcgis.geometry import Point, SpatialReference
from arcgis.features import SpatialDataFrame
from uuid import uuid4


def _dms_to_dd(dms):
    """
    Utility function assisting with converting the degrees, minutes, and seconds found in exif data to decimal degrees.
    :param dms: Degrees, minutes, and seconds from
    :return: Decimal degrees float.
    """
    return dms[0][0] / dms[0][1] + dms[1][0] / dms[1][1] / 60 + dms[2][0] / dms[2][1] / 3600


class Photo(object):
    """
    Photo object.
    """
    def __init__(self, path_to_photo):
        self.exif = piexif.load(path_to_photo)
        self.gps = self.exif['GPS'] if 'GPS' in self.exif else None
        self.x = None
        self.y = None
        self.uuid = uuid4().hex
        self.name = os.path.basename(path_to_photo).split('.')[0]
        self.path = path_to_photo

    def _get_y(self):
        """
        Extract the Y coordinate from the GPS tags.
        :return: Decimal degrees.
        """
        # get the y value
        y = _dms_to_dd(self.gps[2])

        # check to ensure the x value is logical, between the north and south pole in degrees
        if y > 100:
            return None
        else:

            # set positive or negative based on hemisphere
            return -y if self.gps[1] == b'S' else y

    def _get_x(self):
        """
        Extract the X coordinate from the GPS tags.
        :return: Decimal degrees.
        """
        # get the x value
        x = _dms_to_dd(self.gps[4])

        # check to ensure the y value is logical, between the prime meridian and the international date line
        if x > 190:
            return None
        else:

            # set positive or negateive based on hemisphere
            return -x if self.gps[3] == b'W' else x

    @property
    def point(self):
        """
        Property to return point geometry if available.
        :return: Point geometry object if possible.
        """
        if self.x and self.y:
            return Point(x=self.x, y=self.y, sr=SpatialReference(wkid=4326))
        else:
            return None

    @property
    def dictionary(self):
        """
        Provide a representation of the point as a dictionary.
        :return: Dictionary of point properties.
        """
        return {
            'name': self.name,
            'path': self.path,
            'uuid': self.uuid,
            'SHAPE': self.point
        }


class PhotoCollection(object):
    """
    Spatial Data Frame with photos!
    """
    geometry_field_name = 'SHAPE'

    def __init__(self, path_to_directory_containing_photos):
        self.source_directory = path_to_directory_containing_photos
        self._sdf = self._get_sdf(path_to_directory_containing_photos)

    def _get_sdf(self, path_directory):
        """
        Load the photos into a spatial data frame.
        :param path_directory: Path to directory containing photos.
        :return: SpatialDataFrame
        """
        # load up the photos as a list of dictionaries
        photo_list = [Photo(file).dictionary for file in os.listdir(path_directory) if file.lower().endswith('.jpg')]

        # convert this list of dictionaries into a SpatialDataFrame
        photo_sdf = SpatialDataFrame(photo_list)

        # set the geometry field property
        photo_sdf.set_geometry('SHAPE', inplace=True, sr=SpatialReference(wkid=4326))

        # reindex all the data and return the result
        return photo_sdf.reset_index(drop=True)

    @property
    def spatialdataframe(self):
        """
        Return the photo collection as a SpatialDataFrame
        :return: SpatialDataFrame
        """
        return self._sdf

    @property
    def featureset(self):
        """
        Return the photo collection as a FeatureSet
        :return: FeatureSet
        """
        return self._sdf.to_featureset()

    def to_csv(self, output_path):
        """
        Return the photo collection as a CSV
        :param output_path: Path to where CSV will be saved.
        :return: Path to csv.
        """
        return self._sdf.to_csv(output_path)

    def to_featureclass(self, output_path):
        """
        Return the photo collection as a feature class.
        :param output_path: Path to where feature class will be saved.
        :return: Path to feature class.
        """
        return self._sdf.to_featureclass(os.path.dirname(output_path), os.path.basename(output_path))
