"""
Adapters for DataJoint tables.
"""

import datajoint as dj
import numpy as np
import h5py
import os
import trimesh
from microns_utils.adapter_utils import NumpyAdapter

from collections import namedtuple


class MeshAdapter(dj.AttributeAdapter):
    # Initialize the correct attribute type (allows for use with multiple stores)
    def __init__(self, attribute_type):
        self.attribute_type = attribute_type
        super().__init__()

    attribute_type = '' # this is how the attribute will be declared

    # TriangularMesh = namedtuple('TriangularMesh', ['segment_id', 'vertices', 'faces'])
    
    def put(self, filepath):
        # save the filepath to the mesh
        filepath = os.path.abspath(filepath)
        assert os.path.exists(filepath)
        return filepath

    def get(self, filepath):
        # access the h5 file and return a mesh
        assert os.path.exists(filepath)

        with h5py.File(filepath, 'r') as hf:
            vertices = hf['vertices'][()].astype(np.float64)
            faces = hf['faces'][()].reshape(-1, 3).astype(np.uint32)
        
        segment_id = os.path.splitext(os.path.basename(filepath))[0]

        return trimesh.Trimesh(vertices=vertices, faces=faces)
#         self.TriangularMesh(
#             segment_id=int(segment_id),
#             vertices=vertices,
#             faces=faces
#         )


import os
class FilepathAdapter(dj.AttributeAdapter):
    # Initialize the correct attribute type (allows for use with multiple stores)
    def __init__(self, attribute_type):
        self.attribute_type = attribute_type
        super().__init__()

    #?
    attribute_type = '' # this is how the attribute will be declared
    has_version = False # used for file name recognition
    
    def put(self, filepath):
        # save the filepath to the mesh
        filepath = os.path.abspath(filepath)
        assert os.path.exists(filepath)
        return filepath
    
    def get(self, filepath):
        """
        1) Get the filepath of the decimated mesh
        2) Make sure that both file paths exist
        3) use the decompress method
        
        """
        
        #1) Get the filepath of the decimated mesh
        
        filepath = Path(filepath)
        assert os.path.exists(filepath)
        
        """Old way where used the file path
        dec_filepath = get_decimated_mesh_path_from_decomposition_path(filepath)
        assert os.path.exists(dec_filepath)
        print(f"Attempting to get the following files:\ndecomp = {filepath}\ndec = {dec_filepath} ")
        """
        
        """
        ---- 4/26 Change that will only send back the filepath
        
        """
        return filepath
        
        
#         #2) get the decimated mesh 
#         segment_id = int(filepath.stem.split("_")[0])
#         dec_mesh = fetch_segment_id_mesh(segment_id)
        
        
#         #3) use the decompress method
#         recovered_neuron = nru.decompress_neuron(filepath=filepath,
#                      original_mesh=dec_mesh)
        
        return recovered_neuron

class MeshNPZToTrimeshAdapter(FilepathAdapter):
    def get(self, filepath):
        filepath = super().get(filepath)
        mesh = np.load(filepath)
        return trimesh.Trimesh(vertices=mesh['vertices'], faces=mesh['faces'])
    
#import system_utils as su
from pathlib import Path
import numpy as np
import bz2
import _pickle as cPickle

def decompress_pickle(filename):
    """
    Example: 
    data = decompress_pickle('example_cp.pbz2') 
    """
    if type(filename) == type(Path()):
        filename = str(filename.absolute())
    if filename[-5:] != ".pbz2":
        filename += ".pbz2"
        
    data = bz2.BZ2File(filename, 'rb')
    data = cPickle.load(data)
    return data

class DecompressionAdapter(dj.AttributeAdapter):
    """
    Purpose: Decompressed saved external files of
    format type npz or pbz2
    
    """
    # Initialize the correct attribute type (allows for use with multiple stores)
    def __init__(self, attribute_type):
        self.attribute_type = attribute_type
        super().__init__()

    attribute_type = '' # this is how the attribute will be declared

    def put(self, filepath):
        # save the filepath to the mesh
        filepath = os.path.abspath(filepath)
        assert os.path.exists(filepath)
        return filepath

    def get(self, filepath):
        # access the h5 file and return a mesh
        assert os.path.exists(filepath)
        
        filepath = Path(filepath)
        #print(filepath)
        
        if filepath.suffix == ".pbz2":
            return decompress_pickle(filepath)
        elif filepath.suffix == ".npz":
            return np.load(filepath)["data"]
        else:
            raise Exception("Uninterpretted Type")
            
            
# instantiate for use as a datajoint type
h01_meshes = MeshAdapter('filepath@h01_meshes')
h01_faces = DecompressionAdapter('filepath@h01_faces')
h01_skeletons = DecompressionAdapter('filepath@h01_skeletons')
h01_decomposition = FilepathAdapter('filepath@h01_decomposition')
h01_auto_proof_meshes = DecompressionAdapter('filepath@h01_auto_proof_meshes')
h01_auto_proof_skeletons = DecompressionAdapter('filepath@h01_auto_proof_skeletons')
h01_graph = FilepathAdapter("filepath@h01_graph")
#h01_somas = SomasAdapter('filepath@h01_somas')

minnie65_decimated_meshes = MeshAdapter('filepath@minnie65_decimated_meshes')
minnie65_soma_meshes = MeshAdapter('filepath@minnie65_soma_meshes')
minnie65_auto_proof_meshes = DecompressionAdapter('filepath@minnie65_auto_proof_meshes')
minnie65_auto_proof_skeletons = DecompressionAdapter('filepath@minnie65_auto_proof_skeletons')
minnie65_faces = DecompressionAdapter('filepath@minnie65_faces')
minnie65_skeletons = DecompressionAdapter('filepath@minnie65_skeletons')
minnie65_decomposition = FilepathAdapter('filepath@minnie65_decomposition')
minnie65_graph = FilepathAdapter("filepath@minnie65_graph")
#minnie65_somas = SomasAdapter('filepath@minnie65_somas')

minnie65_morphology_v2_decimated_meshes_adapter = MeshNPZToTrimeshAdapter('filepath@minnie65_decimated_meshes')
minnie65_morphology_v2_decomposition_adapter = FilepathAdapter('filepath@minnie65_decomposition')
minnie65_auto_proofreading_v2_auto_proof_meshes_adapter = MeshNPZToTrimeshAdapter('filepath@minnie65_auto_proof_meshes')
minnie65_auto_proofreading_v2_auto_proof_skeletons_adapter = NumpyAdapter('filepath@minnie65_auto_proof_skeletons')
minnie65_auto_proofreading_v2_auto_proof_graphs_adapter = FilepathAdapter('filepath@minnie65_auto_proof_graphs')

# also store in one object for ease of use with virtual modules
h01_auto_proofreading = {
    'h01_auto_proof_meshes': h01_auto_proof_meshes,
    'h01_auto_proof_skeletons': h01_auto_proof_skeletons,
    'h01_faces': h01_faces,
    'h01_skeletons': h01_skeletons,
    'h01_decomposition': h01_decomposition,
    'h01_graph':h01_graph,
}

h01_morphology = {
    'h01_meshes': h01_meshes,
    'h01_skeletons': h01_skeletons,
    #'h01_somas':h01_somas,
    'h01_faces':h01_faces,
}

minnie65_morphology = {
    "minnie65_decimated_meshes": minnie65_decimated_meshes,
    'minnie65_soma_meshes': minnie65_soma_meshes,
    'minnie65_skeletons': minnie65_skeletons,
    #'minnie65_somas':minnie65_somas,
    'minnie65_faces': minnie65_faces,
    
}

minnie65_auto_proofreading = {
    'minnie65_auto_proof_meshes': minnie65_auto_proof_meshes,
    'minnie65_auto_proof_skeletons': minnie65_auto_proof_skeletons,
    'minnie65_faces': minnie65_faces,
    'minnie65_skeletons': minnie65_skeletons,
    'minnie65_decomposition': minnie65_decomposition,
    'minnie65_graph':minnie65_graph,
}

minnie65_morphology_v2 = {
    "minnie65_decimated_meshes": minnie65_morphology_v2_decimated_meshes_adapter,
    'minnie65_decomposition': minnie65_morphology_v2_decomposition_adapter,
}

minnie65_auto_proofreading_v2 = {
    'minnie65_auto_proof_meshes': minnie65_auto_proofreading_v2_auto_proof_meshes_adapter,
    'minnie65_auto_proof_skeletons': minnie65_auto_proofreading_v2_auto_proof_skeletons_adapter,
    'minnie65_auto_proof_graphs': minnie65_auto_proofreading_v2_auto_proof_graphs_adapter,
}

