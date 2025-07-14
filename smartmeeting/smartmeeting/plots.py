def setup_matplotlib_fonts():
    """
    Detect and set appropriate matplotlib font for Chinese characters on different OS
    """
    import matplotlib.pyplot as plt
    import matplotlib
    import platform
    import subprocess
    import os

    # Avoid negative sign display issues
    matplotlib.rcParams["axes.unicode_minus"] = False

    system = platform.system()

    if system == "Darwin":  # macOS
        # macOS fonts that support Chinese
        mac_fonts = [
            "Arial Unicode MS",
            "PingFang SC",
            "Hiragino Sans GB",
            "STHeiti",
            "Apple LiGothic Medium",
        ]

        for font in mac_fonts:
            try:
                matplotlib.rcParams["font.family"] = font
                # Test if font works by creating a simple plot
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, "测试", fontsize=12)
                plt.close(fig)
                print(f"✅ Using macOS font: {font}")
                return font
            except:
                continue

    elif system == "Windows":
        # Windows fonts that support Chinese
        windows_fonts = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong"]

        for font in windows_fonts:
            try:
                matplotlib.rcParams["font.family"] = font
                # Test if font works
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, "测试", fontsize=12)
                plt.close(fig)
                print(f"✅ Using Windows font: {font}")
                return font
            except:
                continue

    elif system == "Linux":
        # Linux fonts that support Chinese
        linux_fonts = [
            "WenQuanYi Micro Hei",
            "WenQuanYi Zen Hei",
            "Noto Sans CJK SC",
            "Noto Sans CJK TC",
            "Droid Sans Fallback",
            "DejaVu Sans",
        ]

        for font in linux_fonts:
            try:
                matplotlib.rcParams["font.family"] = font
                # Test if font works
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, "测试", fontsize=12)
                plt.close(fig)
                print(f"✅ Using Linux font: {font}")
                return font
            except:
                continue

    # Fallback to default if no suitable font found
    print("⚠️ No suitable Chinese font found, using default")
    return None
