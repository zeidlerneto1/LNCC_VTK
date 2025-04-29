import os
from trame.app import get_server
from trame.ui.vuetify import SinglePageLayout
from trame.widgets import vuetify, vtk as vtk_widgets
from vtkmodules.vtkIOXML import vtkXMLPolyDataReader
import vtkmodules.all as vtk

# 1. Configuração VTK
Pasta_Modelos = "modelos"
if not os.path.exists(Pasta_Modelos):
    os.makedirs(Pasta_Modelos)

'''
reader = vtkXMLPolyDataReader()
reader.SetFileName(os.path.join("modelos", "adan.vtp"))
reader.Update()'''

mapper = vtk.vtkPolyDataMapper()
#mapper.SetInputConnection(reader.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.ResetCamera()
renderer.SetBackground(0.2, 0.3, 0.4)  # Cor de fundo

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetOffScreenRendering(1)  # Remove janela nativa

# 2. Configuração Trame
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# 3. Inicializando o estado
state.opacity = 100
state.color_preset = "Default"
state.presets = ["Default", "Heat", "Cool"]  # Lista de presets disponíveis

# 4. Funções de atualização
def update_opacity(opacity, **kwargs):
    """Atualiza a opacidade do ator"""
    actor.GetProperty().SetOpacity(opacity / 100)
    ctrl.view_update()

def apply_color_preset(**kwargs):
    """Aplica o preset de cor selecionado"""
    preset_name = state.color_preset  # Obtém o valor atual do estado
    prop = actor.GetProperty()
    
    if preset_name == "Heat":
        prop.SetColor(1.0, 0.4, 0.3)  # Cor quente
    elif preset_name == "Cool":
        prop.SetColor(0.3, 0.4, 1.0)  # Cor fria
    else:
        prop.SetColor(1.0, 1.0, 1.0)  # Cor padrão
    
    ctrl.view_update()

# 5. Configura handlers de estado
state.change("opacity")(update_opacity)
state.change("color_preset")(apply_color_preset)

# 6. Layout da interface com Trame
with SinglePageLayout(server) as layout:
    layout.title.set_text("Visualizador de Modelos Vasculares")
    
    with layout.toolbar:
        vuetify.VSpacer()
        
        # Controle de opacidade
        vuetify.VSlider(
            v_model=("opacity", state.opacity),
            min=0,
            max=100,
            label="Opacidade",
            dense=True,
            hide_details=True,
            style="max-width: 200px",
        )
        
        # Seletor de cores
        vuetify.VSelect(
            v_model=("color_preset", state.color_preset),
            items=("presets", state.presets),
            label="Mapa de Cores",
            dense=True,
            hide_details=True,
            style="max-width: 200px; margin-left: 20px",
        )
    
    with layout.content:
        with vuetify.VContainer(fluid=True, classes="pa-0 fill-height"):
            # Visualizador VTK
            view = vtk_widgets.VtkLocalView(render_window)
            ctrl.view_update = view.update

if __name__ == "__main__":
    # Inicia o servidor após aplicar as configurações iniciais
    apply_color_preset()  # Aplica o preset padrão
    server.start()