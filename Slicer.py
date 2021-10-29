#!/usr/bin/env python
import math
import struct
import numpy as np

def read_stl(filename):
    with open(filename) as f:
        Header = f.read(80)
        nn = f.read(4)
        Numtri = struct.unpack('i', nn)[0]
        record_dtype = np.dtype([
            ('Normals', np.float32, (3,)),
            ('Vertex1', np.float32, (3,)),
            ('Vertex2', np.float32, (3,)),
            ('Vertex3', np.float32, (3,)),
            ('atttr', '<i2', (1,)),
        ])
        data = np.zeros((Numtri,), dtype=record_dtype)
        for i in xrange(0, Numtri, 10):
            d = np.fromfile(f, dtype=record_dtype, count=10)
            data[i:i+len(d)] = d

    #normals = data['Normals']
    v1 = data['Vertex1']
    v2 = data['Vertex2']
    v3 = data['Vertex3']
    points = np.hstack(((v1[:, np.newaxis, :]), (v2[:, np.newaxis, :]), (v3[:, np.newaxis, :])))
    return points

def main():
    path = "/Users/remibouteiller/Downloads/slicing_algorithm-master/"
    stlfile = path+"xyzCalibration_cube.stl"
    print(read_stl(stlfile))





if __name__ == '__main__':
    main()







# import numpy as np
# import struct


# def read_stl(filename):
#     with open(filename) as f:
#         Header = f.read(80)
#         nn = f.read(4)
#         Numtri = struct.unpack('i', nn)[0]
#         record_dtype = np.dtype([
#             ('Normals', np.float32, (3,)),
#             ('Vertex1', np.float32, (3,)),
#             ('Vertex2', np.float32, (3,)),
#             ('Vertex3', np.float32, (3,)),
#             ('atttr', '<i2', (1,)),
#         ])
#         data = np.zeros((Numtri,), dtype=record_dtype)
#         for i in xrange(0, Numtri, 10):
#             d = np.fromfile(f, dtype=record_dtype, count=10)
#             data[i:i+len(d)] = d

#     #normals = data['Normals']
#     v1 = data['Vertex1']
#     v2 = data['Vertex2']
#     v3 = data['Vertex3']
#     points = np.hstack(((v1[:, np.newaxis, :]), (v2[:, np.newaxis, :]), (v3[:, np.newaxis, :])))
#     return points


# def calc_volume(points):
#     '''
#     Calculate the volume of an stl represented in m x 3 x 3 points array. Expected that input units is mm, so that
#     output is in cubic centimeters (cc).
#     '''
#     v = points
#     volume = np.asarray([np.cross(v[i, 0, :], v[i, 1, :]).dot(v[i, 2, :]) for i in xrange(points.shape[0])])
#     return np.abs(volume.sum()/6.)/(10.**3.)


# def bounding_box(points):
#     '''
#     Calculate the bounding box edge lengths of an stl using the design coordinate system (not an object oriented bounding box),
#     expect that input coordinates are in mm.
#     '''
#     v = points
#     x = v[..., 0].flatten()
#     y = v[..., 1].flatten()
#     z = v[..., 2].flatten()
#     return (x.max()-x.min(), y.max()-y.min(), z.max()-z.min())


# def iter_calc_volume(filename):
#     with open(filename) as f:
#         Header = f.read(80)
#         nn = f.read(4)
#         Numtri = struct.unpack('i', nn)[0]
#         record_dtype = np.dtype([
#             ('Normals', np.float32, (3,)),
#             ('Vertex1', np.float32, (3,)),
#             ('Vertex2', np.float32, (3,)),
#             ('Vertex3', np.float32, (3,)),
#             ('atttr', '<i2', (1,)),
#         ])
#         volume = 0.
#         for i in xrange(0, Numtri, 1):
#             d = np.fromfile(f, dtype=record_dtype, count=1)
#             v1 = d['Vertex1'][0]
#             v2 = d['Vertex2'][0]
#             v3 = d['Vertex3'][0]
#             volume += np.cross(v1, v2).dot(v3)
#     return np.abs(volume/6.)/(10.**3.)


# def iter_calc_bounding(filename):
#     with open(filename) as f:
#         Header = f.read(80)
#         nn = f.read(4)
#         Numtri = struct.unpack('i', nn)[0]
#         record_dtype = np.dtype([
#             ('Normals', np.float32, (3,)),
#             ('Vertex1', np.float32, (3,)),
#             ('Vertex2', np.float32, (3,)),
#             ('Vertex3', np.float32, (3,)),
#             ('atttr', '<i2', (1,)),
#         ])
#         xmax = -9999
#         xmin = 9999
#         ymax = -9999
#         ymin = 9999
#         zmax = -9999
#         zmin = 9999
#         for i in xrange(0, Numtri, 1):
#             d = np.fromfile(f, dtype=record_dtype, count=1)
#             v1 = d['Vertex1']
#             v2 = d['Vertex2']
#             v3 = d['Vertex3']
#             v = np.hstack(((v1[:, np.newaxis, :]), (v2[:, np.newaxis, :]), (v3[:, np.newaxis, :])))
#             x = v[..., 0].flatten()
#             y = v[..., 1].flatten()
#             z = v[..., 2].flatten()
#             tmp_xmin = x.min()
#             tmp_xmax = x.max()
#             tmp_ymin = y.min()
#             tmp_ymax = y.max()
#             tmp_zmin = z.min()
#             tmp_zmax = z.max()
#             xmax = max((tmp_xmax, xmax))
#             xmin = min((tmp_xmin, xmin))
#             ymax = max((tmp_ymax, ymax))
#             ymin = min((tmp_ymin, ymin))
#             zmax = max((tmp_zmax, zmax))
#             zmin = min((tmp_zmin, zmin))
#     X = xmax-xmin
#     Y = ymax-ymin
#     Z = zmax-zmin
#     return (X, Y, Z)


# def test(filename):
#     points = read_stl(filename)
#     vol1 = calc_volume(points)
#     vol2 = iter_calc_volume(filename)
#     print vol1, vol2
#     assert np.isclose(vol1, vol2)  # test for equal taking into account
#                                    # floating point precision
#     bb1 = bounding_box(points)
#     bb2 = iter_calc_bounding(filename)
#     print bb1, bb2
#     assert np.isclose(bb1[0], bb2[0]) and np.isclose(bb1[1], bb2[1]) and np.isclose(bb1[2], bb2[2])

#     return True


# if __name__ == "__main__":
#     import sys
#     if sys.argv[1] == '-t':
#         test(sys.argv[2])
#         print "Passed!"
#     else:
#         filename = sys.argv[1]
#         print "Calculating the volume of %s in cc's" % (filename,)
#         print "The volume is: %f" % (iter_calc_volume(filename),)