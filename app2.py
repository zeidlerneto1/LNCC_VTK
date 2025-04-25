import os
import sys
os.environ['VTK_USE_LEGACY_DISPLAY'] = '1'  # Evita problemas com OpenGL moderno
os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'   # Força renderização via CPU (evita crash AMD)

# Desativa a criação de janelas nativas pelo VTK
os.environ['DISPLAY'] = ':0'  # Para Linux (pode variar dependendo do seu sistema)
os.environ['VTK_DISABLE_NATIVE_WINDOWS'] = '1'

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk as vtk_widgets
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
import vtkmodules.all as vtk

# Configuração do caminho do modelo
pasta_modelos = r"/home/peter/projeto-vtkjs/hemolab/modelos/adan.vtp"
if not os.path.isfile(pasta_modelos):
    raise FileNotFoundError(f"Arquivo do modelo não encontrado: {pasta_modelos}")

# --- Configuração VTK ---
reader = vtkXMLPolyDataReader()
reader.SetFileName(pasta_modelos)
reader.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(reader.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.ResetCamera()
renderer.SetBackground(0.2, 0.3, 0.4)  # Cor de fundo

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetOffScreenRendering(1)  # IMPORTANTE: Renderização off-screen

# --- Configuração Trame ---
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

with SinglePageLayout(server) as layout:
    layout.title.set_text("Visualizador 3D")
    
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            # Usando VtkLocalView para renderização no servidor
            view = vtk_widgets.VtkLocalView(render_window)
            ctrl.view_update = view.update

# --- Inicia o servidor web ---
if __name__ == "__main__":
    server.start()
