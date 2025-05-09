import os
from paraview.simple import *
from wslink.websocket import ServerProtocol
from wslink import register as exportRpc
from paraview.web import protocols as pv_protocols

# Configuração de diretórios
Pasta_Modelos = "modelos"
if not os.path.exists(Pasta_Modelos):
    os.makedirs(Pasta_Modelos)

class VisualizadorVascular(ServerProtocol):
    def __init__(self):
        super().__init__()
        self.available_models = []
        self.reader = None
        self.representation = None
        self.view = None
        self.opacity = 100
        self.color_preset = "Default"

    def initialize(self):
        """Inicialização do servidor"""
        try:
            # Configuração do ParaView
            Disconnect()
            Connect()

            # Criação da view
            self.view = CreateRenderView()
            self.view.Background = [0.2, 0.3, 0.4]

            # Registro de protocolos
            self.registerLinkProtocol(pv_protocols.ParaViewWebMouseHandler())
            self.registerLinkProtocol(pv_protocols.ParaViewWebViewPort())
            self.registerLinkProtocol(pv_protocols.ParaViewWebPublishImageDelivery())

            # Carrega modelos
            self.scan_modelos_diretorio()
            if self.available_models:
                self.load_model(self.available_models[0]["value"])

            return True
        except Exception as e:
            print(f"Falha na inicialização: {str(e)}")
            return False

    def scan_modelos_diretorio(self):
        """Scan do diretório de modelos"""
        self.available_models = [
            {"text": file, "value": os.path.join(Pasta_Modelos, file)}
            for file in os.listdir(Pasta_Modelos)
            if file.lower().endswith((".vtp", ".vtu", ".vtk"))
        ]

    def load_model(self, file_path):
        """Carrega um modelo VTK"""
        try:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            if self.reader:
                Delete(self.reader)
            
            self.reader = OpenDataFile(file_path)
            self.representation = Show(self.reader, self.view)
            
            # Aplica configurações visuais
            self._apply_visual_settings()
            ResetCamera(self.view)
            Render()
            
            print(f"Modelo carregado: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            print(f"Erro ao carregar modelo: {str(e)}")
            return False

    def _apply_visual_settings(self):
        """Aplica configurações visuais"""
        if not self.representation:
            return
            
        self.representation.Opacity = self.opacity / 100
        
        if self.color_preset == "Heat":
            self._apply_color_map([0, 0.23, 0.30, 0.75, 1.0, 0.87, 0.17, 0.49])
        elif self.color_preset == "Cool":
            self._apply_color_map([0, 0.07, 0.20, 0.48, 1.0, 0.60, 0.92, 1.0])
        else:
            ColorBy(self.representation, None)
            self.representation.DiffuseColor = [1.0, 1.0, 1.0]
        
        Render()

    def _apply_color_map(self, rgb_points):
        """Aplica mapa de cores"""
        ColorBy(self.representation, ('POINTS', ''))
        self.representation.LookupTable = GetLookupTableForArray(
            "RGB", 256, RGBPoints=rgb_points
        )

if __name__ == "__main__":
    from wslink import start_webserver
    
    # Configuração do servidor
    server_config = {
        "host": "0.0.0.0",
        "port": 8080,
        "content": "./www",
        "timeout": 300,
        "handle_signals": True  # Para gerenciar CTRL+C corretamente
    }
    
    # Inicialização robusta
    try:
        print(f"Iniciando servidor em http://{server_config['host']}:{server_config['port']}")
        start_webserver(
            config=server_config,
            protocol=VisualizadorVascular
        )
    except KeyboardInterrupt:
        print("\nServidor encerrado pelo usuário")
    except Exception as e:
        print(f"Erro fatal: {str(e)}")