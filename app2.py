import os
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk as vtk_widgets, html
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
import vtkmodules.all as vtk

# 1. Configuração VTK
reader = vtkXMLPolyDataReader()
reader.SetFileName(os.path.join("modelos", "adan.vtp"))
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
render_window.SetOffScreenRendering(1)  # Remove janela nativa

# 2. Configuração Trame
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# 3. Recrie seus controles em Python/Vuetify
def update_opacity(opacity):
    actor.GetProperty().SetOpacity(opacity / 100)
    ctrl.view_update()

def apply_color_preset(preset_name):
    # Implemente sua lógica de cores aqui
    ctrl.view_update()

with SinglePageLayout(server) as layout:
    layout.title.set_text("Visualizador Vascular")
    
    with layout.toolbar:
        vuetify.VSpacer()
        
        # Controle de opacidade
        vuetify.VSlider(
            v_model=("opacity", 100),
            min=0, max=100,
            label="Opacidade",
            dense=True,
            hide_details=True,
            style="max-width: 200px",
            change=ctrl.view_update
        )
        
        # Seletor de cores
        vuetify.VSelect(
            v_model=("color_preset", "Default"),
            items=("presets", ["Default", "Heat", "Cool"]),
            label="Mapa de Cores",
            dense=True,
            hide_details=True,
            style="max-width: 200px; margin-left: 20px",
            change=(apply_color_preset, "[$event]")
        )
    
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            # Visualizador VTK
            view = vtk_widgets.VtkLocalView(render_window)
            ctrl.view_update = view.update
            
            # Tabela de dados (simulada)
            with vuetify.VCard(style="position: absolute; top: 120px; left: 20px; width: 300px;"):
                vuetify.VCardTitle("Dados Vasculares")
                vuetify.VDataTable(
                    headers=("headers", [
                        {"text": "Artéria", "value": "name"},
                        {"text": "Diâmetro", "value": "diameter"},
                    ]),
                    items=("items", [
                        {"name": "Artéria A", "diameter": 2.5},
                        {"name": "Artéria B", "diameter": 1.8},
                    ]),
                    dense=True
                )

if __name__ == "__main__":
    server.start()
