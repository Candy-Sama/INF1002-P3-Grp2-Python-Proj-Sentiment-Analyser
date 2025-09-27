# Logo Placeholder

This folder is for image assets like logos, icons, and other graphics.

To add a logo:
1. Place your logo file (e.g., logo.png, logo.svg) in this directory
2. Reference it in HTML using: `{{ url_for('static', filename='images/logo.png') }}`
3. Use it in CSS using: `url("{{ url_for('static', filename='images/logo.png') }}")`

Current structure:
```
images/
├── README.md (this file)
└── (place your image files here)
```