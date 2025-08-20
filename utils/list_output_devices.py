import sounddevice as sd

def list_output_devices():
    print("Available output devices:")
    for idx, dev in enumerate(sd.query_devices()):
        if dev['max_output_channels'] > 0:
            print(f"  [{idx}] {dev['name']} (channels: {dev['max_output_channels']})")

if __name__ == "__main__":
    list_output_devices()
