from dataclasses import dataclass, field
from math import ceil, cos, floor, sin
from typing import Tuple
from numba import njit, prange

from numba import int16
from numba.experimental import jitclass
from numpy.typing import NDArray
import numpy as np


@dataclass
class   Object3D:
    vertices : list[NDArray[np.float32]] = field(default_factory=list)
    faces : list[NDArray[np.int32]] = field(default_factory=list)

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

bounding_box_spec = [
    ("left", int16),
    ("right", int16),
    ("top", int16),
    ("bottom", int16)
]

@jitclass(bounding_box_spec) # pyright : ignore
class   BoundingBox:
    left: np.int16
    right: np.int16
    top: np.int16
    bottom: np.int16
    def __init__(self, left : np.int16, right : np.int16, top : np.int16, bottom : np.int16):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom


def rasterize(game_objects : list[GameObject], screen : NDArray[np.uint8]):
    for game_object in game_objects:
        for face in game_object.object_3d.faces:
            rasterize_face(face, game_object, screen)


def rasterize_face(face : NDArray[np.int32], game_object : GameObject,
                   screen : NDArray[np.uint8]):
    projected_triangle = get_projected_triangle(game_object, face, screen.shape)
    if projected_triangle is None:
        return
    bounding_box = get_bounding_box(projected_triangle, screen.shape)
    draw_triangle(bounding_box, projected_triangle, screen)


@njit(parallel=True)
def draw_triangle(bounding_box : BoundingBox, projected_triangle : NDArray[np.float32], screen : NDArray[np.uint8]):
    for y in prange(bounding_box.bottom, bounding_box.top):
        for x in range(bounding_box.left, bounding_box.right):
            if is_in_triangle(projected_triangle, x, y):
                screen[y, x] = [255, 255, 255]


def get_projected_triangle(game_object : GameObject, face : NDArray[np.int32], screen_size : Tuple[int, int]) -> NDArray[np.float32] | None:
    projected_triangle = np.empty((3, 3), np.float32)
    for triangle_index, vertex_index in enumerate(face):
        vertex = game_object.object_3d.vertices[vertex_index]
        homogeneous_vertex = np.array([vertex[0], vertex[1], vertex[2], 1])
        model_view_projection = get_model_view_matrix(game_object.transform)
        world_vertex = homogeneous_vertex @ model_view_projection
        if world_vertex[2] <= 0:
            return
        projected_vertex = get_projected_vertex(world_vertex, screen_size)
        projected_triangle[triangle_index] = projected_vertex
    return projected_triangle


@njit(inline="always")
def is_in_triangle(triangle : NDArray[np.float32], x : int, y : int) -> bool:
    return edge(triangle[0], triangle[1], x, y) > 0 \
        and edge(triangle[1], triangle[2], x, y) > 0 \
        and edge(triangle[2], triangle[0], x, y) > 0


@njit(inline="always")
def edge(vector_a : NDArray[np.float32], vector_b : NDArray[np.float32], point_x : int, point_y : int):
    return (vector_a[0] - vector_b[0]) * (point_y - vector_a[1]) \
            - (vector_a[1] - vector_b[1]) * (point_x - vector_a[0])


def get_bounding_box(projected_vertices : NDArray[np.float32], screen_size : Tuple[int, int]) -> BoundingBox:
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
