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

class VTKManager:
    def __init__(self):
        self.renderer = vtk.vtkRenderer()
        self.renderer.SetBackground(0.2, 0.3, 0.4)
        self.render_window = vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.render_window.SetOffScreenRendering(1)
        
        self.reader = vtkXMLPolyDataReader()
        self.mapper = vtk.vtkPolyDataMapper()
        self.actor = vtk.vtkActor()
        self.setup_pipeline()
    
    def setup_pipeline(self):
        self.mapper.SetInputConnection(self.reader.GetOutputPort())
        self.actor.SetMapper(self.mapper)
        self.renderer.AddActor(self.actor)
    
    def load_model(self, file_path):
        """Carrega um modelo com tratamento completo"""
        if not file_path or not os.path.isfile(file_path):
            print(f"Arquivo não encontrado: {file_path}")
            return False
            
        try:
            # Limpeza completa da cena
            self.renderer.RemoveAllViewProps()
            
            # Carrega novo modelo
            self.reader.SetFileName(file_path)
            self.reader.Update()
            
            # Recria o pipeline
            self.mapper = vtk.vtkPolyDataMapper()
            self.actor = vtk.vtkActor()
            self.setup_pipeline()
            
            # Configurações visuais
            self.renderer.ResetCamera()
            self.render_window.Modified()
            self.render_window.Render()
            
            return True
        except Exception as e:
            print(f"Erro ao carregar modelo: {e}")
            return False

# Inicializa o VTKManager
vtk_mgr = VTKManager()

# 2. Configuração Trame
server = get_server(client_type="vue2")
state, ctrl = server.state, server.controller

# 3. Estado inicial
state.opacity = 100
state.color_preset = "Default"
state.presets = ["Default", "Heat", "Cool"]
state.available_models = []
state.selected_model = None
state.temp_model = None  # Armazena seleção temporária

def scan_modelos_diretorio():
    modelos = []
    for file in os.listdir(Pasta_Modelos):
        if file.lower().endswith(".vtp"):
            modelos.append({
                "text": file,
                "value": os.path.join(Pasta_Modelos, file)
            })
    state.available_models = modelos
    if modelos:
        state.selected_model = modelos[0]["value"]
        state.temp_model = modelos[0]["value"]

def load_model():
    """Função chamada pelo botão para carregar o modelo selecionado"""
    if state.temp_model:
        if vtk_mgr.load_model(state.temp_model):
            state.selected_model = state.temp_model
            update_opacity(state.opacity)
            apply_color_preset()
            ctrl.view_update()
            print(f"Modelo carregado: {os.path.basename(state.selected_model)}")

def update_opacity(opacity, **kwargs):
    vtk_mgr.actor.GetProperty().SetOpacity(opacity / 100)
    ctrl.view_update()

def apply_color_preset(**kwargs):
    prop = vtk_mgr.actor.GetProperty()
    if state.color_preset == "Heat":
        prop.SetColor(1.0, 0.4, 0.3)
    elif state.color_preset == "Cool":
        prop.SetColor(0.3, 0.4, 1.0)
    else:
        prop.SetColor(1.0, 1.0, 1.0)
    ctrl.view_update()

# 4. Configura handlers
state.change("opacity")(update_opacity)
state.change("color_preset")(apply_color_preset)

# 5. Interface com botão de confirmação
with SinglePageLayout(server) as layout:
    layout.title.set_text("Visualizador de Modelos Vasculares")
    
    with layout.toolbar:
        vuetify.VSpacer()
        
        # Seletor de modelos (armazena seleção temporária)
        vuetify.VSelect(
            v_model=("temp_model", None),
            items=("available_models", []),
            label="Selecione um modelo",
            dense=True,
            hide_details=True,
            style="min-width: 300px; margin-right: 10px",
        )
        
        # Botão de confirmação
        vuetify.VBtn(
            "Carregar Modelo",
            click=load_model,
            color="primary",
            style="margin-right: 20px",
        )
        
        # Controles visuais
        vuetify.VSlider(
            v_model=("opacity", state.opacity),
            min=0,
            max=100,
            label="Opacidade",
            dense=True,
            hide_details=True,
            style="max-width: 200px",
        )
        
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
            view = vtk_widgets.VtkLocalView(vtk_mgr.render_window)
            ctrl.view_update = view.update

# Inicialização
if __name__ == "__main__":
    scan_modelos_diretorio()
    if state.selected_model:
        load_model()  # Carrega o primeiro modelo
    
    print("\n=== Modelos Disponíveis ===")
    for i, model in enumerate(state.available_models, 1):
        print(f"{i}. {model['text']}")
    
    print("\nServidor pronto em http://localhost:8080")
    print("Selecione um modelo e clique em 'Carregar Modelo'")
    server.start()