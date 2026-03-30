<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>pw-matrix | User Manual</title>
    <style>
        :root {
            --bg-dark: #252525;
            --bg-panel: #333333;
            --text-main: #eeeeee;
            --text-muted: #aaaaaa;
            --accent-orange: #FF9800;
            --accent-green: #4CAF50;
            --accent-red: #F44336;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-main);
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: var(--bg-panel);
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        h1 {
            color: var(--accent-orange);
            border-bottom: 2px solid var(--accent-orange);
            padding-bottom: 10px;
            margin-top: 0;
        }
        h2 {
            color: #ffffff;
            margin-top: 30px;
        }
        h3 {
            color: var(--accent-orange);
        }
        p {
            color: var(--text-muted);
        }
        code {
            background-color: #1e1e1e;
            color: #4CAF50;
            padding: 4px 8px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 14px;
        }
        pre {
            background-color: #1e1e1e;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            border: 1px solid #444;
        }
        pre code {
            background-color: transparent;
            padding: 0;
            color: #dddddd;
        }
        ul {
            color: var(--text-muted);
        }
        li {
            margin-bottom: 10px;
        }
        .highlight {
            color: var(--accent-orange);
            font-weight: bold;
        }
        .badge-green {
            background-color: rgba(76, 175, 80, 0.2);
            color: var(--accent-green);
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid var(--accent-green);
        }
        .badge-red {
            background-color: rgba(244, 67, 54, 0.2);
            color: var(--accent-red);
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid var(--accent-red);
        }
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #777;
            border-top: 1px solid #444;
            padding-top: 20px;
        }
        .slogan {
            font-style: italic;
            color: #cccccc;
            font-size: 14px;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>pw-matrix</h1>
    <p><em>Professional PipeWire Audio Routing Matrix</em></p>

    <h2>1. Overview</h2>
    <p><strong>pw-matrix</strong> is a lightweight, professional-grade visual patchbay for Linux systems running PipeWire. Designed with a DAW-style (Ardour/Reaper) matrix grid, it allows you to instantly route audio between hardware devices and software applications.</p>
    <p>It features automatic intelligent port aliasing (cleaning up ugly ALSA strings), crosshair highlighting to prevent routing mistakes, and a unique <strong>Diagonal Swipe</strong> feature for rapid bulk connections.</p>

    <hr style="border: 0; border-top: 1px solid #444; margin: 30px 0;">

    <h2>2. Installation Instructions</h2>
    <p>This application is written in Python and uses <strong>PyQt6</strong> for its graphical interface. It utilizes your system's native <code>pw-link</code> commands under the hood.</p>

    <h3>Prerequisites (Ubuntu / Debian)</h3>
    <p>Open your terminal and install the required Python bindings:</p>
    <pre><code>sudo apt update
sudo apt install python3-pyqt6</code></pre>

    <h3>Running the App</h3>
    <p>Make the script executable and launch it:</p>
    <pre><code>chmod +x pw_matrix.py
./pw_matrix.py</code></pre>

    <hr style="border: 0; border-top: 1px solid #444; margin: 30px 0;">

    <h2>3. User Manual</h2>

    <h3>Basic Navigation</h3>
    <ul>
        <li><strong>Sources (Outputs)</strong> are listed on the left axis.</li>
        <li><strong>Destinations (Inputs)</strong> are listed on the top axis.</li>
        <li><strong>Crosshair Hover:</strong> Move your mouse over any square in the grid. The corresponding Source and Destination text will light up in <span class="highlight">Orange</span>, acting as a visual crosshair so you never lose your place.</li>
    </ul>

    <h3>Making Connections</h3>
    <ul>
        <li><strong>Single Connect/Disconnect:</strong> Click any square in the grid to toggle a connection. Green means connected; dark grey means disconnected.</li>
        <li><strong>Diagonal Swipe Connect:</strong> To connect multiple 1-to-1 channels (e.g., L to L, R to R), <span class="badge-green">Left-Click & Drag</span> diagonally across the grid. A thick green line will appear. Release the mouse to instantly connect all intersected nodes.</li>
        <li><strong>Diagonal Swipe Disconnect:</strong> To rapidly delete connections, <span class="badge-red">Right-Click & Drag</span> diagonally. A thick red line will appear, breaking all intersected connections upon release.</li>
    </ul>

    <h3>Intelligent Naming</h3>
    <p>The app automatically detects messy PipeWire system names and cleans them up for a studio environment:</p>
    <ul>
        <li><code>monitor_aux_0</code> becomes <strong>d.out-1</strong> (Direct Out)</li>
        <li><code>playback_aux_2</code> becomes <strong>tx-3</strong> (Transmit/Send)</li>
        <li><code>playback_FL</code> becomes <strong>L</strong> (Left)</li>
        <li>MIDI nodes are automatically hidden to keep the audio routing clean.</li>
    </ul>

    <h3>State Saving & Autostart</h3>
    <p>Every time you click a box or make a swipe, your routing matrix is instantly saved to <code>~/.config/pw_matrix_routing.json</code>.</p>
    <p>To have your computer automatically restore your complex routing matrix every time you boot up without showing the GUI, add the script to your OS <em>Startup Applications</em> with the headless flag:</p>
    <pre><code>/path/to/pw_matrix.py --apply-only</code></pre>

    <div class="footer">
        <p class="slogan">"Bahwa sesungguhnya kemerdekaan itu ialah hak segala bangsa."</p>
        <p>developed by rekambergeraklab Yogyakarta-Indonesia v1.0.0</p>
    </div>
</div>

</body>
</html>
