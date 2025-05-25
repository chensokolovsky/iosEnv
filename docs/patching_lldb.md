
# Introduction
LLDB, the chosen debugger, comes ready in the docker.  
However, lldb does not recognize the "SDK folder" which is the iOS library which is stored usually on the hosting Mac.  
To fix this, unfourtunatelly, there is no env variable or settings to point to other folders.  
The solution is then to patch lldb and force it to find the needed SDK path on the host


# Applying the Patch
In our [init script](../docker/env/init) the following line replaces the one of the lldb's SO files with the patched one
```
mv /env/liblldb-14.so.1_patched /usr/lib/aarch64-linux-gnu/liblldb-14.so.1
```


# How the issue came up?

When debugging an iOS device with lldb, the first step is:
```
(lldb) platform select remote-ios
```
When doing so on a mac, the output of lldb (which is similar to the output of the command *platform status*) is the following:
```
(lldb) platform select remote-ios
 Platform: remote-ios
 Connected: no
 SDK Path: "/Users/chenshalev/Library/Developer/Xcode/iOS DeviceSupport/14.5.1 (18E212)"
 SDK Roots: [ 0] "/Users/chenshalev/Library/Developer/Xcode/iOS DeviceSupport/iPhone10,3 14.5.1 (18E212)"
 SDK Roots: [ 1] "/Users/chenshalev/Library/Developer/Xcode/iOS DeviceSupport/14.5.1 (18E212)"
 ```
However, running the command on the container:

```
SDK Path: error: unable to locate SDK
```
which then shows a warning:
```
warning: libobjc.A.dylib is being read from process memory. This indicates that LLDB could not find the on-disk shared cache for this device. This will likely reduce debugging performance.
```
The *libobjc.A.dylib* is located in the SDK Path above.  
However, simply using the -v option in the docker run and exposing this folder is not enough...  
The lldb client can't find the SDK  
Environment variables are not available for this, nor debugging settings  

So, the option is to patch lldb and direct it to a selected folder of our choice, which we can link via the host  



# Researching

To help research this I used:
* source code from llvm and swift lang
* log messages of lldb which can be turned on by categories (lldb) log enable lldb <category>
* strings util to find the source file
* Opening the library with Ghidra and comparing to the source code
* debugging lldb with lldb


### sources:
[swiftlang llvm on github](https://github.com/swiftlang/llvm-project/blob/44036755b0464524cf1815783854ef939173e6d1/lldb/source/Plugins/Platform/MacOSX/PlatformDarwinDevice.cpp#L229)
[apple llvm on github](https://github.com/search?q=repo%3Aapple%2Fswift-lldb+UpdateSDKDirectoryInfosIfNeeded&type=code)
[llvm's llvm on github](https://github.com/llvm/llvm-project/blob/1c154a20b4943e9c94bcff8ee5bba34fdf9e52e5/lldb/source/Utility/XcodeSDK.cpp#L330)

### log messages
to be the most verbose you can use
```
(lldb) log enable lldb all
```
To be specific and not experience the spamming messages for each action, use these
```
(lldb) log enable lldb target
(lldb) log enable lldb process
(lldb) log enable lldb platform
```
full list is here
```
(lldb) log list
```


### strings
To find which files we need to work with for the patch, just looked for the strings in the logs
```
grep -r "SDK Path" .
```
this can be run in lldb and its relevant llvm folders  
Found the file *liblldb-14.so.1*


### ghidra
looking for string to find the functions and reading ARM instructions
This helps to debug lldb and find what to patch   
This can be done by copying the library from the docker to the host which runs ghidra
```
docker cp <image id>:/path/to/file /destination/path/on/host
```

### debugging lldb with lldb
Starting the container and running lldb   
Then, connect to the container to find lldb's pid
```
$ docker exec -it <image id> /bin/bash
# ps -A | grep lldb
```
Connect to lldb
```
# lldb --attach-pid <pid>
```

Now we can break as pleased according to ghidra locations:
Find the base address
```
(lldb) sh image list | grep lldb
```


# Debugging Results:

Patching with lldb

1) Run the container

2) enter the container using the image id
```
docker ecev -it <image id> /bin/bash
```
3)
```
ps -A | grep lldb
```
4)
```
lldb --attach-pid=<pid>
```

5)
```
command script import /env/scripts/lldbsh.py
```

6)
```
sh image list | grep lldb
```

7)
```
script hex(<base address> + 0x0827f44)
```

8)
```
script hex(<base address> + 0x00828018)
```

9)
```
break set -a <result of 7>
break set -a <result of 8>
```

10)
in lldb of docker:
```
platform select remote-ios
```

11)
on first breakpoint:
```
mem read $x0
c
```

12)
on second breakpoint (ret)
```
mem wr x0 <value of x0>
```

13)
```
continue
detatch
q
```



# Patching


The value reaches x1 at line 0x827f28
```
ffff8e1c7f28 cc 30 e6 97     bl         <EXTERNAL>::llvm::Twine::str[abi:cxx11]          undefined str[abi:cxx11](void)
```

The return value is in both x0 and x1

so, we can just skip to the epilog
ie, jump (using b) from 0x827f2c to 0x828004

x0 will be the return value of this function, pointing to the needed path

The patch:
```
        00827f28 cc 30 e6 97     bl     <EXTERNAL>::llvm::Twine::str[abi:cxx11]          undefined str[abi:cxx11](void)
        00827f2c 36 00 00 14     b      LAB_00828004    <---- This is the patch  <-----
        00827f30 74 a2 0b 91     add    x20,x19,#0x2e8
```

After the patch, we can replace the library, which sits here:
```
% docker cp liblldb-14.so.1_patched 6d282177ee07:/usr/lib/aarch64-linux-gnu/liblldb-14.so.1
```

The patch make [this](https://github.com/llvm/llvm-project/blob/d02a704ec952f01ab258e8c4cbb3c01c8f768e15/lldb/source/Plugins/Platform/MacOSX/PlatformDarwinDevice.cpp#L229) function return the platform dir in x0 to the caller to GetDeviceSupportDirectory. This is probably because HostInfo:: is not set as Apple host since it was not compiled for apple dist to work on linux

