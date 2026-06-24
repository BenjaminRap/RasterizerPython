from dataclasses import dataclass, field

@dataclass
class   Object3D:
    vertices : list[list[float]] = field(default_factory=list)
    faces : list[list[int]] = field(default_factory=list)

def parseVertexLine(splittedLine : list[str]) -> list[float]:
    if len(splittedLine) != 3:
        raise ValueError("Invalid line format, the vertex should contains 3 floats !")
    vertex = [float(component) for component in splittedLine]
    return vertex

def parseFaceLine(splittedLine : list[str]) -> list[int]:
    if len(splittedLine) != 3:
        raise ValueError("Invalid line format : the face should contains 3 integers !")
    face = [int(vertexIndex) for vertexIndex in splittedLine]
    if any(vertexIndex <= 0 for vertexIndex in face):
        raise ValueError("Invalid vertex index in face, it should be superior to 0 !")
    return face

def parseLine(object3D : Object3D, line : str) -> None:
    splittedLine = line.split()
    if len(splittedLine) == 0:
        return ;
    if splittedLine[0] == "v":
         vertex = parseVertexLine(splittedLine[1::])
         object3D.vertices.append(vertex)
    elif splittedLine[0] == "f":
        face = parseFaceLine(splittedLine[1::])
        object3D.faces.append(face)
    else:
        raise ValueError(f"Invalid line format, it should begin with 'v' for vertex or 'f' for face !")

def parseSimpleObjFile(filePath : str) -> Object3D:
    object3D = Object3D()
    with open(filePath) as file:
        lineIndex = 0
        while line := file.readline():
            try:
                parseLine(object3D, line)
            except Exception as e:
                raise ValueError(f"Invalid file format at line {lineIndex} : {line}") from e
    vertexIndices = (vertexIndex for face in object3D.faces for vertexIndex in face)
    verticesCount = len(object3D.vertices)
    if any(vertexIndex > verticesCount for vertexIndex in vertexIndices):
        raise ValueError(f"Invalid vertex index in face ! It should be smaller or equal to the number of vertices !")
    return object3D

if __name__ == "__main__":
    filePath = "./objects/square.simpleObj"
    try:
        object3D = parseSimpleObjFile(filePath)
        print(object3D)
    except OSError as e:
        raise RuntimeError(f"Failed to load model: {filePath}") from e
