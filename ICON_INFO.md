# G + Wallet application icon

- `glassbalance/assets/glassbalance_icon.svg`: editable vector master.
- `glassbalance/assets/glassbalance_icon.png`: 512px icon for Qt/Linux.
- `glassbalance/assets/glassbalance_icon.ico`: multi-resolution icon for Windows.
- `scripts/create_icon.py`: regenerates all icon formats using `cairosvg` and Pillow (asset generation only; these packages are not required to run the application).

The icon is created locally and does not require an external image service. GitHub builds bundle pre-generated assets.
