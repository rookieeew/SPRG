import os
import sys

import numpy as np
import spectral.io.envi as envi
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QPixmap, QDoubleValidator
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QLabel, QWidget, QHBoxLayout, \
    QVBoxLayout, QLineEdit, QComboBox
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # main window
        self.setWindowTitle("UCD")
        self.setObjectName("MainWindow")
        self.setMinimumSize(650, 650)

        # main layout and widget
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")

        # wavelength part
        self.wavelengthLayout = QVBoxLayout()
        self.wavelengthLayout.setObjectName("wavelengthLayout")
        self.wavelengthWidget = QWidget()
        self.wavelengthWidget.setObjectName("wavelengthWidget")
        self.wavelengthWidget.setLayout(self.wavelengthLayout)
        self.wavelengthWidget.setFixedSize(650, 120)
        self.mainLayout.addWidget(self.wavelengthWidget, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        self.wavelengthsSelectorTitle = QLabel("Wavelength Selector")
        self.wavelengthsSelectorTitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.wavelengthLayout.addWidget(self.wavelengthsSelectorTitle, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.wavelengthsSelectorLayout = QHBoxLayout()
        self.wavelengthsSelectorLayout.setObjectName("wavelengthsSelectorLayout")
        self.wavelengthsSelectorWidget = QWidget()
        self.wavelengthsSelectorWidget.setObjectName("wavelengthsSelectorWidget")
        self.wavelengthsSelectorWidget.setLayout(self.wavelengthsSelectorLayout)
        self.wavelengthsSelectorWidget.setFixedSize(400, 50)
        self.wavelengthLayout.addWidget(self.wavelengthsSelectorWidget, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.wavelengthEdit = QLineEdit()
        self.wavelengthEdit.setObjectName("wavelengthWidget")
        self.wavelengthEdit.setPlaceholderText("Enter Wavelength")
        self.wavelengthEdit.setFixedWidth(120)
        self.wavelengthEdit.setValidator(QDoubleValidator())
        self.wavelengthEdit.setMaxLength(12)
        self.wavelengthEdit.returnPressed.connect(self.typed)
        self.wavelengthsSelectorLayout.addWidget(self.wavelengthEdit)

        self.wavelengthBtn = QPushButton()
        self.wavelengthBtn.setObjectName("wavelengthBtn")
        self.wavelengthBtn.setText("Enter")
        self.wavelengthBtn.setFixedWidth(80)
        self.wavelengthBtn.clicked.connect(self.typed)
        self.wavelengthsSelectorLayout.addWidget(self.wavelengthBtn)

        self.wavelengthComboBox = QComboBox()
        self.wavelengthComboBox.setObjectName("wavelengthComboBox")
        self.wavelengthComboBox.setFixedWidth(100)
        self.wavelengthsSelectorLayout.addWidget(self.wavelengthComboBox)
        # Notice that: when import all wavelength to this combox, it will trigger this attached function
        # So after loading files, the grayscale will render automatically
        self.wavelengthComboBox.currentTextChanged.connect(self.select_wavelength_from_combobox)

        self.imagePaletteLayout = QHBoxLayout()
        self.imagePaletteLayout.setObjectName("imagePaletteLayout")
        self.imagePaletteWidget = QWidget()
        self.imagePaletteWidget.setObjectName("imagePaletteWidget")
        self.imagePaletteWidget.setLayout(self.imagePaletteLayout)
        self.imagePaletteWidget.setFixedSize(200, 50)
        self.wavelengthLayout.addWidget(self.imagePaletteWidget, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.imagePaletteTitle = QLabel("Palette: ")
        self.imagePaletteTitle.setObjectName("imagePaletteTitle")
        self.imagePaletteLayout.addWidget(self.imagePaletteTitle)
        self.imagePaletteCombobox = QComboBox()
        self.imagePaletteCombobox.setObjectName("imagePaletteCombobox")
        self.imagePaletteCombobox.addItems(
            ['gray', 'viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Purples', 'Blues', 'Greens', 'Oranges',
             'Reds', 'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu', 'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn'])
        self.imagePaletteCombobox.currentIndexChanged.connect(self.selectColorImage)

        self.imagePaletteLayout.addWidget(self.imagePaletteCombobox)

        # grayscale part
        self.grayscaleImageLabel = QLabel()
        self.grayscaleImageLabel.setObjectName("grayscaleImageLabel")
        self.grayscaleImageLabel.setFixedSize(650, 500)

        self.mainWidget = QtWidgets.QWidget()
        self.mainWidget.setObjectName("mainWidget")
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        # add menubar
        self.menubar = QtWidgets.QMenuBar(parent=self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        # add menu
        self.menuFile = QtWidgets.QMenu(parent=self.menubar)
        self.menuFile.setObjectName("menuFile")

        # create action to each menu
        self.actionSave_As = QtGui.QAction(parent=self)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionSave = QtGui.QAction(parent=self)
        self.actionSave.setObjectName("actionSave")
        self.actionImport = QtGui.QAction(parent=self)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtGui.QAction(parent=self)
        self.actionExport.setObjectName("actionExport")
        # add action to parent menu
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)

        self.menubar.addAction(self.menuFile.menuAction())
        # add a slot to the action
        self.actionImport.triggered.connect(self.import_file)
        self.actionExport.triggered.connect(self.export_grayscale_image)

        self.retranslateUi()

        # data
        self.uploaded_files = []
        self.file_prefix = ""
        self.raw_data = ""
        self.wavelengths = ""
        self.grayscale_image = ""

    # slot
    def typed(self):
        if self.wavelengthEdit.text() == "":
            print("No Wavelength Typed")
        elif len(self.uploaded_files) < 2:
            print("Upload enough files")
        else:
            wavelength = float(self.wavelengthEdit.text())
            print("User entered " + str(wavelength))
            self.wavelengthComboBox.setCurrentText(self.wavelengthEdit.text())
            self.colorImage(wavelength, self.imagePaletteCombobox.currentText())

    def select_wavelength_from_combobox(self, s):
        self.wavelengthEdit.setText(self.wavelengthComboBox.currentText())
        wavelength = float(s)
        self.colorImage(wavelength, self.imagePaletteCombobox.currentText())

    def import_file(self):
        for i in range(2):
            file_dialog = QFileDialog.getOpenFileName(self, 'Open File', '', 'All Files (*.hdr *.raw)')
            self.uploaded_files.append(file_dialog[0])
        print("Upload files Successfully")
        self.file_prefix = os.path.splitext(os.path.basename(self.uploaded_files[0]))[0]
        if len(self.uploaded_files) == 2 and (self.uploaded_files[0] != "" and self.uploaded_files[1] != ""):
            # Perform further processing with the selected files
            self.read_data_from_files(self.uploaded_files)
        else:
            print("Lock files")

    def export_grayscale_image(self):
        saved_path = os.path.join(os.getcwd() + "/" + self.file_prefix + ".tif")
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image",
                                                   saved_path,
                                                   "TIFF Files (*.tif)")
        if file_path:
            pixmap = self.grayscale_image

            # Save the QPixmap to the specified file path
            pixmap.save(file_path)
            print("Save Grayscale image is successfully")
            print(f"Grayscale image exported to: {file_path}")

    # write co
    def read_data_from_files(self, file_paths):
        for path in file_paths:
            if path.endswith("hdr"):
                hdr_file = path
            else:
                raw_file = path
        # read data
        hdr = envi.read_envi_header(hdr_file)
        raw_data = np.fromfile(raw_file, dtype=np.uint16)

        # Extract necessary information using regular expressions
        wavelengths = np.array([float(x) for x in hdr["wavelength"]])
        wavelengths = list(dict.fromkeys(wavelengths))
        wavelengths.sort()
        wavelengths = np.array(wavelengths)
        lines = int(hdr["lines"])
        samples = int(hdr["samples"])
        bands = int(hdr["bands"])

        # pre-process the raw data
        raw_data = raw_data.reshape((lines, bands, samples))

        self.raw_data = raw_data
        self.wavelengths = wavelengths
        self.wavelengthComboBox.addItems(np.array([str(i) for i in self.wavelengths]))

    def colorImage(self, wavelength, color='gray'):
        print(f"wavelength{wavelength}")
        desired_wavelength = wavelength

        # Find the index corresponding to the desired wavelength
        wavelength_index = np.abs(self.wavelengths - desired_wavelength).argmin()
        desired_wavelength_data = self.raw_data[:, :, wavelength_index]

        # Apply a colormap to enhance contrast or assign different colors to different intensity levels
        cmap = plt.get_cmap(color)
        norm = plt.Normalize(vmin=desired_wavelength_data.min(),
                             vmax=desired_wavelength_data.max())  # Normalize the data
        colored_data = cmap(norm(desired_wavelength_data))  # Apply colormap to the data

        # Display colorful grayscale image
        fig, ax = plt.subplots()

        # Display colorful grayscale image on the axis
        im = ax.imshow(colored_data, cmap=cmap, aspect='auto')  # Add aspect='auto' here
        ax.set_title(f'Image for Wavelength {desired_wavelength} nm')
        # Create color bar corresponding to the colormap
        cbar = fig.colorbar(im, ax=ax, label='Intensity', orientation='vertical', cmap=cmap)
        cbar.set_label("Intensity")
        # Set x and y axis labels
        plt.xlabel('(μm)')
        plt.ylabel('(μm)')

        # Convert the figure to a canvas
        canvas = FigureCanvas(fig)
        canvas.draw()

        # Convert the rendered canvas to a QImage
        qimage = canvas.grab().toImage()
        self.grayscale_image = qimage

        # Create a QLabel to display the image
        pixmap = QPixmap.fromImage(qimage)
        self.grayscaleImageLabel.setPixmap(pixmap)
        self.mainLayout.addWidget(self.grayscaleImageLabel)

    def selectColorImage(self):
        if self.wavelengthComboBox.currentText() != "":
            wavelength = float(self.wavelengthComboBox.currentText())
            self.colorImage(wavelength, self.imagePaletteCombobox.currentText())
        else:
            print("You need to select a specific wavelength")

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "UCD Spectral Imaging Research Group(SIRG)"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionImport.setText(_translate("MainWindow", "Import"))
        self.actionExport.setText(_translate("MainWindow", "Export"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
