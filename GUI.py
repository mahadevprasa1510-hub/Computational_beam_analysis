from PySide6.QtWidgets import (QMainWindow, 
                               QLabel,
                               QLineEdit,
                               QComboBox,
                               QVBoxLayout,
                               QFileDialog,
                               QWidget,
                               QSplitter,
                               QGridLayout,
                               QMessageBox,
                               QTabWidget
                               ) 

from PySide6.QtGui import QAction

from PySide6.QtCore import Qt

from Analytical_solver import solve_simply_supported_beam, solve_cantilever_beam

import json

from I_O_module import *

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from visualization import (
    plot_deflected_shape,
    plot_bending_moment_diagram,
    plot_shear_force_diagram,
)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Computational Beam Analysis")

    # -----------------
    # widgets
    # -----------------

        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        input_widget = QWidget()
        result_widget = QWidget()
        input_widget.setObjectName("inputPanel")
        result_widget.setObjectName("resultPanel")

        input_widget.setStyleSheet(
            "#inputPanel { border: 1px solid gray; }"
        )

        result_widget.setStyleSheet(
            "#resultPanel { border: 1px solid gray; }"
        )

        
        input_layout = QVBoxLayout()
        result_layout = QVBoxLayout()
        input_widget.setLayout(input_layout)
        result_widget.setLayout(result_layout)
        input_layout.setAlignment(Qt.AlignTop)



        label_1 = QLabel(text="Inputs")
        label_2 = QLabel(text = "Results")
        label_1.setAlignment(Qt.AlignHCenter)
        label_2.setAlignment(Qt.AlignHCenter)

        input_layout.addWidget(label_1)
        result_layout.addWidget(label_2)
        input_grid = QGridLayout()
        input_layout.addLayout(input_grid)


    # -----------------
    # splitter
    # -----------------  
               
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        splitter.addWidget(input_widget)
        splitter.addWidget(result_widget)
        layout.addWidget(splitter)

    # -----------------
    # File Menu
    # -----------------

        file_menu = self.menuBar().addMenu("File")

        open_action = QAction("Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)

        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

    # -----------------
    # Tool Bar
    # -----------------

        toolbar = self.addToolBar("Toolbar")

        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addSeparator()
        toolbar.addAction(exit_action)

    # -----------------
    # Analysis Menu
    # -----------------

        analysis_menu = self.menuBar().addMenu("Analysis")
        analysis_action = QAction("Run Analysis", self)
        analysis_action.setShortcut("Ctrl+R")
        analysis_action.triggered.connect(self.analysis)
        analysis_menu.addAction(analysis_action)

    # -----------------
    # Status Bar
    # -----------------

        self.statusBar().showMessage("Ready")

    # -----------------
    # Combo  Box
    # -----------------

        self.boundary_condition_combo = QComboBox()
        boundary_types= ["Simply Supported", "Cantilever"]
        self.boundary_condition_combo.addItems(boundary_types)
        label_3 = QLabel(text="Boundary condition")
        input_grid.addWidget(label_3,1,0)
        input_grid.addWidget(self.boundary_condition_combo,1,1)

        self.load_type_combo = QComboBox()
        load_types =  ["Point load", "UDL"]
        self.load_type_combo.addItems(load_types)
        label_4 = QLabel(text="Load type")
        input_grid.addWidget(label_4,2,0)
        input_grid.addWidget(self.load_type_combo,2,1)

# -----------------
# Inputs
# -----------------

        self.length_label = QLabel("Beam Length")
        self.length_input = QLineEdit()
        self.length_unit = QLabel("m")

        self.load_label = QLabel("Load Magnitude")
        self.load_input = QLineEdit()
        self.load_unit = QLabel("kN")

        youngs_modulus_label = QLabel("Young's Modulus (E)")
        self.youngs_modulus_input = QLineEdit()
        youngs_modulus_unit = QLabel("MPa")

        moment_of_inertia_label = QLabel("Second Moment of Area (I)")
        self.moment_of_inertia_input = QLineEdit()
        moment_of_inertia_unit = QLabel("mm⁴")

        self.load_position_label = QLabel("Point Load Position")
        self.load_position_input = QLineEdit()
        self.load_position_unit = QLabel("m")

        self.beam_ID_label = QLabel("Beam ID")
        self.beam_ID_input = QLineEdit()
        input_grid.addWidget(self.beam_ID_label,0,0)
        input_grid.addWidget(self.beam_ID_input,0,1)


        widgets = [
            (self.length_label, self.length_input, self.length_unit),
            (self.load_label, self.load_input, self.load_unit),
            (youngs_modulus_label, self.youngs_modulus_input, youngs_modulus_unit),
            (moment_of_inertia_label, self.moment_of_inertia_input, moment_of_inertia_unit),
            (self.load_position_label, self.load_position_input, self.load_position_unit)
]

        for row, (label, input_widget, unit) in enumerate(widgets):
            input_grid.addWidget(label, row + 3, 0)
            input_grid.addWidget(input_widget, row + 3, 1)
            input_grid.addWidget(unit, row + 3, 2)

        self.load_type_combo.currentTextChanged.connect(
            self.update_load_inputs
        )


        self.load_type_combo.currentTextChanged.connect(
            self.update_load_inputs)
        self.update_load_inputs(
                                 self.load_type_combo.currentText()
                                )

    # -----------------
    # Result label
    # -----------------

        self.results_label = QLabel("Results will appear here.")
        self.results_label.setWordWrap(True)
        self.results_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        result_layout.addWidget(self.results_label)

    # -----------------
    # Tabs
    # -----------------  
        self.plot_tabs = QTabWidget()
        self.plot_tabs.setMinimumHeight(300)

        result_layout.addWidget(self.plot_tabs)

    # -----------------
    # Assumptions label
    # -----------------
        assumptions_title = QLabel("<b><u>Assumptions & Limitations</u></b><br>")
        assumptions_title.setAlignment(Qt.AlignHCenter)

        assumptions_text = QLabel(
    "• Prismatic beam with constant flexural rigidity EI.\n"
    "• Linear-elastic material behaviour.\n"
    "• Small deflections and rotations.\n"
    "• Idealized supports and static loading.\n"
    "• Euler-Bernoulli beam theory; shear deformation neglected.\n"
    "• Supports only these four boundary conditions: Simply Supported,\n "
    "  Cantilever, Fixed-Fixed, and Propped Cantilever.\n"
    "• Only downward point loads and downward full-span UDLs are supported.\n"
    "• Results require engineering verification and are not a design-code "
    "compliance check."
)

        assumptions_text.setWordWrap(True)
        input_grid.addWidget(assumptions_title, 8,0)
        input_grid.addWidget(assumptions_text,9,0)

    # -----------------
    # Action Functions
    # -----------------
    
    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Beam Model",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        # Collect input data from the GUI
        beam_data = {
            "beam_ID":self.beam_ID_input.text(),
            "boundary_condition": self.boundary_condition_combo.currentText(),
            "load_type": self.load_type_combo.currentText(),
            "length": self.length_input.text(),
            "load_magnitude": self.load_input.text(),
            "youngs_modulus": self.youngs_modulus_input.text(),
            "moment_of_inertia": self.moment_of_inertia_input.text(),
            "load_position": (
                self.load_position_input.text()
                if self.load_type_combo.currentText() == "Point load"
                else None
            )
        }

        try:
            if not file_path.lower().endswith(".json"):
                file_path += ".json"

            save_beam_data(file_path, beam_data)

        except (OSError, TypeError, ValueError) as error:
            QMessageBox.critical(
                self, "Save Failed", str(error)
            )
            return

        self.statusBar().showMessage("Beam model saved successfully.")


    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Beam Model",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            beam_data = load_beam_data(file_path)

            # Check required keys before updating the GUI
            required_keys = {
                "beam_ID",
                "boundary_condition",
                "load_type",
                "length",
                "load_magnitude",
                "youngs_modulus",
                "moment_of_inertia",
                "load_position"
            }

            if not required_keys.issubset(beam_data):
                raise ValueError("The JSON file is missing required fields.")

            # Validate dropdown selections before changing the GUI
            if beam_data["boundary_condition"] not in [
                self.boundary_condition_combo.itemText(i)
                for i in range(self.boundary_condition_combo.count())
            ]:
                raise ValueError("Unknown boundary condition in the JSON file.")

            if beam_data["load_type"] not in [
                self.load_type_combo.itemText(i)
                for i in range(self.load_type_combo.count())
            ]:
                raise ValueError("Unknown load type in the JSON file.")

            # Populate the GUI
            self.beam_ID_input.setText(beam_data["beam_ID"])
            self.boundary_condition_combo.setCurrentText(
                beam_data["boundary_condition"]
            )
            self.load_type_combo.setCurrentText(beam_data["load_type"])

            self.length_input.setText(str(beam_data["length"]))
            self.load_input.setText(str(beam_data["load_magnitude"]))
            self.youngs_modulus_input.setText(
                str(beam_data["youngs_modulus"])
            )
            self.moment_of_inertia_input.setText(
                str(beam_data["moment_of_inertia"])
            )

            self.load_position_input.setText(
                "" if beam_data["load_position"] is None
                else str(beam_data["load_position"])
            )

            # Refresh visibility of point-load position fields
            self.update_load_inputs(beam_data["load_type"])

        except (OSError, json.JSONDecodeError, ValueError, TypeError) as error:
            QMessageBox.critical(
                self, "Open Failed", str(error)
            )
            return

        self.statusBar().showMessage("Beam model loaded successfully.")


    def analysis(self):
        self.statusBar().showMessage("Running Analysis...")

        try:
            # 1. Read inputs
            length = float(self.length_input.text())
            E = float(self.youngs_modulus_input.text())
            I = float(self.moment_of_inertia_input.text())

            load_type = self.load_type_combo.currentText()
            load_magnitude = float(self.load_input.text())

            if load_type == "Point load":
                load_position = float(self.load_position_input.text())
            else:
                load_position = None

            # 2. Select the solver
            boundary_condition = (
                self.boundary_condition_combo.currentText()
            )

            if boundary_condition == "Simply Supported":
                solver = solve_simply_supported_beam

            elif boundary_condition == "Cantilever":
                solver = solve_cantilever_beam

            else:
                QMessageBox.information(
                    self,
                    "Not Yet Supported",
                    "This boundary condition is not supported yet."
                )
                return

            # 3. Run the analysis
            results = solver(
                length,
                E,
                I,
                load_type,
                load_magnitude,
                load_position,
            )

            # 4. Determine maximum shear location
            if boundary_condition == "Simply Supported":

                if load_type == "Point load":
                    if abs(results["reaction_A_kN"]) >= abs(
                        results["reaction_B_kN"]
                    ):
                        shear_location = "just right of Support A"
                    else:
                        shear_location = "just left of Support B"
                else:
                    shear_location = "at either support"

            else:
                shear_location = (
                    "just to the right of fixed support A"
                )

            # 5. Format support reactions
            if boundary_condition == "Cantilever":
                reaction_text = (
                    "<b><u>FIXED SUPPORT REACTIONS</u></b><br>"
                    f"Vertical reaction at A: "
                    f"{results['reaction_A_kN']:.3f} kN<br>"
                    f"Fixed-end moment at A: "
                    f"{results['fixed_end_moment_kNm']:.3f} "
                    "kN·m<br><br>"
                )
            else:
                reaction_text = (
                    "<b><u>REACTIONS</u></b><br>"
                    f"Reaction at A: "
                    f"{results['reaction_A_kN']:.3f} kN<br>"
                    f"Reaction at B: "
                    f"{results['reaction_B_kN']:.3f} kN<br><br>"
                )

            # 6. Format numerical results
            result_text = (
                f"{reaction_text}"
                "<b><u>MAXIMUM SHEAR FORCE</u></b><br>"
                f"{results['max_shear_kN']:.3f} kN<br>"
                f"Location: {shear_location}<br><br>"

                "<b><u>MAXIMUM BENDING MOMENT</u></b><br>"
                f"{results['max_moment_kNm']:.3f} kN·m<br>"
                f"Position: "
                f"{results['max_moment_position_m']:.3f} m<br><br>"

                "<b><u>MAXIMUM DEFLECTION</u></b><br>"
                f"{results['max_deflection_mm']:.4f} mm<br>"
                f"Position: "
                f"{results['max_deflection_position_m']:.3f} m"
            )
            self.results_label.setText(result_text)

            # 7. Update the plots using the same solver results
            self._update_plots(results)

            self.statusBar().showMessage("Analysis completed.")

        except (ValueError, KeyError) as error:
            self.statusBar().showMessage("Analysis failed.")
            QMessageBox.critical(
                self,
                "Analysis Failed",
                str(error)
            )



    def update_load_inputs(self, load_type):
        if load_type == "Point load":
            self.load_unit.setText("kN")

            self.load_position_label.setVisible(True)
            self.load_position_input.setVisible(True)
            self.load_position_unit.setVisible(True)

        elif load_type == "UDL":
            self.load_unit.setText("kN/m")

            self.load_position_label.setVisible(False)
            self.load_position_input.setVisible(False)
            self.load_position_unit.setVisible(False)

    
    def _update_plots(self, results):
        """Create and display the three beam-response plots."""

        # Remove plots from the previous analysis.
        while self.plot_tabs.count():
            old_widget = self.plot_tabs.widget(0)
            self.plot_tabs.removeTab(0)
            old_widget.deleteLater()

        # Generate figures using the solver's results.
        figures = [
            ("Deflected Shape", plot_deflected_shape(results)),
            ("BMD", plot_bending_moment_diagram(results)),
            ("SFD", plot_shear_force_diagram(results)),
        ]

        # Embed each Matplotlib figure into a Qt tab.
        for title, figure in figures:
            canvas = FigureCanvasQTAgg(figure)
            canvas.draw()
            self.plot_tabs.addTab(canvas, title)