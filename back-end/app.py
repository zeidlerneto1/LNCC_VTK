import os
import sys
os.environ['VTK_USE_LEGACY_DISPLAY'] = '1'
os.environ['LIBGL_ALWAYS_SOFTWARE'] = '1'

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

# --- Funções de atualização ---
def apply_color_filter(color):
    color_map = vtk.vtkColorTransferFunction()
    if color == "Azul-Vermelho":
        color_map.AddRGBPoint(0, 0.0, 0.0, 1.0)
        color_map.AddRGBPoint(1, 1.0, 0.0, 0.0)
    elif color == "Escala de cinza":
        color_map.AddRGBPoint(0, 0.0, 0.0, 0.0)
        color_map.AddRGBPoint(1, 1.0, 1.0, 1.0)
    elif color == "Mapa de calor":
        color_map.AddRGBPoint(0, 0.0, 0.0, 1.0)
        color_map.AddRGBPoint(0.5, 0.0, 1.0, 0.0)
        color_map.AddRGBPoint(1, 1.0, 0.0, 0.0)

    mapper.SetLookupTable(color_map)
    ctrl.view_update()

# --- Configuração Trame ---
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# Inicializa variáveis de estado
state.opacity = 100
state.color_filter = "Azul-Vermelho"

def update_opacity(opacity, **kwargs):
    actor.GetProperty().SetOpacity(opacity / 100.0)
    ctrl.view_update()

def update_color_filter(color_filter, **kwargs):
    apply_color_filter(color_filter)

# Configura handlers de mudança de estado
state.change("opacity")(update_opacity)
state.change("color_filter")(update_color_filter)

# --- Interface do usuário ---
with SinglePageLayout(server) as layout:
    layout.title.set_text("Visualizador 3D - Hemolab")
    
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSelect(
            label="Filtro de Cor",
            items=["Azul-Vermelho", "Escala de cinza", "Mapa de calor"],
            v_model=("color_filter",),
            hide_details=True,
            dense=True,
            style="max-width: 200px;",
        )
        vuetify.VSlider(
            label="Opacidade",
            v_model=("opacity",),
            min=0,
            max=100,
            hide_details=True,
            style="max-width: 200px; margin-left: 20px;",
        )
    
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            # Usando VtkRemoteView para renderização no cliente (mais eficiente)
            view = vtk_widgets.VtkRemoteView(render_window)
            ctrl.view_update = view.update

# --- Inicia o servidor ---
if __name__ == "__main__":
    server.start()