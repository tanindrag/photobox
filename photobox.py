import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QMessageBox, QComboBox, QGridLayout
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt


class PhotoboxApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photobox App")
        self.setGeometry(100, 100, 800, 600)
        self.photos_taken = []
        self.photo_index = 0
        self.cap = None
        self.timer = None
        self.countdown = 5  # Countdown timer in seconds

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # UI elements
        self.label = QLabel("Welcome to the Photobox App")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.package_label = QLabel("Select a Package:")
        self.package_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.package_label)

        self.package_selector = QComboBox()
        self.package_selector.addItem("Single (1 Print)")
        self.package_selector.addItem("Double (2 Prints)")
        self.package_selector.currentIndexChanged.connect(self.select_package)
        self.layout.addWidget(self.package_selector)

        self.btn_start_session = QPushButton("Start Photo Session")
        self.btn_start_session.clicked.connect(self.start_photo_session)
        self.layout.addWidget(self.btn_start_session)

        self.video_feed = QLabel(self)
        self.video_feed.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.video_feed)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_widget.setLayout(self.grid_layout)
        self.layout.addWidget(self.grid_widget)
        self.grid_widget.hide()

        self.btn_print_photos = QPushButton("Print Photos")
        self.btn_print_photos.clicked.connect(self.print_photos)
        self.layout.addWidget(self.btn_print_photos)
        self.btn_print_photos.setEnabled(False)

    def select_package(self):
        """Set the selected package."""
        index = self.package_selector.currentIndex()
        self.selected_package = "Single" if index == 0 else "Double"
        QMessageBox.information(self, "Package Selected", f"Selected Package: {self.selected_package}")

    def start_photo_session(self):
        """Start a session to automatically take six photos with a 10-second interval."""
        if not hasattr(self, 'selected_package') or not self.selected_package:
            QMessageBox.warning(self, "No Package Selected", "Please select a package first.")
            return

        self.photos_taken = []  # Reset the photos
        self.photo_index = 0  # Reset photo index
        self.cap = cv2.VideoCapture(0)  # Open the camera

        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Camera not detected.")
            return

        QMessageBox.information(self, "Photo Session", "Starting photo session. Photos will be taken every 5 seconds.")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.capture_photo)
        self.timer.start(5000) 
        # Update video feed
        self.feed_timer = QTimer(self)
        self.feed_timer.timeout.connect(self.update_feed)
        self.feed_timer.start(30)  # Refresh video feed every 30 ms

    def update_feed(self):
        """Display the live video feed with a countdown timer."""
        ret, frame = self.cap.read()
        if ret:
            # Add countdown timer overlay
            overlay_text = f"Time Remaining: {self.countdown} sec"
            cv2.putText(frame, overlay_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB for PyQt

            height, width, channel = frame.shape
            step = channel * width
            qimg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.video_feed.setPixmap(QPixmap.fromImage(qimg))

        # Countdown logic
        if self.countdown > 0 and self.photo_index < 6:
            self.countdown -= 1
        else:
            self.countdown = 10  # Reset for next photo


    def capture_photo(self):
        """Capture a single photo and store it."""
        ret, frame = self.cap.read()
        if ret:
            photo_name = f"photo_{self.photo_index + 1}.jpg"
            cv2.imwrite(photo_name, frame)
            self.photos_taken.append(photo_name)
            self.photo_index += 1
            print(f"Photo {self.photo_index} saved as {photo_name}.")

        if self.photo_index == 6:
            self.finish_session()

    def finish_session(self):
        """Stop the timer and show captured photos in a grid layout."""
        self.timer.stop()
        self.feed_timer.stop()
        self.cap.release()
        QMessageBox.information(self, "Session Complete", "Photo session completed. Showing captured photos.")

        # Display captured photos in a grid
        self.video_feed.clear()
        self.grid_widget.show()
        for i, photo in enumerate(self.photos_taken):
            row, col = divmod(i, 3)  # Arrange in 2 rows and 3 columns
            pixmap = QPixmap(photo).scaled(200, 150, Qt.KeepAspectRatio)
            photo_label = QLabel(self)
            photo_label.setPixmap(pixmap)
            self.grid_layout.addWidget(photo_label, row, col)

        self.btn_print_photos.setEnabled(True)

    def print_photos(self):
        """Simulate printing the captured photos."""
        QMessageBox.information(self, "Printing", "Printing photos...")
        num_prints = 1 if self.selected_package == "Single" else 2
        for _ in range(num_prints):
            print(f"Printing {len(self.photos_taken)} photos.")
        QMessageBox.information(self, "Print Complete", "Photos printed successfully.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoboxApp()
    window.show()
    sys.exit(app.exec_())
