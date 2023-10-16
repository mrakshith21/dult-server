import dbus
import command_result

import threading
import multiprocessing
from playsound import playsound

from advertisement import Advertisement
from service import Application, Service, Characteristic, Descriptor

GATT_CHRC_IFACE = "org.bluez.GattCharacteristic1"

# Sound player process and a mutex lock for the same
mutex = threading.Lock()
sound_player = multiprocessing.Process(target=playsound, args=("sound.wav",))

def encode(str):
    data = [dbus.Byte(c.encode()) for c in str]
    return data

class NonOwnerAdvertisement(Advertisement):
    def __init__(self, index):
        Advertisement.__init__(self, index, "peripheral")
        self.add_local_name("Rakshith GATT Server")
        self.include_tx_power = True

class NonOwnerService(Service):
    NON_OWNER_SERVICE_UUID = "00000090-710e-4a5b-8d75-3e5b444bc3cf"

    def __init__(self, index):

        Service.__init__(self, index, self.NON_OWNER_SERVICE_UUID, True)
        self.add_characteristic(ProductData(self))
        self.add_characteristic(ManufacturerName(self))
        self.add_characteristic(ModelName(self))
        self.add_characteristic(AccessoryCapabilities(self))
        self.add_characteristic(AccessoryCategory(self))
        self.add_characteristic(SoundStart(self))
        self.add_characteristic(SoundStop(self))

class ProductData(Characteristic):
    PRODUCT_DATA_CHARACTERISTIC_UUID = "00000306-0000-1000-8000-00805F9B34FB"

    def __init__(self, service):
        self.notifying = False
        self.product_data = "0xdfeceff1e1ff54db"

        Characteristic.__init__(
                self, self.PRODUCT_DATA_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(ProductDataDescriptor(self))

    def Get_Product_Data(self, options):
        print("Get Product Data Request")
        return self.WriteValue(options)

    def Get_Product_Data_Response(self, options):
        print("Server responding to Product Data Request")
        return self.IndicateValue(options)

    def WriteValue(self, options):
        print("Write request over Product Data")
        return self.Get_Product_Data_Response(options)
    
    def IndicateValue(self, options):
        print("Indication response to request for Product Data")
        return encode(self.product_data)

class ProductDataDescriptor(Descriptor):
    PRODUCT_DATA_DESCRIPTOR_UUID = "2901"
    PRODUCT_DATA_DESCRIPTOR_VALUE = "Product Data"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.PRODUCT_DATA_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        return encode(self.PRODUCT_DATA_DESCRIPTOR_VALUE)

class ManufacturerName(Characteristic):
    MANUFACTURER_NAME_CHARACTERISTIC_UUID = "00000307-0000-1000-8000-00805F9B34FB"

    def __init__(self, service):
        self.notifying = False
        self.manufacturer_name = "Tile"

        Characteristic.__init__(
                self, self.MANUFACTURER_NAME_CHARACTERISTIC_UUID,
                ["read"], service)
        self.add_descriptor(ManufacturerNameDescriptor(self))

    def ReadValue(self, options):
        print("Get Manufacturer Name Request")
        return encode(self.manufacturer_name)

class ManufacturerNameDescriptor(Descriptor):
    MANUFACTURER_NAME_DESCRIPTOR_UUID = "2902"
    MANUFACTURER_NAME_DESCRIPTOR_VALUE = "Manufacturer Name"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.MANUFACTURER_NAME_DESCRIPTOR_UUID,
                ["read"],
                characteristic)

    def ReadValue(self, options):
        return encode(self.MANUFACTURER_NAME_DESCRIPTOR_VALUE)


class ModelName(Characteristic):
    MODEL_NAME_CHARACTERISTIC_UUID = "00000308-0000-1000-8000-00805F9B34FB"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.MODEL_NAME_CHARACTERISTIC_UUID,
                ['read'],
                service)
        self.notifying = False
        self.model_name = "Tile Slim 2020"

        self.add_descriptor(ModelNameDescriptor(self))

    def ReadValue(self, options):
        print("Get Model Name Request")
        return encode(self.model_name)

class ModelNameDescriptor(Descriptor):
    MODEL_NAME_DESCRIPTOR_UUID = "2901"
    MODEL_NAME_DESCRIPTOR_VALUE = "Model Name"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.MODEL_NAME_DESCRIPTOR_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return encode(self.MODEL_NAME_DESCRIPTOR_VALUE)
    
class AccessoryCategory(Characteristic):
    ACCESSORY_CATEGORY_CHARACTERISTIC_UUID = "00000309-0000-1000-8000-00805F9B34FB"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.ACCESSORY_CATEGORY_CHARACTERISTIC_UUID,
                ['read'],
                service)
        self.notifying = False
        self.accessory_category = "1"
        self.add_descriptor(AccessoryCategoryDescriptor(self))

    def ReadValue(self, options):
        print("Get Accessory Category Request")
        return encode(self.accessory_category)

class AccessoryCategoryDescriptor(Descriptor):
    ACCESSORY_CATEGORY_DESCRIPTOR_UUID = "2901"
    ACCESSORY_CATEGORY_DESCRIPTOR_VALUE = "Accessory Category"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.ACCESSORY_CATEGORY_DESCRIPTOR_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return encode(self.ACCESSORY_CATEGORY_DESCRIPTOR_VALUE)

class AccessoryCapabilities(Characteristic):
    ACCESSORY_CAPABILITIES_CHARACTERISTIC_UUID = "0000030A-0000-1000-8000-00805F9B34FB"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.ACCESSORY_CAPABILITIES_CHARACTERISTIC_UUID,
                ['read'],
                service)
        self.notifying = False
        self.accessory_capabilities = "11"
        self.add_descriptor(AccessoryCapabilitiesDescriptor(self))

    def ReadValue(self, options):
        print("Get Accessory Capabilities Request")
        return encode(self.accessory_capabilities)

class AccessoryCapabilitiesDescriptor(Descriptor):
    ACCESSORY_CAPABILITIES_DESCRIPTOR_UUID = "2901"
    ACCESSORY_CAPABILITIES_DESCRIPTOR_VALUE = "Accessory Capabilities"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.ACCESSORY_CAPABILITIES_DESCRIPTOR_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return encode(self.ACCESSORY_CAPABILITIES_DESCRIPTOR_VALUE)

class SoundStart(Characteristic):
    OPCODE = '0300'
    SOUND_START_CHARACTERISTIC_UUID = "00000300-0000-1000-8000-00805F9B34FB"

    def __init__(self, service):
        Characteristic.__init__(
                self, self.SOUND_START_CHARACTERISTIC_UUID,
                ['write'],
                service)
        self.notifying = False
        self.add_descriptor(SoundStartDescriptor(self))

    def start_sound(self):
        global mutex, sound_player
        mutex.acquire()
        if not sound_player.is_alive():
            try:
                sound_player = multiprocessing.Process(target=playsound, args=("sound.wav",))
                print("Playing sound...")
                sound_player.start()
            except:
                print("Error while playing sound")
                mutex.release()
                return False
            mutex.release()
            return True
        mutex.release()
        return False

    def WriteValue(self, value, options):
        print("Sound Start request")
        response = self.start_sound()
        if not response:
            print("Error while starting sound, might be already playing")        
            return command_result.get_command_result(self.OPCODE, command_result.INVALID_STATE)
        print("Sound start successful")
        return command_result.get_command_result(self.OPCODE, command_result.SUCCESS)

class SoundStartDescriptor(Descriptor):
    SOUND_START_DESCRIPTOR_UUID = "2901"
    SOUND_START_DESCRIPTOR_VALUE = "Sound Start Command"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.SOUND_START_DESCRIPTOR_UUID,
                ['read'],
                characteristic)                

    def ReadValue(self, options):
        return encode(self.SOUND_START_DESCRIPTOR_VALUE)


class SoundStop(Characteristic):
    SOUND_STOP_CHARACTERISTIC_UUID = "00000301-0000-1000-8000-00805F9B34FB"
    OPCODE = '0301'

    def __init__(self, service):
        Characteristic.__init__(
                self, self.SOUND_STOP_CHARACTERISTIC_UUID,
                ['write'],
                service)
        self.notifying = False
        self.add_descriptor(SoundStopDescriptor(self))

    def stop_sound(self):
        global mutex, sound_player
        mutex.acquire()
        if sound_player.is_alive():        
            try:
                sound_player.terminate()
            except Exception:
                return False
            mutex.release()
            return True
        mutex.release()
        return False

    def WriteValue(self, value, options):
        print("Sound Stop Request")
        response = self.stop_sound()
        if not response:
            print("Error while stopping sound, might be already stopped")
            return command_result.get_command_result(self.OPCODE, command_result.INVALID_STATE)
        print("Sound stop successful")
        return command_result.get_command_result(self.OPCODE, command_result.SUCCESS)

class SoundStopDescriptor(Descriptor):
    SOUND_STOP_DESCRIPTOR_UUID = "2901"
    SOUND_STOP_DESCRIPTOR_VALUE = "Sound Start Command"

    def __init__(self, characteristic):
        Descriptor.__init__(
                self, self.SOUND_STOP_DESCRIPTOR_UUID,
                ['read'],
                characteristic)

    def ReadValue(self, options):
        return encode(self.SOUND_STOP_DESCRIPTOR_VALUE)

# Set up the application with the non owner service
app = Application()
app.add_service(NonOwnerService(0))
app.register()

# Register advertisement
adv = NonOwnerAdvertisement(0)
adv.register()

try:
    app.run()
except KeyboardInterrupt:
    app.quit()
    adv.Release()
