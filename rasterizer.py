from dataclasses import dataclass
from math import ceil, cos, floor, sin
from typing import Tuple

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
    object_3d : Object3D
    transform : Transform

@dataclass
class   Camera:
    transform: Transform
    fov : float
    near : float
    far : float

@dataclass
class   BoundingBox:
    left: int
    right: int
    top: int
    bottom: int

def rasterize(game_object : GameObject, screen : Surface, depth_buffer : NDArray[np.float32]):
    for face in game_object.object_3d.faces:
        rasterize_face(face, game_object, screen, depth_buffer)

def rasterize_face(face : NDArray[np.int32], game_object : GameObject,
                   screen : Surface, depth_buffer : NDArray[np.float32]):
    screen_size = screen.get_size()
    projected_triangle : list[NDArray[np.float32]] = []
    for vertex_index in face:
        vertex = game_object.object_3d.vertices[vertex_index]
        homogeneous_vertex = np.array([vertex[0], vertex[1], vertex[2], 1])
        model_view_projection = get_model_view_matrix(game_object.transform)
        world_vertex = homogeneous_vertex @ model_view_projection
        if world_vertex[2] <= 0:
            return
        projected_vertex = get_projected_vertex(world_vertex, screen_size)
        projected_triangle.append(projected_vertex)
    bounding_box = get_bounding_box(projected_triangle, screen_size)
    for y in range(bounding_box.bottom, bounding_box.top):
        for x in range(bounding_box.left, bounding_box.right):
            if is_in_triangle(projected_triangle, x, y):
                screen.set_at((x, y), (255, 255, 255))

def is_in_triangle(triangle : list[NDArray[np.float32]], x : int, y : int) -> bool:
    return edge(triangle[0], triangle[1], x, y) > 0 \
        and edge(triangle[1], triangle[2], x, y) > 0 \
        and edge(triangle[2], triangle[0], x, y) > 0

def edge(vector_a : NDArray[np.float32], vector_b : NDArray[np.float32], point_x : int, point_y : int):
    return (vector_a[0] - vector_b[0]) * (point_y - vector_a[1]) \
            - (vector_a[1] - vector_b[1]) * (point_x - vector_a[0])

def get_bounding_box(projected_vertices : list[NDArray[np.float32]], screen_size : Tuple[int, int]) -> BoundingBox:
    left = max(floor(min(vertex[0] for vertex in projected_vertices)), 0)
    right = min(ceil(max(vertex[0] for vertex in projected_vertices)), screen_size[0])
    bottom = max(floor(min(vertex[1] for vertex in projected_vertices)), 0)
    top = min(ceil(max(vertex[1] for vertex in projected_vertices)), screen_size[1])
    return BoundingBox(left, right, top, bottom)


def get_model_view_matrix(transform : Transform) -> NDArray[np.float32]:
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

def get_projected_vertex(world_vertex : NDArray[np.float32], screen_size : Tuple[int, int]) -> NDArray[np.float32]:
    projected_vertex = np.array([
        (world_vertex[0] / world_vertex[2] + 0.5) * screen_size[0],
        (world_vertex[1] / world_vertex[2] + 0.5) * screen_size[1],
        world_vertex[2]
        ])
    return projected_vertex
