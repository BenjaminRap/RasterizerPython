from dataclasses import dataclass
from math import cos, sin

from numpy.typing import NDArray
from pygame import Surface
import numpy as np

from parseSimpleObjFile import Object3D

@dataclass
class   Transform:
    position: NDArray[np.float32]
    scale: NDArray[np.float32]
    rotation: NDArray[np.float32]

@dataclass
class   GameObject:
    object3D : Object3D
    transform : Transform

@dataclass
class   Camera:
    transform: Transform
    fov : float
    near : float
    far : float

def rasterize(object3D : Object3D, screen : Surface, depth_buffer : NDArray[np.float32]):
    print("rasterize")

def getModelViewProjectionMatrix(transform : Transform):
    pos = transform.position
    position_matrix = np.array([[1, 0, 0, 0],
                                [0, 1, 0, 0],
                                [0, 0, 1, 0],
                                [pos[0], pos[1], pos[2], 1]])
    scale = transform.scale
    scale_matrix = np.array([[scale[0], 0, 0, 0],
                             [0, scale[1], 0, 0],
                             [0, 0, scale[2], 0],
                             [0, 0, 0, 1]])
    rot_x = transform.rotation[0]
    rotation_x_matrix = np.array([[1, 0, 0, 0],
                                  [0, cos(rot_x), sin(rot_x), 0],
                                  [0, -sin(rot_x), cos(rot_x), 0],
                                  [0, 0, 0, 1]])
    rot_y = transform.rotation[1]
    rotation_y_matrix = np.array([[cos(rot_y), 0, -sin(rot_y), 0],
                                  [0, 1, 0, 0],
                                  [sin(rot_y), 0, cos(rot_y), 0],
                                  [0, 0, 0, 1]])
    rot_z = transform.rotation[2]
    rotation_z_matrix = np.array([[cos(rot_z), sin(rot_z), 0, 0],
                                  [-sin(rot_z), cos(rot_z), 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])
    return scale_matrix @ rotation_x_matrix @ rotation_y_matrix @ rotation_z_matrix @ position_matrix


if __name__ == "__main__":
    transform = Transform(np.array([0, 0, 0]), np.array([1, 1, 1]), np.array([0, 0, 0]))
    model_view_projection = getModelViewProjectionMatrix(transform)
    vertex = np.array([1, 10, 5, 1])
    worldVertex = vertex @ model_view_projection
    print(f"transform : {transform}")
    print(f"vertex : {vertex}")
    print(f"worldVertex : {worldVertex}")

