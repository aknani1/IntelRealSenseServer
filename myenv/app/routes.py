from flask import render_template, current_app,request,jsonify
from app import socketio
from .camera import generate_frames
from .camera import stop_generating_frames
import pyrealsense2 as rs
from .camera import streaming
from .camera import framerate
from .camera import exposure_value
from .camera import change_exposure
from .camera import toggle_metadata


pipeline = rs.pipeline()
config = rs.config()

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')
    @app.route('/api/configure', methods=['POST'])
    def configure():
        try:
            # Parse the JSON payload from the client
            data = request.json
            module = data.get('module')
            resolution = data.get('resolution') 
            frame_rate = int(data.get('frame_rate'))
            stop_generating_frames()
            print(data)
            # Validate the input
            if not module or not resolution or not frame_rate:
                return jsonify({"error": "Invalid input"}), 400
    
            # Parse resolution into width and height
            width, height = map(int, resolution.split('x'))
    
            # Configure the RealSense pipeline based on the module
            if module == 'depth':
                rs.pipeline.stop()  # Stop the current pipeline
                config.enable_stream(rs.stream.depth, 640, 360, rs.format.z16, frame_rate)  # Apply new configuration
                pipeline.start(config)  # Restart the pipeline with updated config

                print(f"Depth Module updated to {resolution} at {frame_rate} FPS")
            elif module == 'rgb': 
                streaming["status"] = True
                framerate["status"] = frame_rate
                print(f"RGB Module updateddddddddd to {resolution} at {frame_rate} FPS")
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

    @app.route('/api/toggle_metadata', methods=['POST'])
    def toggle_metadata_endpoint():
        data = request.json
        module = data.get('module')
        if module not in ['rgb', 'depth']:
            return jsonify({"error": "Invalid module"}), 400
        
        toggle_metadata(module)
        return jsonify({"message": f"{module.capitalize()} metadata toggled", "status": metadata_toggles[module]})

    @app.route('/api/exposure', methods=['POST'])
    def update_exposure():
        try:
            # Parse the JSON payload from the client
            data = request.json
            module = data.get('module')
            req_exposure_value = int(data.get('exposure'))  # Exposure value (e.g., 8500)
            
            print(data)
            # Validate input
            if not module or exposure_value is None:
                return jsonify({"error": "Invalid input"}), 400
    
            if module == 'depth':
                # Ensure depth sensor exists
                if len(sensors) < 1:
                    return jsonify({"error": "Depth sensor not found"}), 500
    
                depth_sensor = sensors[0]  # Assuming depth is the first sensor
                if rs.option.exposure in depth_sensor.get_supported_options():
                    depth_sensor.set_option(rs.option.exposure, exposure_value)
                    print(f"Depth Module exposure updated to {exposure_value}")
                else:
                    return jsonify({"error": "Exposure option not supported for Depth Module"}), 400
    
            elif module == 'rgb':
                # Ensure RGB sensor exists
                exposure_value["status"] = req_exposure_value
                change_exposure()
    
            else:
                return jsonify({"error": "Invalid module"}), 400
    
            return jsonify({
                "message": f"{module.capitalize()} Module exposure updated",
                "exposure": exposure_value
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