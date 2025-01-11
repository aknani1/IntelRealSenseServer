from flask import render_template, current_app,request,jsonify
from app import socketio
from .camera import generate_frames
import pyrealsense2 as rs

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')
    @app.route('/api/configure', methods=['POST'])
    def configure():
        try:
            # Parse the JSON payload from the client
            data = request.json
            module = data.get('module')  # 'depth' or 'rgb'
            resolution = data.get('resolution')  # e.g., '640x480'
            frame_rate = int(data.get('frame_rate'))  # e.g., 30
            print(data)
            # Validate the input
            if not module or not resolution or not frame_rate:
                return jsonify({"error": "Invalid input"}), 400
    
            # Parse resolution into width and height
            width, height = map(int, resolution.split('x'))
    
            # Configure the RealSense pipeline based on the module
            if module == 'depth':
                config.enable_stream(rs.stream.depth, width, height, rs.format.z16, frame_rate)
                print(f"Depth Module updated to {resolution} at {frame_rate} FPS")
            elif module == 'rgb':
                config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, frame_rate)
                print(f"RGB Module updated to {resolution} at {frame_rate} FPS")
            else:
                return jsonify({"error": "Invalid module"}), 400
    
    
            return jsonify({
                "message": f"{module.capitalize()} Module updated",
                "resolution": resolution,
                "frame_rate": frame_rate
            }), 200
    
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500
        
    @socketio.on('connect')
    def handle_connect():
        
        print('Client connected')

    @socketio.on('start_stream')
    def start_stream():
        for frame in generate_frames():
            socketio.emit('video_frame', frame)

pipeline = rs.pipeline()
config = rs.config()



@socketio.on('update_configuration')
def update_configuration(data):
    module = data['module']   # 'depth' or 'rgb'
    resolution = data['resolution']   # e.g., '640x480'
    frame_rate = int(data['frameRate'])   # e.g., '30'

    width, height = map(int, resolution.split('x'))

    if module == 'depth':
        config.enable_stream(rs.stream.depth, width, height, rs.format.z16, frame_rate)
        print(f"Depth Module updated to {resolution} at {frame_rate} FPS")
    elif module == 'rgb':
        config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, frame_rate)
        print(f"RGB Module updated to {resolution} at {frame_rate} FPS")

# Call this function in __init__.py after creating the app
# init_routes(current_app)