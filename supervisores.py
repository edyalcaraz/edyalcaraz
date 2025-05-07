from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from datetime import datetime
import pandas as pd
import qrcode
import os
import sys
from kivy.resources import resource_add_path
from kivy.uix.image import Image as KivyImage
from kivy.utils import platform
from kivy.config import Config

# Configuración del teclado
Config.set('kivy', 'keyboard_mode', 'system')

# Configuración multiplataforma
if platform == 'android':
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE,
                        Permission.READ_EXTERNAL_STORAGE])

    def get_downloads_folder():
        path = os.path.join(primary_external_storage_path(), 'Download', 'ToconesApp')
        os.makedirs(path, exist_ok=True)
        return path

    def share_file_android(filename):
        from jnius import autoclass
        Intent = autoclass('android.content.Intent')
        Uri = autoclass('android.net.Uri')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')

        intent = Intent()
        intent.setAction(Intent.ACTION_SEND)
        intent.setType("application/vnd.ms-excel")
        intent.putExtra(Intent.EXTRA_STREAM, Uri.parse("file://" + filename))
        current_activity = PythonActivity.mActivity
        current_activity.startActivity(Intent.createChooser(intent, "Compartir via"))
else:
    def get_downloads_folder():
        path = os.path.join(os.path.expanduser("~"), 'Downloads', 'ToconesApp')
        os.makedirs(path, exist_ok=True)
        return path

    def share_file_android(filename):
        import subprocess
        if sys.platform == 'win32':
            os.startfile(filename)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', filename])
        else:
            subprocess.Popen(['xdg-open', filename])

# Configuración de colores
PRIMARY_COLOR = (0.2, 0.6, 0.86, 1)
SECONDARY_COLOR = (0.9, 0.9, 0.9, 1)
ACCENT_COLOR = (0.96, 0.26, 0.21, 1)
DARK_TEXT = (0.2, 0.2, 0.2, 1)
LIGHT_TEXT = (1, 1, 1, 1)

# Listas de personas
SUPERVISORES = [
    "Astudillo Pungo, Elkin Antonio",
    "Lopez Chandillo, Miguel Angel",
    "Orozco Ramírez, Juliana",
    "Hernandez, Erika",
    "Ramirez Ramirez, Grimaneza",
    "Tabares Tamayo, Jhon Edward"
]

EVALUADORES = [
    "Astudillo Pungo, Elkin Antonio",
    "Lopez Chandillo, Miguel Angel",
    "Orozco Ramírez, Juliana",
    "Hernandez, Erika",
    "Ramirez Ramirez, Grimaneza",
    "Tabares Tamayo, Jhon Edward"
]

MOTOSIERRISTAS = [
    "Franco Franco, Ubeimar Ely",
    "Trejos Rendon, Ivan de Jesus",
    "Castañeda Vicente, Aldemar",
    "Hernadez Loaiza, Danover de Jesus",
    "Gutierrez Parra, Jairo de Jesus",
    "Jaramillo Ramirez, Rafael Andres",
    "Cruz Cardona, Cristian Danilo"
]

class Logo(KivyImage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'assets/exfor.png'  # Changed to assets folder for Android
        self.size_hint = (None, None)
        self.size = (200, 200)

class SignaturePad(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lines = []
        with self.canvas.before:
            Color(*SECONDARY_COLOR)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            with self.canvas:
                Color(*DARK_TEXT)
                touch.ud['line'] = Line(points=[touch.x, touch.y], width=dp(2))
                self.lines.append(touch.ud['line'])
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]
            return True
        return super().on_touch_move(touch)

    def clear_canvas(self):
        self.canvas.clear()
        self.lines = []
        with self.canvas.before:
            Color(*SECONDARY_COLOR)
            self.rect = Rectangle(pos=self.pos, size=self.size)

class SignatureWidget(BoxLayout):
    def __init__(self, title_text='Firma', **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), **kwargs)
        self.title_label = Label(text=title_text,
                               size_hint_y=None,
                               height=dp(30),
                               color=DARK_TEXT,
                               bold=True)
        self.add_widget(self.title_label)

        self.signature_pad = SignaturePad(size_hint_y=0.8)
        self.add_widget(self.signature_pad)

        btn_clear = Button(text='Limpiar Firma',
                         size_hint_y=None,
                         height=dp(40),
                         background_color=ACCENT_COLOR,
                         color=LIGHT_TEXT)
        btn_clear.bind(on_release=lambda x: self.signature_pad.clear_canvas())
        self.add_widget(btn_clear)

class MenuPrincipal(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(40), spacing=dp(20))

        title = Label(text='Sistema de Evaluación Forestal',
                    font_size=dp(24),
                    bold=True,
                    color=DARK_TEXT)
        layout.add_widget(title)

        botones = ['TOCONES', 'CORREDORES', 'CUBICACIÓN', 'MICROPLANEACIÓN']
        for boton in botones:
            btn = Button(text=boton,
                       size_hint_y=None,
                       height=dp(60),
                       background_color=PRIMARY_COLOR,
                       color=LIGHT_TEXT)
            btn.bind(on_release=self.ir_a_tocones if boton == 'TOCONES' else self.no_disponible)
            layout.add_widget(btn)

        self.add_widget(layout)

    def ir_a_tocones(self, instance):
        self.manager.current = 'encabezado'

    def no_disponible(self, instance):
        popup = Popup(title='Aviso',
                     content=Label(text='Funcionalidad no disponible aún'),
                     size_hint=(0.7, 0.3))
        popup.open()

class EncabezadoTocones(Screen):
    datos_encabezado = ObjectProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datos_encabezado = {}

        scroll = ScrollView(do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical',
                              spacing=dp(15),
                              padding=dp(20),
                              size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        form_layout = GridLayout(cols=2,
                               size_hint_y=None,
                               spacing=dp(15),
                               padding=dp(10),
                               row_default_height=dp(50))
        form_layout.bind(minimum_height=form_layout.setter('height'))

        campos = [
            ('Finca', 'finca', 'text'),
            ('Lote', 'lote', 'text'),
            ('Especie', 'especie', 'text'),
            ('Plantación (dd/mm/aaaa)', 'plantacion', 'text'),
            ('Evaluación (dd/mm/aaaa)', 'evaluacion', 'text'),
            ('Supervisor', 'supervisor', 'spinner_supervisor'),
            ('Evaluador', 'evaluador', 'spinner_evaluador'),
            ('Motosierrista', 'motosierrista', 'spinner_motosierrista')
        ]

        self.inputs = {}
        for label, name, field_type in campos:
            lbl = Label(text=label,
                      halign='left',
                      color=DARK_TEXT,
                      size_hint_y=None,
                      height=dp(40))
            form_layout.add_widget(lbl)

            if field_type.startswith('spinner'):
                spinner_values = {
                    'spinner_supervisor': SUPERVISORES,
                    'spinner_evaluador': EVALUADORES,
                    'spinner_motosierrista': MOTOSIERRISTAS
                }[field_type]

                spinner = Spinner(
                    text='Seleccione',
                    values=spinner_values,
                    size_hint_y=None,
                    height=dp(40),
                    background_color=(1, 1, 1, 1)
                )
                self.inputs[name] = spinner
                form_layout.add_widget(spinner)
            else:
                ti = TextInput(multiline=False,
                             size_hint_y=None,
                             height=dp(40),
                             background_color=(1, 1, 1, 1))
                self.inputs[name] = ti
                form_layout.add_widget(ti)

        lbl_edad = Label(text='Edad (años)',
                       halign='left',
                       color=DARK_TEXT,
                       size_hint_y=None,
                       height=dp(40))
        form_layout.add_widget(lbl_edad)

        self.edad_input = TextInput(multiline=False,
                                  readonly=True,
                                  size_hint_y=None,
                                  height=dp(40),
                                  background_color=(0.9, 0.9, 0.9, 1))
        form_layout.add_widget(self.edad_input)

        btn_calcular = Button(text='Calcular Edad',
                            size_hint_y=None,
                            height=dp(50),
                            background_color=(0.3, 0.69, 0.49, 1),
                            color=LIGHT_TEXT)
        form_layout.add_widget(Label())
        form_layout.add_widget(btn_calcular)
        btn_calcular.bind(on_release=self.calcular_edad)

        main_layout.add_widget(form_layout)

        firmas_layout = GridLayout(cols=2,
                                 size_hint_y=None,
                                 height=dp(250),
                                 spacing=dp(20),
                                 padding=dp(10))

        self.firma_eval = SignatureWidget(title_text='Firma Evaluador',
                                        size_hint_y=None,
                                        height=dp(200))
        firmas_layout.add_widget(self.firma_eval)

        self.firma_moto = SignatureWidget(title_text='Firma Motosierrista',
                                        size_hint_y=None,
                                        height=dp(200))
        firmas_layout.add_widget(self.firma_moto)

        main_layout.add_widget(firmas_layout)

        btn_guardar = Button(text='Guardar y Continuar',
                           size_hint_y=None,
                           height=dp(60),
                           background_color=PRIMARY_COLOR,
                           color=LIGHT_TEXT)
        btn_guardar.bind(on_release=self.guardar_y_continuar)
        main_layout.add_widget(btn_guardar)

        scroll.add_widget(main_layout)
        self.add_widget(scroll)

    def calcular_edad(self, instance):
        try:
            fecha_plant = datetime.strptime(self.inputs['plantacion'].text, '%d/%m/%Y')
            fecha_eval = datetime.strptime(self.inputs['evaluacion'].text, '%d/%m/%Y')
            diferencia = fecha_eval - fecha_plant
            edad = round(diferencia.days / 365.25, 1)
            self.edad_input.text = str(edad)
        except ValueError:
            popup = Popup(title='Error',
                        content=Label(text='Formato de fecha inválido\nUse dd/mm/aaaa'),
                        size_hint=(0.8, 0.4))
            popup.open()

    def guardar_y_continuar(self, instance):
        if not self.edad_input.text:
            self.calcular_edad(instance)
            return

        self.datos_encabezado = {
            'finca': self.inputs['finca'].text,
            'lote': self.inputs['lote'].text,
            'especie': self.inputs['especie'].text,
            'plantacion': self.inputs['plantacion'].text,
            'evaluacion': self.inputs['evaluacion'].text,
            'supervisor': self.inputs['supervisor'].text,
            'evaluador': self.inputs['evaluador'].text,
            'motosierrista': self.inputs['motosierrista'].text,
            'edad': self.edad_input.text
        }

        self.manager.current = 'ingreso_tocones'

class IngresoToconesScreen(Screen):
    datos_tocones = ObjectProperty({})

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.datos_tocones = {i: {} for i in range(1, 13)}

        scroll = ScrollView(do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        title = Label(text='Ingreso de Datos de Tocones',
                    font_size=dp(24),
                    bold=True,
                    color=DARK_TEXT,
                    size_hint_y=None,
                    height=dp(50))
        main_layout.add_widget(title)

        columns_layout = BoxLayout(orientation='horizontal', spacing=dp(15), size_hint_y=None)
        columns_layout.bind(minimum_height=columns_layout.setter('height'))

        left_column = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        left_column.bind(minimum_height=left_column.setter('height'))

        right_column = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        right_column.bind(minimum_height=right_column.setter('height'))

        for i in range(1, 13):
            btn = Button(text=f'Tocón {i}',
                       size_hint_y=None,
                       height=dp(60),
                       background_color=PRIMARY_COLOR,
                       color=LIGHT_TEXT)
            btn.bind(on_release=lambda instance, num=i: self.abrir_formulario_tocon(num))

            if i <= 6:
                left_column.add_widget(btn)
            else:
                right_column.add_widget(btn)

        columns_layout.add_widget(left_column)
        columns_layout.add_widget(right_column)
        main_layout.add_widget(columns_layout)

        btn_guardar_todo = Button(text='Guardar Todos los Datos',
                                size_hint_y=None,
                                height=dp(60),
                                background_color=(0.3, 0.69, 0.49, 1),
                                color=LIGHT_TEXT)
        btn_guardar_todo.bind(on_release=self.guardar_todo_y_generar_excel)
        main_layout.add_widget(btn_guardar_todo)

        btn_volver = Button(text='Volver',
                          size_hint_y=None,
                          height=dp(60),
                          background_color=ACCENT_COLOR,
                          color=LIGHT_TEXT)
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'encabezado'))
        main_layout.add_widget(btn_volver)

        scroll.add_widget(main_layout)
        self.add_widget(scroll)

    def abrir_formulario_tocon(self, numero_tocon):
        if not self.manager.has_screen(f'formulario_tocon_{numero_tocon}'):
            self.manager.add_widget(FormularioToconScreen(
                name=f'formulario_tocon_{numero_tocon}',
                numero_tocon=numero_tocon,
                datos_tocones=self.datos_tocones
            ))
        self.manager.current = f'formulario_tocon_{numero_tocon}'

    def guardar_todo_y_generar_excel(self, instance):
        # Verificar que todos los tocones tengan datos
        for i in range(1, 13):
            if not self.datos_tocones[i]:
                popup = Popup(title='Advertencia',
                            content=Label(text=f'Faltan datos del Tocón {i}'),
                            size_hint=(0.7, 0.3))
                popup.open()
                return

        try:
            encabezado = self.manager.get_screen('encabezado').datos_encabezado

            data = {
                'tocon': list(range(1, 13)),
                'finca': [encabezado['finca']] * 12,
                'lote': [encabezado['lote']] * 12,
                'especie': [encabezado['especie']] * 12,
                'plantacion': [encabezado['plantacion']] * 12,
                'evaluacion': [encabezado['evaluacion']] * 12,
                'supervisor': [encabezado['supervisor']] * 12,
                'evaluador': [encabezado['evaluador']] * 12,
                'motosierista': [encabezado['motosierrista']] * 12,
                'firma_evaluad': ['Firma guardada'] * 12,
                'firma_motosierista': ['Firma guardada'] * 12,
                'diametro': [self.datos_tocones[i]['d'] for i in range(1, 13)],
                'altura': [self.datos_tocones[i]['altura'] for i in range(1, 13)],
                'tocon_num': list(range(1, 13)),
                'CT': [self.datos_tocones[i]['ct'] for i in range(1, 13)],
                'CD': [self.datos_tocones[i]['cd'] for i in range(1, 13)],
                'Ancho Bisagra (AB)': [self.datos_tocones[i]['ab'] for i in range(1, 13)],
                'Altura entre CT y CD': [self.datos_tocones[i]['altura1'] for i in range(1, 13)],
                'CT/d*100': [self.datos_tocones[i]['ct_d_ratio'] for i in range(1, 13)],
                'CD/d*100': [self.datos_tocones[i]['cd_d_ratio'] for i in range(1, 13)],
                'AB/d*100': [self.datos_tocones[i]['ab_d_ratio'] for i in range(1, 13)]
            }

            df = pd.DataFrame(data)
            downloads_folder = get_downloads_folder()
            filename = os.path.join(downloads_folder,
                                  f"Evaluacion_Tocones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            df.to_excel(filename, index=False)

            # Generar QR
            qr_data = f"""EVALUACIÓN DE TOCONES - DATOS COMPLETOS
Finca: {encabezado['finca']}
Lote: {encabezado['lote']}
Fecha: {encabezado['evaluacion']}

ARCHIVO GENERADO:
{filename}"""

            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(qr_data)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_filename = os.path.join(downloads_folder, "qr_tocones.png")
            qr_img.save(qr_filename)

            # Mostrar popup con opciones
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text='¡Datos guardados con éxito!', size_hint_y=None, height=dp(40)))
            content.add_widget(Label(text=f'Ubicación: {filename}', size_hint_y=None, height=dp(30)))

            qr_kivy = KivyImage(source=qr_filename, size_hint_y=0.6)
            content.add_widget(qr_kivy)

            btn_share = Button(text='Compartir Archivo' if platform == 'android' else 'Abrir Carpeta',
                             size_hint_y=None,
                             height=dp(50),
                             background_color=(0.2, 0.8, 0.4, 1))
            btn_share.bind(on_release=lambda x: share_file_android(filename))
            content.add_widget(btn_share)

            btn_close = Button(text='Cerrar',
                             size_hint_y=None,
                             height=dp(50),
                             background_color=ACCENT_COLOR)
            btn_close.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
            content.add_widget(btn_close)

            popup = Popup(title='Operación Exitosa',
                        content=content,
                        size_hint=(0.95, 0.95))
            popup.open()

        except Exception as e:
            popup = Popup(title='Error',
                        content=Label(text=f'Error al guardar: {str(e)}'),
                        size_hint=(0.8, 0.4))
            popup.open()

class FormularioToconScreen(Screen):
    def __init__(self, numero_tocon, datos_tocones, **kwargs):
        super().__init__(**kwargs)
        self.numero_tocon = numero_tocon
        self.datos_tocones = datos_tocones

        scroll = ScrollView(do_scroll_x=False)
        main_layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20), size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        title = Label(text=f'Datos del Tocón {numero_tocon}',
                    font_size=dp(24),
                    bold=True,
                    color=DARK_TEXT,
                    size_hint_y=None,
                    height=dp(50))
        main_layout.add_widget(title)

        form_layout = GridLayout(cols=2,
                               size_hint_y=None,
                               spacing=dp(15),
                               padding=dp(10),
                               row_default_height=dp(50))
        form_layout.bind(minimum_height=form_layout.setter('height'))

        campos = [
            ('Diámetro (d)', 'd'),
            ('Altura tocon', 'altura'),
            ('Corte de tala (CT)', 'ct'),
            ('Corte de dirección (CD)', 'cd'),
            ('Ancho Bisagra (AB)', 'ab'),
            ('Altura entre CT y CD', 'altura1')
        ]

        self.inputs = {}
        for label, name in campos:
            lbl = Label(text=label,
                      halign='left',
                      color=DARK_TEXT,
                      size_hint_y=None,
                      height=dp(40))
            form_layout.add_widget(lbl)

            ti = TextInput(multiline=False,
                         size_hint_y=None,
                         height=dp(40),
                         background_color=(1, 1, 1, 1))
            self.inputs[name] = ti
            form_layout.add_widget(ti)

        resultados = [
            ('CT/d*100', 'ct_d_ratio'),
            ('CD/d*100', 'cd_d_ratio'),
            ('AB/d*100', 'ab_d_ratio')
        ]

        for label, name in resultados:
            lbl = Label(text=label,
                      halign='left',
                      color=DARK_TEXT,
                      size_hint_y=None,
                      height=dp(40))
            form_layout.add_widget(lbl)

            result_lbl = Label(text='',
                             halign='left',
                             color=DARK_TEXT,
                             size_hint_y=None,
                             height=dp(40))
            self.inputs[name] = result_lbl
            form_layout.add_widget(result_lbl)

        main_layout.add_widget(form_layout)

        btn_calcular = Button(text='Calcular',
                            size_hint_y=None,
                            height=dp(60),
                            background_color=(0.3, 0.69, 0.49, 1),
                            color=LIGHT_TEXT)
        btn_calcular.bind(on_release=self.calcular_ratios)
        main_layout.add_widget(btn_calcular)

        btn_guardar = Button(text='Guardar',
                           size_hint_y=None,
                           height=dp(60),
                           background_color=PRIMARY_COLOR,
                           color=LIGHT_TEXT)
        btn_guardar.bind(on_release=self.guardar_datos)
        main_layout.add_widget(btn_guardar)

        btn_volver = Button(text='Volver',
                          size_hint_y=None,
                          height=dp(60),
                          background_color=ACCENT_COLOR,
                          color=LIGHT_TEXT)
        btn_volver.bind(on_release=lambda x: setattr(self.manager, 'current', 'ingreso_tocones'))
        main_layout.add_widget(btn_volver)

        scroll.add_widget(main_layout)
        self.add_widget(scroll)

        # Cargar datos existentes si los hay
        if numero_tocon in datos_tocones and datos_tocones[numero_tocon]:
            datos = datos_tocones[numero_tocon]
            for campo in ['d', 'altura', 'ct', 'cd', 'ab', 'altura1']:
                if campo in datos:
                    self.inputs[campo].text = datos[campo]
            for ratio in ['ct_d_ratio', 'cd_d_ratio', 'ab_d_ratio']:
                if ratio in datos:
                    self.inputs[ratio].text = datos[ratio]

    def calcular_ratios(self, instance):
        try:
            d = float(self.inputs['d'].text)
            ct = float(self.inputs['ct'].text)
            cd = float(self.inputs['cd'].text)
            ab = float(self.inputs['ab'].text)

            ct_d = (ct / d) * 100
            cd_d = (cd / d) * 100
            ab_d = (ab / d) * 100

            self.inputs['ct_d_ratio'].text = f"{ct_d:.1f}% {'✅' if abs(ct_d - 65) < 0.1 else '❌'}"
            self.inputs['cd_d_ratio'].text = f"{cd_d:.1f}% {'✅' if 20 <= cd_d <= 25 else '❌'}"
            self.inputs['ab_d_ratio'].text = f"{ab_d:.1f}% {'✅' if ab_d <= 10 else '❌'}"

        except ValueError:
            popup = Popup(title='Error',
                        content=Label(text='Por favor ingrese valores numéricos válidos'),
                        size_hint=(0.8, 0.4))
            popup.open()

    def guardar_datos(self, instance):
        if not self.inputs['ct_d_ratio'].text:
            self.calcular_ratios(instance)
            return

        self.datos_tocones[self.numero_tocon] = {
            'd': self.inputs['d'].text,
            'altura': self.inputs['altura'].text,
            'ct': self.inputs['ct'].text,
            'cd': self.inputs['cd'].text,
            'ab': self.inputs['ab'].text,
            'altura1': self.inputs['altura1'].text,
            'ct_d_ratio': self.inputs['ct_d_ratio'].text,
            'cd_d_ratio': self.inputs['cd_d_ratio'].text,
            'ab_d_ratio': self.inputs['ab_d_ratio'].text
        }

        popup = Popup(title='Éxito',
                    content=Label(text=f'Datos del Tocón {self.numero_tocon} guardados'),
                    size_hint=(0.7, 0.3))
        popup.open()

class ToconesApp(App):
    def build(self):
        Window.clearcolor = SECONDARY_COLOR
        sm = ScreenManager()
        sm.add_widget(MenuPrincipal(name='menu'))
        sm.add_widget(EncabezadoTocones(name='encabezado'))
        sm.add_widget(IngresoToconesScreen(name='ingreso_tocones'))
        return sm

if __name__ == '__main__':
    ToconesApp().run()