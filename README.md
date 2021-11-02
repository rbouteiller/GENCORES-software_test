
# Python Slicer module


Develop a Python module that slice a geometry into contiguous segments, starting by the outer perimeter of the part and then filling the inside.

For details please visit:
https://github.com/rbouteiller/GENCORES-software_test (private repository)

---

## Slicing Process

![](https://hedgedoc.bouteiller.org/uploads/upload_2c9ef91b56a6811e1fa9745b6dc020c3.png)

---


## STL parsing

STL files describe only the surface geometry of a three-dimensional object as a mesh of triangles.
<div style="text-align:left">
Two types
	
  ``` 
ASCII STL :			Binary STL :
	
facet normal ni nj nk		foreach triangle 
    outer loop				REAL32[3] – Normal 	
        vertex v1x v1y v1z		REAL32[3] – Vertex 1
        vertex v2x v2y v2z		REAL32[3] – Vertex 2
        vertex v3x v3y v3z		REAL32[3] – Vertex 3
    endloop				UINT16    – Attrib
endfacet			end
```
The binary STL format is the most used today
</div>

----

### Parser code

```python=
def read_stl(filename, objet):
    with open(filename, "rb") as f:
        Header = f.read(80)
        N_triangles = struct.unpack('i', f.read(4))[0]
        for i in range(0, N_triangles):
            np.fromfile(f, np.float32, 3)
            p0 = Point(np.fromfile(f, np.float32, 3))
            p1 = Point(np.fromfile(f, np.float32, 3))
            p2 = Point(np.fromfile(f, np.float32, 3))
            np.fromfile(f, '<i2', 1)
            triangle = Triangle(p0, p1, p2)
            objet.triangles.append(triangle)
    return
```


---

## Slicing steps

1. Finding the height of the object
2. Calculate the number of slices
3. For each slice : 
	1. Calculate intersection between layer plane and the triangles
	2. Resolve the different perimeters (External and if existing internal)
	3. Extract the contour perimeter
	4. Not done : Define a toolpath

----

### Object height
```python=
# find the minimum et maximum Z heights of the object
# Detemine the number of layers
for t in objet.triangles:
    z_max = max(t.p[0].z, t.p[1].z, t.p[2].z, z_max)
    z_min = min(t.p[0].z, t.p[1].z, t.p[2].z, z_min)
N_layers =int((z_max - z_min) / layer_size)+1
```

----

### Intersection

<div class="stretch">
	
```python=
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
    if n == 3 : 
        pass
    elif n != 0:
        outer.append(line)
```
	
</div>
    


----

### Perimeters solving
```python=
# build perimeters with segments
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
```

----

```python=
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
```

---

## Intersection

### 3 cases : 
- 3 Vertex of a triangle are at the layer level
- 2 Vertex of a triangle are at the layer level
- Triangle intersect the layer level

----

![](https://hedgedoc.bouteiller.org/uploads/upload_2b8623c0d22231cb106f7195be4169e6.png)

----

![](https://hedgedoc.bouteiller.org/uploads/upload_c69a9d48fc83c127a32ffa53694eab65.png)

---

## Perimeters distinction

![](https://hedgedoc.bouteiller.org/uploads/upload_5d80ddb633b2dda721e768d3003e10c4.png)

---

## Formalism clarification

<div style="text-align:left">
Input : - Add layer height ?

Output : 
In some cases the toolpath cannot be continuous.
- Replace `contour_segments` with `external_contour_segments` and `internal_contour_segments[]`
- Replace `filling_segments` with `filling_segments[]`
</div>

---

## To do

<ol>
	<span><li class> From different perimeters, define a toolpath (Use of shapely ?) </li><!-- .element: class="fragment" data-fragment-index="1" --></span> 
	<span><li class> Solve the first and last layer problem </li><!-- .element: class="fragment" data-fragment-index="2" --></span>
	<span><li class> Use Gencores formalism for input/output </li><!-- .element: class="fragment" data-fragment-index="3" --></span>
	<span><li class> Some variable names are not in english </li><!-- .element: class="fragment" data-fragment-index="4" --></span>
	</ol>

---


