"""
addr: Audio Metadata Organiser
by Yunus Sufian
2023

Description:
This program is designed to organize audio metadata, including titles, artists, albums, and more. It allows you to manage your audio files by editing their metadata and converting them to the .m4a format.

Functionality:
- Drag and drop audio files for metadata editing and conversion.
- Edit song metadata fields such as title, artist, album, etc.
- Automatically convert audio files to the .m4a format.
- Option to mark songs as explicit.
- Save edited metadata to audio files.
"""
import sys
import os
import subprocess
from mutagen.mp4 import MP4
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QListWidget,
)
from PyQt5 import uic

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QAbstractItemView


# Custom QListWidget to handle drag-and-drop functionality
class ListboxWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.resize(600, 600)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            unique_links = set()

            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = str(url.toLocalFile())
                    if file_path not in unique_links:
                        unique_links.add(file_path)
                        self.addItem(file_path)
                else:
                    print("Not added")
        else:
            event.ignore()


# Class to represent a song
class Song:
    def __init__(self, title, artist, album, albumartist, genre, year, songpath):
        self.title = title
        self.artist = artist
        self.album = album
        self.albumartist = albumartist
        self.trackno = 1
        self.genre = genre
        self.year = year
        self.songpath = songpath

    def checkExt(self, songFilePath):
        if songFilePath.endswith(".m4a"):
            return songFilePath
        else:
            convFilePath = songFilePath[:-4] + ".m4a"
            ffmpeg_command = [
                "ffmpeg",
                "-i",
                songFilePath,
                "-c:a",
                "aac",
                "-strict",
                "experimental",
                "-b:a",
                "320k",
                convFilePath,
            ]
            subprocess.run(ffmpeg_command)
            return convFilePath

    def setSong(self, postSongFile):
        song = MP4(postSongFile)
        return song


# User interface class
class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        # Load the main.ui file using a relative path
        uic.loadUi(
            os.path.join(
                os.path.dirname(__file__ if __file__ else sys.argv[0]), "main.ui"
            ),
            self,
        )

        # Initialize the QListWidget for drag-and-drop
        self.listBox = ListboxWidget(self)
        self.ddLayout = self.findChild(QVBoxLayout, "ddLayout")
        self.ddLayout.addWidget(self.listBox)

        # Find and store references to various input fields
        self.titleField = self.findChild(QLineEdit, "titleField")
        self.artistField = self.findChild(QLineEdit, "artistField")
        self.albumField = self.findChild(QLineEdit, "albumField")
        self.albumArtistField = self.findChild(QLineEdit, "albumArtistField")
        self.genreField = self.findChild(QLineEdit, "genreField")
        self.yearField = self.findChild(QLineEdit, "yearField")
        self.trackField = self.findChild(QLineEdit, "trackField")
        self.explicitBox = self.findChild(QCheckBox, "explicitBox")
        self.saveButton = self.findChild(QPushButton, "saveButton")

        # Store references to input fields in the allFields list
        self.allFields = [
            self.titleField,
            self.artistField,
            self.albumField,
            self.albumArtistField,
            self.genreField,
            self.yearField,
            self.trackField,
        ]

        # Connect the save button's click event to the function
        self.saveButton.clicked.connect(self.clicker)

        self.show()

    # Handle save button click
    def clicker(self):
        if not self.listBox.selectedItems():
            print("No items selected. Please select items to save.")
            return

        textFields = [field.text() for field in self.allFields]
        explicit = self.explicitBox.isChecked()
        self.saveAndApply(textFields, explicit)

    # Retrieve selected items in the list
    def getSelectedItem(self):
        selectedItems = [item.text() for item in self.listBox.selectedItems()]
        if not selectedItems[0].endswith(".m4a"):
            selectedItems[0] = self.convert(selectedItems[0])
        return selectedItems

    # Convert audio file using ffmpeg
    def convert(self, preSongPath):
        conv = os.path.join(os.getcwd(), "conv")
        if not os.path.exists(conv):
            os.makedirs(conv)
        convFilePath = os.path.join(conv, os.path.basename(preSongPath)[:-4] + ".m4a")
        ffmpeg_command = [
            "ffmpeg",
            "-i",
            preSongPath,
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            "-b:a",
            "320k",
            convFilePath,
        ]
        subprocess.run(ffmpeg_command)
        print("\nConverted!\n")
        return convFilePath

    # Save metadata to the selected song
    def saveAndApply(self, textFields, explicit):
        songPathArray = self.getSelectedItem()
        if songPathArray:
            print(songPathArray[0])
            song = MP4(songPathArray[0])
            setMetadata(song, textFields, explicit)


# Function to set metadata for a song
def setMetadata(song, textFields, explicit):
    song["\xa9nam"] = textFields[0]
    song["\xa9ART"] = textFields[1]
    song["\xa9alb"] = textFields[2]
    song["aART"] = textFields[3]
    song["\xa9gen"] = textFields[4]
    try:
        year = str(textFields[5])
        song["year"] = year
    except ValueError:
        song["year"] = str(2023)
    song["trkn"] = [(1, 1)]
    if explicit:
        try:
            song["rtng"] = [1]
            song.save()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    else:
        print("not explicit")
    song.save()
    print("Success!")


app = QApplication(sys.argv)
UIWindow = UI()
sys.exit(app.exec())
