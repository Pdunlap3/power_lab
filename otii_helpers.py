import time

from otii_tcp_client import otii_client

#MEASURMENT_DURATION = 5.0


def wait_for_uart(otii: otii_client.Connect) -> None:
    """Placeholder for UART wait logic."""
    # this is a basic connect to the otii and check if it succesfully connected.
    devices = otii.get_devices()
    if len(devices) ==0:
        raise RuntimeError('No devices is connected')
    device = devices[0]

    # Setting up power settings for the otii
    device.set_main_voltage(12)
    device.set_exp_voltage(3.3)

    # Setting up the Channels that will be in use.
    device.set_uart_baudrate(115200)  # Will change depending on camera model
    device.enable_channel('mc', True)
    device.enable_channel('mp', True)
    device.enable_channel('rx', True)


    # starting a new project
    project = otii.create_project()

    # Turning on power WATCH OUT!
    device.set_main(True)

    '''Setting up the Serial Reading section'''
    #intializing our time variables
    IDLE_TIMEOUT = 5.0    # seconds of UART silence before stopping
    MAX_DURATION = 60.0   # hard cap no matter what

    recording = project.get_last_recording()
    assert recording is not None

    seen = 0
    start = time.time()
    last_rx = start       # counts as "activity" so the DUT has time to boot
    
    while True:
            now = time.time()
            if now - last_rx > IDLE_TIMEOUT:
                print(f"No UART data for {IDLE_TIMEOUT}s, stopping.")
                break
            if now - start > MAX_DURATION:
                print("Max duration reached, stopping.")
                break
    
            count = recording.get_channel_data_count(device.id, "rx")
            if count > seen:
                data = recording.get_channel_data(device.id, "rx", seen, count - seen)
                seen = count
                last_rx = now                  # reset the idle timer
                for line in data["values"]:
                    print(f'{line["timestamp"]:.3f}s  {line["value"]}')
                    if "BL" in line["value"]:
                        device.write_tx("START_TEST\r\n")
    
            time.sleep(0.1)                    # poll interval, inside the loop
    
        # Turn off the main output of the selected device
    device.set_main(False)
    
    print("it works")
    
    # Stop the recording
    project.stop_recording()



 
 
def main()-> None:
    client = otii_client.OtiiClient()
    with client.connect() as otii:
        wait_for_uart(otii)
if __name__ == '__main__':
    main()