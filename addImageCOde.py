right_widget = QWidget()
right_layout = QVBoxLayout()

# Upper part - Image with version and username
upper_widget = QWidget()
upper_widget.setMinimumHeight(200)
upper_widget.setStyleSheet("""
    QWidget {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 #87CEEB, stop:1 #4A90E2);
        border-radius: 10px;
    }
""")

# Create layout for upper widget
upper_layout = QVBoxLayout()
upper_layout.setContentsMargins(0, 0, 0, 0)
upper_layout.setSpacing(0)

# Add image label
image_label = QLabel()
image_label.setStyleSheet("background: transparent;")
pixmap = QPixmap(r'C:\Users\parul\Desktop\iaf.jpeg')  # Replace with your image path

# Scale the image to fill the width while maintaining aspect ratio
# The image will scale to fit the widget size
image_label.setPixmap(pixmap)
image_label.setScaledContents(True)  # This makes the image scale with the label
image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

# Create a container for image (this will take most of the space)
image_container = QWidget()
image_container.setStyleSheet("background: transparent;")
image_container_layout = QVBoxLayout()
image_container_layout.setContentsMargins(0, 0, 0, 0)
image_container_layout.addWidget(image_label)
image_container.setLayout(image_container_layout)

upper_layout.addWidget(image_container, stretch=1)

# Create horizontal layout for username and version labels
labels_widget = QWidget()
labels_widget.setStyleSheet("background: transparent;")
labels_layout = QHBoxLayout()
labels_layout.setContentsMargins(10, 5, 10, 10)

username_label = QLabel(f'User: {self.username}')
username_label.setStyleSheet('color: white; font-size: 14px; font-weight: bold; background: transparent;')
username_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

version_label = QLabel('Version: 1.0.0')
version_label.setStyleSheet('color: white; font-size: 14px; font-weight: bold; background: transparent;')
version_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)

labels_layout.addWidget(username_label)
labels_layout.addStretch()
labels_layout.addWidget(version_label)

labels_widget.setLayout(labels_layout)
upper_layout.addWidget(labels_widget)

upper_widget.setLayout(upper_layout)