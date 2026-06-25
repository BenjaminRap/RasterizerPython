from dataclasses import dataclass, field
import numpy as np
from numpy.typing import NDArray

@dataclass
class   Object3D:
    vertices : list[NDArray[np.float32]] = field(default_factory=list)
    faces : list[NDArray[np.int32]] = field(default_factory=list)

def parse_vertex_line(splitted_line : list[str]) -> NDArray[np.float32]:
    if len(splitted_line) != 3:
        raise ValueError("Invalid line format, the vertex should contains 3 floats !")
    vertex = np.array([float(component) for component in splitted_line], np.float32)
    return vertex

def parse_face_line(splitted_line : list[str]) -> NDArray[np.int32]:
    if len(splitted_line) != 3:
        raise ValueError("Invalid line format : the face should contains 3 integers !")
    face = np.array([int(vertex_index) - 1 for vertex_index in splitted_line], np.int32)
    if any(vertex_index < 0 for vertex_index in face):
        raise ValueError("Invalid vertex index in face, it should be superior to 0 !")
    return face

def parse_line(object3D : Object3D, line : str) -> None:
    splitted_line = line.split()
    if len(splitted_line) == 0:
        return ;
    if splitted_line[0] == "v":
         vertex = parse_vertex_line(splitted_line[1::])
         object3D.vertices.append(vertex)
    elif splitted_line[0] == "f":
        face = parse_face_line(splitted_line[1::])
        object3D.faces.append(face)
    else:
        raise ValueError(f"Invalid line format, it should begin with 'v' for vertex or 'f' for face !")

def parse_simple_obj_file(file_path : str) -> Object3D:
    object3D = Object3D()
    with open(file_path) as file:
        line_index = 0
        while line := file.readline():
            try:
                parse_line(object3D, line)
            except Exception as e:
                raise ValueError(f"Invalid file format at line {line_index} : {line}") from e
    vertex_indices = (vertex_index for face in object3D.faces for vertex_index in face)
    vertices_count = len(object3D.vertices)
    if any(vertex_index >= vertices_count for vertex_index in vertex_indices):
        raise ValueError(f"Invalid vertex index in face ! It should be smaller or equal to the number of vertices !")
    return object3D

if __name__ == "__main__":
    file_path = "./objects/square.simpleObj"
    try:
        object3D = parse_simple_obj_file(file_path)
        print(object3D)
    except OSError as e:
        raise RuntimeError(f"Failed to load model: {file_path}") from e
