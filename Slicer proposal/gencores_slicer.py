#!/usr/bin/env python
import math
import struct
import numpy as np

# class for each point of a triangle
class Point:
    def __init__(self, x_, y_, z_):
        self.x = x_
        self.y = y_
        self.z = z_
    def __repr__(self):
        return str(self.x)+", "+str(self.y)+", "+str(self.z)

# class for triangle, contain point and the norm of the triangle, norm isn't used
class Triangle:
    def __init__(self, p0_, p1_, p2_, norm_):
        self.p = [p0_, p1_, p2_]
        self.norm = norm_
    def __repr__(self):
        return "\n ["+self.p[0].__str__()+"] \t["+self.p[1].__str__()+"] \t["+self.p[2].__str__()+"]"

# class for 3d object, contains some info about it
class Object:
    def __init__(self):
        self.layer_size = 10
        self.path_width = 10
        self.triangles = []
        self.z_min = +100
        self.z_max = -100
        
# Format of binary .stl file
# UINT8[80]    – Header                 -     80 bytes                           
# UINT32       – Number of triangles    -      4 bytes

# foreach triangle                      - 50 bytes:
#     REAL32[3] – Normal vector             - 12 bytes
#     REAL32[3] – Vertex 1                  - 12 bytes
#     REAL32[3] – Vertex 2                  - 12 bytes
#     REAL32[3] – Vertex 3                  - 12 bytes
#     UINT16    – Attribute byte count      -  2 bytes
# end
def read_stl(filename, objet):

    triangle_dtype = np.dtype([
            ('Normal', np.float32, (3,)),
            ('Vertex1', np.float32, (3,)),
            ('Vertex2', np.float32, (3,)),
            ('Vertex3', np.float32, (3,)),
            ('Attribute', '<i2', (1,)),
        ])

    with open(filename, "rb") as f:
        Header = f.read(80)
        N_triangles = struct.unpack('i', f.read(4))[0]

        raw_triangles = np.zeros((N_triangles,), dtype=triangle_dtype)
        
        for i in range(0, N_triangles, 10):
            d = np.fromfile(f, dtype=triangle_dtype, count=10)
            raw_triangles[i:i+len(d)] = d

    triangles = []
    for raw_triangle in raw_triangles :
        p0 = Point(raw_triangle['Vertex1'][0],raw_triangle['Vertex1'][1],raw_triangle['Vertex1'][2])
        p1 = Point(raw_triangle['Vertex2'][0],raw_triangle['Vertex2'][1],raw_triangle['Vertex2'][2])
        p2 = Point(raw_triangle['Vertex3'][0],raw_triangle['Vertex3'][1],raw_triangle['Vertex3'][2])
        triangle = Triangle(p0, p1, p2,raw_triangle['Normal'][0])
        objet.triangles.append(triangle)

    return

# find the minimum et maximum Z heights of the object
def Z_min_max(objet):
    z_min = +100
    z_max = -100

    for triangle in objet.triangles:
        maximum = max(triangle.p[0].z, triangle.p[1].z, triangle.p[2].z)
        minimum = min(triangle.p[0].z, triangle.p[1].z, triangle.p[2].z)
        
        if maximum > objet.z_max:
            objet.z_max = maximum
        if minimum < objet.z_min:
            objet.z_min = minimum

    return
    
# calculate intersection between the layer plane and mesh triangles
def calculate_intersect(triangle, layer, outer, objet):
    t = triangle
    n = 0
    line = []
    for point in triangle.p:
        if point.z == layer :
            line.append((point.x, point.y))
            n += 1
    
    couples = [(0,1), (1,0), (0,2), (2,0), (1,2), (2,1)]
    if n < 2:
        for i,j in couples:
            if t.p[i].z < layer and t.p[j].z >layer :
                coef = (t.p[i].z + layer)/t.p[j].z
                x = (t.p[j].x - t.p[i].x) * coef + t.p[i].x
                y = (t.p[j].y - t.p[i].y) * coef + t.p[i].y
                line.append((x, y))
                n +=1
    
    if n == 3 : #if a triangles is completly parallel to the plane, we didn't need his segments
        pass
        # print(line, layer)
        # outer.append([line[0], line[1]])
        # outer.append([line[0], line[2]])
        # outer.append([line[1], line[2]])
        
    elif n != 0:
        outer.append(line)

# with external segments, we build outer or internal perimeters
def solve_perimeters(outer):
    perimeters = []
    prev_len = 0
    while len(outer) > 0:
        perimeter = []
        perimeter.append(outer.pop(0))
        while perimeter[-1][-1] != perimeter[0][0] and prev_len != len(perimeter):
            prev_len = len(perimeter)
            for i in range(len(outer)):
                p1,p2 = outer[i]
                if p1 == perimeter[-1][-1]:
                    perimeter.append(outer.pop(i))
                    break
                if p2 == perimeter[-1][-1]:
                    perimeter.append(outer.pop(i)[::-1])
                    break
        perimeters.append(perimeter)
    return perimeters

# return the external perimeter and left internals in place
def distiction_intern_extern(perimeters):
    maximums = []
    external_perimeter = []
    i = 0
    for perimeter in perimeters:
        maximums.append(-100)
        for line in perimeter:
            if line[0][0] > maximums[i]:
                maximums[i] = line[0][0]
        i +=1
    external_perimeter =  perimeters.pop(maximums.index(max(maximums)))
    return external_perimeter

# calculate intersection and then possible perimeters for each layer height
def calculate_layers(objet):
    N_layers =int((objet.z_max - objet.z_min) / objet.layer_size)+1
    layers_externals = []
    layers_internals = []
    
    for layer in range(0, N_layers):
        outer = []
        outer_clean = []
        height = layer*objet.layer_size
        for triangle in objet.triangles:
            calculate_intersect(triangle, height, outer, objet)
        outer = [line for line in outer if len(line) ==2]
        [outer_clean.append(line) for line in outer if (line not in outer_clean) and (line[::-1] not in outer_clean) and (line[0] != line[1])]
        perimeters = solve_perimeters(outer_clean)
        external = distiction_intern_extern(perimeters)
        layers_internals.append(perimeters)
        layers_externals.append(external)
    
    return (layers_externals, layers_internals)

# slicer function
def slicer(geom_filename, settings):
    contour_segments = []
    filling_segments = []
    objet = Object()
    objet.path_width =settings["path_fill_width"]
    objet.layer_size = settings["path_layer_size"]
    read_stl(geom_filename, objet)
    Z_min_max(objet)
    layers = calculate_layers(objet)
    print("Internal perimeter layer 4:\n", layers[1][4])
    print("External perimeter layer 4:\n", layers[0][4])
    print("Simple cube example with a round hole in the center")
    # To do : the conversion between obtained perimeters and gencores formalism
    # To do : generate the toolpath
    return (contour_segments, filling_segments)


def main():
    
    path = "/Users/remibouteiller/Documents/ETUDES/M2/STAGE/GENCORES/GENCORES-software_test/"
    stlfile = path+"cube2.stl"
    settings = {"infill_origin": (0, 0), "path_fill_width": 1, "path_layer_size": 2}
    slicer(stlfile, settings)


if __name__ == '__main__':
    main()