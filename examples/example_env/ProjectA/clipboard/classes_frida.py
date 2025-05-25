print("Starting the python script that will run frida-python")
"""
Usage: python3 script_name.py program_name host:port
Example: python3 class_enumeration_frida.py Weather host.docker.internal:4001
"""


import frida
import sys


if len(sys.argv) != 3:
    print("Usage: python3 script_name.py program_name host:port")
    sys.exit(-1)

print(f"The first argument is {sys.argv[1]}")
print(f"The second argument is {sys.argv[2]}")

# Frida JS script
js_code = """
rpc.exports = {
    ping: function() {
        send("Ping from Frida script");
        return "Pong";
    },

    getAllObjcClasses: function() {
        let result = Object.keys(ObjC.classes)
        return result
    },

    getMethodsForClass: function(className) {
        let clazz = ObjC.classes[className]
        let methods = clazz.$ownMethods
        return methods
    }


};
"""

# Python script
def on_message(message, data):
    print(f"Message from JS: {message['payload']}")

device = frida.get_device_manager().add_remote_device(sys.argv[2])
session = device.attach(sys.argv[1])
script = session.create_script(js_code)
script.on("message", on_message)
script.load()
print(script.exports_sync.ping())
all_classes = script.exports_sync.get_all_objc_classes()
print(f"got {len(all_classes)} classes")


with open('/projects/location/all_objc_interfaces.txt', 'a') as f:

    for class_name in all_classes:
        methods = script.exports_sync.get_methods_for_class(class_name)
        #print(f"got {len(methods)} for class {class_name}")
        f.write("++++++++++++++\n")
        f.write(f"{class_name}")
        f.write("\n-------------\n")
        for method in methods:
            f.write(f"{method}\n")
        f.write("\n")

input("Press Enter to exit...\n")  # Keep the script running




