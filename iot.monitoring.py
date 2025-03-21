from flask import Flask
import dash
from dash import html, dcc
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import random
from datetime import datetime, timedelta
import socket
import threading
import time
import cv2
import numpy as np
import mss

# Initialize Flask and Dash
server = Flask(__name__)
app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True)

# Server host details (no longer shown in layout)
host_info = {
    "hostname": socket.gethostname(),
    "ip_address": socket.gethostbyname(socket.gethostname()),
}

# Global flag and thread handle for screen recording
recording_flag = False
recording_thread = None

# IoT devices with enhanced AI and predictive features
devices = {
    "Smart Thermostat": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                           "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.95,
                           "threat_score": 0.1, "health_score": 90, "ai_log": [], "anomaly_detected": False,
                           "maintenance_alert": None, "optimization_suggestion": None,
                           "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Security Camera": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                        "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.98,
                        "threat_score": 0.05, "health_score": 95, "ai_log": [], "anomaly_detected": False,
                        "maintenance_alert": None, "optimization_suggestion": None,
                        "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Smart Lock": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                   "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.90,
                   "threat_score": 0.15, "health_score": 85, "ai_log": [], "anomaly_detected": False,
                   "maintenance_alert": None, "optimization_suggestion": None,
                   "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Smart Light": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                    "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.92,
                    "threat_score": 0.12, "health_score": 88, "ai_log": [], "anomaly_detected": False,
                    "maintenance_alert": None, "optimization_suggestion": None,
                    "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Smart Speaker": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                      "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.93,
                      "threat_score": 0.08, "health_score": 92, "ai_log": [], "anomaly_detected": False,
                      "maintenance_alert": None, "optimization_suggestion": None,
                      "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Smart Fridge": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                     "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.96,
                     "threat_score": 0.07, "health_score": 94, "ai_log": [], "anomaly_detected": False,
                     "maintenance_alert": None, "optimization_suggestion": None,
                     "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Smart TV": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                 "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.94,
                 "threat_score": 0.09, "health_score": 91, "ai_log": [], "anomaly_detected": False,
                 "maintenance_alert": None, "optimization_suggestion": None,
                 "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Smart Doorbell": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                       "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.97,
                       "threat_score": 0.06, "health_score": 96, "ai_log": [], "anomaly_detected": False,
                       "maintenance_alert": None, "optimization_suggestion": None,
                       "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Smart AC": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                 "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.91,
                 "threat_score": 0.13, "health_score": 87, "ai_log": [], "anomaly_detected": False,
                 "maintenance_alert": None, "optimization_suggestion": None,
                 "failure_probability": 0.0, "predicted_maintenance_date": None},
    "Smart Washer": {"status": "Online", "ai_shield": True, "vision_status": "Active", "last_scan": "Clean",
                     "scan_log": ["Starting scan..."], "error_log": ["No issues"], "ai_confidence": 0.89,
                     "threat_score": 0.14, "health_score": 86, "ai_log": [], "anomaly_detected": False,
                     "maintenance_alert": None, "optimization_suggestion": None,
                     "failure_probability": 0.0, "predicted_maintenance_date": None},
}

# Notification storage and time markers
notifications = []
last_hourly_check = datetime.now()
last_30min_check = datetime.now()

# Utility functions for logs
def generate_scan_log(device):
    messages = [
        f"[{datetime.now().strftime('%H:%M:%S')}] Vision scan on {device}...",
        f"[{datetime.now().strftime('%H:%M:%S')}] AI analysis complete: {devices[device]['last_scan']}"
    ]
    return random.choice(messages)

def generate_error_log(device):
    error_types = {
        "Smart Thermostat": "Temp anomaly detected - AI corrected",
        "Security Camera": "Vision blur detected - AI enhanced",
        "Smart Lock": "Access violation - AI locked",
        "Smart Light": "Light flicker - AI stabilized",
        "Smart Speaker": "Audio distortion - AI fixed",
        "Smart Fridge": "Door left open - AI alerted",
        "Smart TV": "Screen glitch - AI resolved",
        "Smart Doorbell": "False detection - AI filtered",
        "Smart AC": "Vent blockage - AI cleared",
        "Smart Washer": "Water overflow - AI stopped"
    }
    messages = [
        f"[{datetime.now().strftime('%H:%M:%S')}] Critical failure - AI rebooting",
        f"[{datetime.now().strftime('%H:%M:%S')}] Vision module offline - AI restoring",
        f"[{datetime.now().strftime('%H:%M:%S')}] {error_types[device]}"
    ]
    return random.choice(messages if random.random() < 0.3 else [f"[{datetime.now().strftime('%H:%M:%S')}] No issues detected"])

def generate_ai_log(device):
    actions = [
        f"[{datetime.now().strftime('%H:%M:%S')}] AI adjusted {device} parameters",
        f"[{datetime.now().strftime('%H:%M:%S')}] Threat prediction updated for {device}",
        f"[{datetime.now().strftime('%H:%M:%S')}] Health score recalculated for {device}",
        (f"[{datetime.now().strftime('%H:%M:%S')}] Anomaly detection triggered for {device}"
         if devices[device]['anomaly_detected'] else f"[{datetime.now().strftime('%H:%M:%S')}] No anomalies in {device}"),
        (f"[{datetime.now().strftime('%H:%M:%S')}] Maintenance scheduled for {device}"
         if devices[device]['maintenance_alert'] else f"[{datetime.now().strftime('%H:%M:%S')}] No maintenance needed for {device}"),
        (f"[{datetime.now().strftime('%H:%M:%S')}] Optimization applied: {devices[device]['optimization_suggestion']}"
         if devices[device]['optimization_suggestion'] else f"[{datetime.now().strftime('%H:%M:%S')}] No optimization needed for {device}")
    ]
    return random.choice(actions)

def format_device_info(device, data):
    """Combine all device data, logs, and detailed diagnostics into a formatted string."""
    info = [
        f"Device: {device}",
        f"Status: {data['status']}",
        f"AI Shield: {'Active' if data['ai_shield'] else 'Inactive'}",
        f"Vision Module: {data['vision_status']}",
        f"AI Confidence: {data['ai_confidence']:.2f}",
        f"Threat Score: {data['threat_score']:.2f}",
        f"Health Score: {data['health_score']}",
        f"Anomaly: {'Yes' if data['anomaly_detected'] else 'No'}",
        f"Maintenance: {data['maintenance_alert'] or 'None'}",
        f"Optimization: {data['optimization_suggestion'] or 'None'}",
        f"Failure Probability: {data['failure_probability']:.2f}",
        f"Predicted Maintenance: {data['predicted_maintenance_date'] or 'N/A'}",
        f"Last Scan: {data['last_scan']}",
        ""
    ]
    # Extra forensic details per device
    if device == "Smart Thermostat":
        info.append("Forensics: Current Temperature is 21°C (Desired: 22°C). Sensor calibration applied.")
    elif device == "Security Camera":
        info.append("Forensics: Movement detected at front door at " + datetime.now().strftime("%H:%M:%S") + ". Video snippet saved.")
    elif device == "Smart Lock":
        info.append("Forensics: Door unlocked by user 'Alice' at " + datetime.now().strftime("%H:%M:%S") + ". Access log updated.")
    elif device == "Smart Light":
        info.append("Forensics: Dynamic color cycle activated. Light intensity stabilized.")
    elif device == "Smart Speaker":
        info.append("Forensics: Now playing 'Imagine' by John Lennon. Audio normalization applied.")
    elif device == "Smart Fridge":
        info.append("Forensics: Fridge temperature steady at 4°C. Inventory: Milk, Eggs, Cheese verified.")
    elif device == "Smart TV":
        num_games = random.randint(2, 4)
        possible_games = [
            "Champions League: PSG vs Liverpool", 
            "Champions League: Real Madrid vs Barcelona", 
            "Champions League: Manchester City vs Bayern", 
            "Champions League: Juventus vs AC Milan"
        ]
        games = random.sample(possible_games, num_games)
        info.append("Forensics: Programs watched: " + ", ".join(games) + ". Streaming quality optimized.")
    elif device == "Smart Doorbell":
        info.append("Forensics: Visitor snapshot captured at " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ". Facial recognition initiated.")
    elif device == "Smart AC":
        info.append("Forensics: Cooling mode active. Set to 18°C. Airflow optimized.")
    elif device == "Smart Washer":
        info.append("Forensics: Laundry cycle in progress (Spin cycle at 80%). Load balanced.")
    
    # Append logs
    info.append("")
    info.append("Scan Log:")
    info.append("\n".join(data['scan_log']))
    info.append("")
    info.append("Error Log:")
    info.append("\n".join(data['error_log']))
    info.append("")
    info.append("AI Log:")
    info.append("\n".join(data['ai_log']))
    
    # Detailed Diagnostics (rich details about issues and fixes)
    diagnostics = []
    diagnostics.append("Detailed Diagnostics:")
    if data['anomaly_detected']:
        diagnostics.append("- Issue: Anomaly detected in sensor data.")
        diagnostics.append("- Resolution: AI recalibrated sensors and updated threat model.")
    else:
        diagnostics.append("- Issue: No significant anomalies detected.")
        diagnostics.append("- Resolution: Device operating within normal parameters.")
    if data['maintenance_alert']:
        diagnostics.append(f"- Maintenance Recommendation: {data['maintenance_alert']}. Schedule service immediately.")
    else:
        diagnostics.append("- Maintenance: No immediate service required.")
    if data['optimization_suggestion']:
        diagnostics.append(f"- Optimization: {data['optimization_suggestion']} applied.")
    else:
        diagnostics.append("- Optimization: No changes necessary.")
    diagnostics.append("- Overall, AI successfully monitored and auto-corrected issues where necessary.")
    info.append("")
    info.append("\n".join(diagnostics))
    
    return "\n".join(info)

# Screen recording function using opencv-python (MP4 format), with manual stop support
def record_screen():
    global recording_flag
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primary monitor
        fps = 20
        width = monitor["width"]
        height = monitor["height"]
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter("screen_record.mp4", fourcc, fps, (width, height))
        start_time = time.time()
        while recording_flag and (time.time() - start_time < 60):
            sct_img = sct.grab(monitor)
            frame = np.array(sct_img)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            out.write(frame)
            time.sleep(1 / fps)
        out.release()

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Quantum Vision Control Center</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                background: linear-gradient(135deg, #1a2525 0%, #0a1414 100%);
                font-family: 'Arial', sans-serif;
                color: #e6f0fa;
                margin: 0;
                padding: 30px;
                overflow-x: hidden;
            }
            .container {
                max-width: 1500px;
                margin: 0 auto;
                position: relative;
            }
            .header {
                background: rgba(10, 20, 30, 0.9);
                border-radius: 15px;
                padding: 30px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.7);
                border: 1px solid #2e4057;
                margin-bottom: 20px;
                position: relative;
            }
            .eye-icon {
                position: absolute;
                top: 20px;
                left: 20px;
                font-size: 32px;
                color: #5e8299;
                animation: blink 3s infinite;
            }
            @keyframes blink {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .notification-banner {
                background: linear-gradient(45deg, #ff6b6b, #d9534f);
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                font-weight: bold;
            }
            .manual-controls {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            .manual-controls button {
                background: linear-gradient(45deg, #3e5c76, #5e8299);
                border: none;
                padding: 10px 20px;
                border-radius: 20px;
                color: #e6f0fa;
                cursor: pointer;
                font-weight: bold;
                transition: all 0.3s ease;
                box-shadow: 0 2px 10px rgba(62, 92, 118, 0.5);
            }
            .manual-controls button:hover {
                background: linear-gradient(45deg, #5e8299, #7aa5c2);
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(62, 92, 118, 0.7);
            }
            .device-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                gap: 20px;
            }
            .device-card {
                background: linear-gradient(145deg, #2e4057, #1a2525);
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
                border: 1px solid #3e5c76;
                transition: all 0.3s ease;
            }
            .device-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 20px rgba(62, 92, 118, 0.4);
            }
            .terminal {
                background: #0a1414;
                color: #66d9ef;
                font-family: 'Courier New', monospace;
                padding: 12px;
                border-radius: 8px;
                height: 250px;
                overflow-y: auto;
                font-size: 11px;
                margin-top: 12px;
                border: 1px solid #2e4057;
                white-space: pre-wrap;
            }
            .graph-container {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin: 30px 0;
            }
            .graph-card {
                background: rgba(10,20,30,0.9);
                border-radius: 12px;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.7);
                border: 1px solid #2e4057;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Dashboard layout (without separate server info or AI summary sections)
app.layout = html.Div(className='container', children=[
    html.Div(className='header', children=[
        html.Span("👁️", className='eye-icon', title="AI is watching"),
        html.H1("Quantum Vision Control Center", style={'color': '#5e8299', 'fontSize': '42px', 'fontWeight': 'bold'}),
        html.P("AI-Driven Device Monitoring", style={'color': '#b3c6ff', 'fontSize': '20px'})
    ]),
    # Notification banner
    html.Div(className='notification-banner', children=[
        "Notification: Last critical issue was notified via SMS. Please approve the update for the Security Camera driver. "
        "Suggestion: Run a full system diagnostic and verify sensor connectivity."
    ]),
    # Manual control panel with extra buttons
    html.Div(className='manual-controls', children=[
        html.Button("Lock Devices", id="lock-all"),
        html.Button("Freeze Operations", id="freeze-all"),
        html.Button("Cancel Operation", id="cancel-operation"),
        html.Button("Record Screen (Start)", id="record-screen"),
        html.Button("Stop Recording", id="stop-record"),
        html.Button("Update Firmware", id="update-firmware"),
        html.Button("Restart Devices", id="restart-devices")
    ]),
    html.Div(className='device-grid', children=[
        html.Div(className='device-card', children=[
            html.H3(device, style={'color': '#5e8299'}),
            # Terminal with full details and diagnostics
            html.Div(id=f'device-terminal-{device}', className='terminal', children="Loading data...")
        ]) for device in list(devices.keys())
    ]),
    html.Div(className='graph-container', children=[
        html.Div(className='graph-card', children=[dcc.Graph(id='confidence-graph')]),
        html.Div(className='graph-card', children=[dcc.Graph(id='vision-status-graph')]),
        html.Div(className='graph-card', children=[dcc.Graph(id='error-rate-graph')]),
        html.Div(className='graph-card', children=[dcc.Graph(id='failure-probability-graph')])
    ]),
    html.Div(id='alerts', className='alert-box'),
    html.Div(id='popup-alert', className='popup', style={'display': 'none'}),
    dcc.Interval(id='interval-component', interval=2*1000, n_intervals=0)
])

# Callback for manual controls
@app.callback(
    Output('alerts', 'children'),
    [Input('lock-all', 'n_clicks'),
     Input('freeze-all', 'n_clicks'),
     Input('cancel-operation', 'n_clicks'),
     Input('record-screen', 'n_clicks'),
     Input('stop-record', 'n_clicks'),
     Input('update-firmware', 'n_clicks'),
     Input('restart-devices', 'n_clicks')]
)
def manual_controls_callback(lock_clicks, freeze_clicks, cancel_clicks, record_clicks, stop_clicks, firmware_clicks, restart_clicks):
    global recording_flag, recording_thread
    ctx = dash.callback_context
    if not ctx.triggered:
        return ""
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == "lock-all":
        return html.P("Manual Action: All devices locked for security.", style={'color': '#fff', 'fontWeight': 'bold'})
    elif button_id == "freeze-all":
        return html.P("Manual Action: Operations frozen for troubleshooting.", style={'color': '#fff', 'fontWeight': 'bold'})
    elif button_id == "cancel-operation":
        return html.P("Manual Action: Current operation canceled.", style={'color': '#fff', 'fontWeight': 'bold'})
    elif button_id == "record-screen":
        if not recording_flag:
            recording_flag = True
            recording_thread = threading.Thread(target=record_screen, daemon=True)
            recording_thread.start()
            return html.P("Manual Action: Screen recording started for up to 1 minute. Saved as 'screen_record.mp4'.", style={'color': '#fff', 'fontWeight': 'bold'})
        else:
            return html.P("Screen recording is already in progress.", style={'color': '#fff', 'fontWeight': 'bold'})
    elif button_id == "stop-record":
        if recording_flag:
            recording_flag = False
            return html.P("Manual Action: Screen recording stopped.", style={'color': '#fff', 'fontWeight': 'bold'})
        else:
            return html.P("No screen recording is currently active.", style={'color': '#fff', 'fontWeight': 'bold'})
    elif button_id == "update-firmware":
        return html.P("Manual Action: Firmware update initiated on selected devices.", style={'color': '#fff', 'fontWeight': 'bold'})
    elif button_id == "restart-devices":
        return html.P("Manual Action: All devices are restarting.", style={'color': '#fff', 'fontWeight': 'bold'})
    return ""

# Main update callback: updates graphs and composite terminal per device
@app.callback(
    [Output('confidence-graph', 'figure'),
     Output('vision-status-graph', 'figure'),
     Output('error-rate-graph', 'figure'),
     Output('failure-probability-graph', 'figure'),
     Output('popup-alert', 'children'),
     Output('popup-alert', 'style')] +
    [Output(f'device-terminal-{device}', 'children') for device in list(devices.keys())],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    global last_hourly_check, last_30min_check, notifications
    current_time = datetime.now()
    
    # Update device data with AI features and predictive analytics
    for device in devices:
        if random.random() < 0.25 and devices[device]['ai_shield']:
            devices[device]['status'] = random.choice(['Online', 'Offline'])
            devices[device]['vision_status'] = random.choice(['Active', 'Degraded']) if devices[device]['status'] == 'Online' else 'Offline'
            devices[device]['ai_confidence'] = random.uniform(0.7, 0.99) if devices[device]['vision_status'] == 'Active' else random.uniform(0.5, 0.7)
            devices[device]['threat_score'] = random.uniform(0.05, 0.8) if devices[device]['vision_status'] == 'Degraded' else random.uniform(0.05, 0.3)
            devices[device]['health_score'] = random.randint(70, 95) if devices[device]['vision_status'] == 'Active' else random.randint(50, 80)
            devices[device]['anomaly_detected'] = random.random() < 0.2 if devices[device]['threat_score'] > 0.5 else False
            devices[device]['maintenance_alert'] = "Schedule service" if devices[device]['health_score'] < 70 else None
            devices[device]['optimization_suggestion'] = random.choice(["Increase scan frequency", "Adjust AI threshold", None]) if random.random() < 0.3 else None
            if devices[device]['vision_status'] == 'Degraded':
                devices[device]['last_scan'] = 'Threat Detected'
        
        # Append logs
        devices[device]['scan_log'].append(generate_scan_log(device))
        devices[device]['error_log'].append(generate_error_log(device))
        devices[device]['ai_log'].append(generate_ai_log(device))
        devices[device]['scan_log'] = devices[device]['scan_log'][-5:]
        devices[device]['error_log'] = devices[device]['error_log'][-5:]
        devices[device]['ai_log'] = devices[device]['ai_log'][-5:]
        
        # Predictive analytics update
        if devices[device]['health_score'] < 80:
            devices[device]['failure_probability'] = random.uniform(0.5, 0.9)
            days_until = random.randint(1, 7)
            predicted_date = (current_time + timedelta(days=days_until)).strftime('%Y-%m-%d %H:%M')
            devices[device]['predicted_maintenance_date'] = predicted_date
        else:
            devices[device]['failure_probability'] = random.uniform(0.1, 0.5)
            devices[device]['predicted_maintenance_date'] = "N/A"
    
    # Build visualizations
    confidence_fig = go.Figure(data=[go.Bar(x=list(devices.keys()),
                                              y=[devices[d]['ai_confidence'] for d in devices.keys()],
                                              marker_color='#66d9ef')])
    confidence_fig.update_layout(title='AI Confidence Levels', plot_bgcolor='rgba(0,0,0,0)',
                                   paper_bgcolor='rgba(10,20,30,0.9)', font=dict(color='#e6f0fa'),
                                   height=300, margin=dict(l=40, r=40, t=40, b=40))
    
    vision_counts = {'Active': 0, 'Degraded': 0, 'Offline': 0}
    for d in devices.values():
        vision_counts[d['vision_status']] += 1
    vision_status_fig = go.Figure(data=[go.Pie(labels=list(vision_counts.keys()),
                                                values=list(vision_counts.values()),
                                                marker=dict(colors=['#66d9ef', '#ff6b6b', '#d9534f']))])
    vision_status_fig.update_layout(title='Vision Module Status', plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(10,20,30,0.9)', font=dict(color='#e6f0fa'), height=300)
    
    error_rates = [sum(1 for log in devices[d]['error_log'] if 'No issues' not in log) / 5 for d in devices.keys()]
    error_rate_fig = go.Figure(data=[go.Scatter(x=list(devices.keys()),
                                                 y=error_rates,
                                                 mode='lines+markers',
                                                 line=dict(color='#ff6b6b', width=3))])
    error_rate_fig.update_layout(title='Error Rate (Last 5 Scans)', plot_bgcolor='rgba(0,0,0,0)',
                                 paper_bgcolor='rgba(10,20,30,0.9)', font=dict(color='#e6f0fa'),
                                 height=300, margin=dict(l=40, r=40, t=40, b=40))
    
    failure_fig = go.Figure(data=[go.Bar(x=list(devices.keys()),
                                          y=[devices[d]['failure_probability'] for d in devices.keys()],
                                          marker_color='#ff6b6b')])
    failure_fig.update_layout(title='Device Failure Probability', plot_bgcolor='rgba(0,0,0,0)',
                              paper_bgcolor='rgba(10,20,30,0.9)', font=dict(color='#e6f0fa'),
                              height=300, margin=dict(l=40, r=40, t=40, b=40))
    
    # Popup notifications for critical alerts and admin approvals
    popup_content = []
    popup_style = {'display': 'none'}
    if (current_time - last_hourly_check).total_seconds() >= 3600:
        last_hourly_check = current_time
        dev = random.choice(list(devices.keys()))
        if "Critical" in devices[dev]['error_log'][-1] or devices[dev]['status'] == 'Offline' or devices[dev]['anomaly_detected']:
            msg = f"Critical issue on {dev}: {devices[dev]['error_log'][-1]}"
            notifications.append({
                "time": current_time.strftime('%H:%M:%S'),
                "message": f"Slack: {msg}\nEmail: vision@quantum.io\nSMS: +1-555-987-6543"
            })
            popup_content = [
                html.H3("Critical Alert", style={'color': '#5e8299'}),
                html.P(f"Slack: {msg}", style={'color': '#e6f0fa'}),
                html.P("Email: Sent to vision@quantum.io", style={'color': '#e6f0fa'}),
                html.P("SMS: Sent to +1-555-987-6543", style={'color': '#e6f0fa'})
            ]
            popup_style = {'display': 'block'}
    
    if (current_time - last_30min_check).total_seconds() >= 1800:
        last_30min_check = current_time
        dev = "Security Camera"
        approval_msg = f"Admin approval required for update of {dev} driver."
        notifications.append({
            "time": current_time.strftime('%H:%M:%S'),
            "message": approval_msg
        })
        popup_content = [
            html.H3("Update Approval Request", style={'color': '#5e8299'}),
            html.P(approval_msg, style={'color': '#e6f0fa'})
        ]
        popup_style = {'display': 'block'}
    
    # Generate composite terminal outputs with rich details for each device
    terminal_outputs = []
    for device, data in devices.items():
        terminal_outputs.append(format_device_info(device, data))
    
    return ([confidence_fig, vision_status_fig, error_rate_fig, failure_fig, popup_content, popup_style] +
            terminal_outputs)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
