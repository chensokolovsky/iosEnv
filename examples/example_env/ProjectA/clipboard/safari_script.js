// frida_demo.js

setTimeout(function() {
    const baseAddr = Module.findBaseAddress("MobileSafari");
    console.log("Base Address: " + baseAddr);
}, 100);
