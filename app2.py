import os
import sys
os.environ['VTK_USE_LEGACY_DISPLAY'] = '1'  # Evita problemas com OpenGL moderno
os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'   # Força renderização via CPU (evita crash AMD)

from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk as vtk_widgets
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
import vtkmodules.all as vtk

#caminho do .vtp 
pasta_modelos = r"C:\Users\peter\Documents\LNCC\modelos\adan.vtp"
if not os.path.isfile(pasta_modelos):
    raise FileNotFoundError(f"nao achou o modelo.vtp : {pasta_modelos}")


# --- Configuração VTK (exemplo: cone) ---
#cone = vtk.vtkConeSource()
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

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# --- Configuração Trame (Vue2) ---
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

with SinglePageLayout(server) as layout:
    layout.title.set_text("VTK + Trame Web")
    
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            # Usando VtkLocalView (renderização no servidor)
            view = vtk_widgets.VtkLocalView(render_window)
            ctrl.view_update = view.update  # Garante atualizações

# --- Inicia o servidor web ---
if __name__ == "__main__":
    server.start()