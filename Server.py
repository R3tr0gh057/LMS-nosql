from flask import Flask, render_template, jsonify, request
import serial
import threading
import time
import pyautogui
import serial.tools.list_ports

app = Flask(__name__)
ser = None

read_command = "-"
stop_read_command = "_"
write_command = ";"
stop_write_command = ":"

# Global variables to store the last read UID and data
last_read_data = ""
last_read_uid = ""

# Global variable for the library version
id_serial_port = None
book_serial_port = None
id_thread = None
book_thread = None
stop_threads = False

id_data = ""
book_data = ""



# Global variables to store keystroke status
keystrokeStatus = False

# Serial write function to send commands to the serial port
def serial_write(command):
    if ser:
        ser.write(command.encode())
        print(f"Command sent to serial: {command}")

# Function to read data from the serial port
def read_from_serial():
    global last_read_data, last_read_uid

    if ser is None:
        print("Serial port not available.")
        return
    
    flag = {
        "ets Jul 29 2019 12:21:46", "rst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)", 
        "configsip: 0, SPIWP:0xee", "clk_drv:0x00,q_drv:0x00,d_drv:0x00,cs0_drv:0x00,hd_drv:0x00,wp_drv:0x00", 
        "mode:DIO, clock div:1", "load:0x3fff0030,len:1184", "load:0x40078000,len:13260", 
        "load:0x40080400,len:3028", "entry 0x400805e4"
    }
    
    while True:
        if ser.in_waiting > 0:
            try:
                # Clear last read data before reading new data
                # last_read_data = ""
                # Read Data
                Data = ser.readline().strip().decode('utf-8')
                if any(flag_str in Data for flag_str in flag):
                    continue
                elif Data == "MIFARE_Read() failed: The CRC_A does not match.":
                    continue
                else:
                    last_read_data = Data
                    print(f"Read Data: {last_read_data}")

            except UnicodeDecodeError:
                print("Failed to decode RFID tag")

# Function to write data as keystrokes
def keystroke_function():
    global keystrokeStatus
    while keystrokeStatus:
        try:
            if ser.in_waiting > 0:
                time.sleep(0.5)
                pyautogui.typewrite(last_read_data)
                pyautogui.press('enter')
                print(f"Typed data: {last_read_data}")
                # Clearing last read data to avoid merged data
                # last_read_data = ""
        except Exception as e:
            print(f"Exception occurred: {e}")

# Function to keep the serial connection alive
def maintain_serial_connection():
    global ser
    while True:
        if ser is not None:
            try:
                if not ser.is_open:
                    ser.open()
            except serial.SerialException as e:
                print(f"Failed to maintain serial connection: {e}")
        time.sleep(1)

# Start a background thread to read RFID data if the serial port is available
if ser is not None:
    thread = threading.Thread(target=read_from_serial)
    thread.daemon = True
    thread.start()

###################
# Library functions
###################

# Function to handle reading data from the ID card serial port
def read_id_data():
    global stop_threads, id_serial_port, id_data
    while not stop_threads:
        try:
            if id_serial_port and id_serial_port.is_open:
                data = id_serial_port.readline().decode('utf-8').strip()
                print("ID Data read:", data)
                id_data = data  # Update the latest ID card data
        except serial.SerialException as e:
            print("Error reading from ID serial port:", e)
            break

# Function to handle reading data from the Book Reader serial port
def read_book_data():
    global stop_threads, book_serial_port, book_data
    while not stop_threads:
        try:
            if book_serial_port and book_serial_port.is_open:
                data = book_serial_port.readline().decode('utf-8').strip()
                print("Book Data read:", data)
                book_data = data  # Update the latest Book Reader data
        except serial.SerialException as e:
            print("Error reading from Book serial port:", e)
            break



# Main page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ports', methods=['GET'])
def list_ports():
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return jsonify(ports=ports)

@app.route('/connect', methods=['POST'])
def connect():
    global ser
    data = request.get_json()
    port = data.get('port')

    if ser:
        ser.close()

    try:
        print(f"Port started at {port}")
        ser = serial.Serial(port, 9600, timeout=1)
        threading.Thread(target=read_from_serial, daemon=True).start()
        return jsonify(success=True)
    except serial.SerialException as e:
        return jsonify(success=False, error=str(e))

@app.route('/startRead', methods=['POST'])
def startRead():
    try:
        serial_write(read_command)
        return jsonify({'status': 'read started'})
    except Exception as e:
        print(f"Exception occurred while starting read: {e}")
        return jsonify({'status': 'failed', 'error': str(e)}), 500

@app.route('/stopRead', methods=['POST'])
def stopRead():
    global keystrokeStatus
    try:
        serial_write(stop_read_command)
        keystrokeStatus = False
        return jsonify({'status': 'read stopped'})
    except Exception as e:
        print(f"Exception occurred while stopping read: {e}")
        return jsonify({'status': 'failed', 'error': str(e)}), 500

@app.route('/startWrite', methods=['POST'])
def startWrite():
    try:
        serial_write(write_command)
        return jsonify({'status': 'write started'})
    except Exception as e:
        print(f"Exception occurred while starting write: {e}")
        return jsonify({'status': 'failed', 'error': str(e)}), 500

@app.route('/stopWrite', methods=['POST'])
def stopWrite():
    try:
        serial_write(stop_write_command)
        return jsonify({'status': 'write stopped'})
    except Exception as e:
        print(f"Exception occurred while stopping write: {e}")
        return jsonify({'status': 'failed', 'error': str(e)}), 500

# Endpoint to send data to be written to the EEPROM
@app.route('/newWrite/<data>', methods=['POST'])
def newWrite(data):
    if data:
        serial_write(data + "\n")
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failed', 'error': 'No data provided'}), 400

# Endpoint to get the last read data
@app.route('/getReadData')
def getReadData():
    # return jsonify({'uid': last_read_uid, 'data': last_read_data})
    return jsonify({'data': last_read_data})

# Endpoint to start keystroke function
@app.route('/keystrokeMode/<int:data>', methods=['POST'])
def keystrokeMode(data):
    global keystrokeStatus

    keystrokeStatus = bool(data)
    print(f"Keystroke function {'started' if keystrokeStatus else 'stopped'}, status: {keystrokeStatus}")
    
    if keystrokeStatus:
        threading.Thread(target=keystroke_function).start()
    return jsonify({'status': 'received'})

##############
# LIBRARY
##############

@app.route('/library')
def index():
    return render_template('library.html')

@app.route('/libraryPortConnect', methods=['POST'])
def connect_ports():
    global id_serial_port, book_serial_port, id_thread, book_thread
    data = request.json

    id_port_name = data.get('IdPport')
    book_port_name = data.get('BookPort')

    try:
        # Establish connections to both serial ports
        id_serial_port = serial.Serial(id_port_name, baudrate=9600, timeout=1)
        book_serial_port = serial.Serial(book_port_name, baudrate=115200, timeout=1)

        # Start threads to handle data reading
        stop_threads = False

        id_thread = threading.Thread(target=read_id_data)
        book_thread = threading.Thread(target=read_book_data)

        id_thread.start()
        book_thread.start()

        return jsonify({'success': True})
    except serial.SerialException as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.route('/startLibraryKeystroke/<int:state>', methods=['POST'])
def start_keystroke(state):
    global stop_threads

    if state == 1:  # Start keystroke
        stop_threads = False
        return jsonify({'status': 'Keystroke threads running'})
    elif state == 0:  # Stop keystroke
        stop_threads = True
        if id_thread is not None:
            id_thread.join()
        if book_thread is not None:
            book_thread.join()
        return jsonify({'status': 'Keystroke threads stopped'})
    else:
        return jsonify({'status': 'Invalid state'})
    
def break_connection():
    global id_serial_port, book_serial_port, stop_threads

    stop_threads = True
    if id_serial_port and id_serial_port.is_open:
        id_serial_port.close()
    if book_serial_port and book_serial_port.is_open:
        book_serial_port.close()

    return jsonify({'status': 'Connections terminated'})

@app.route('/LibraryGetReadData', methods=['GET'])
def get_read_data():
    # Return the latest data from both Arduinos
    return jsonify({
        'id_data': id_data,
        'book_data': book_data
    })

if __name__ == '__main__':
    app.run()
