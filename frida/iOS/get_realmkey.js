Interceptor.attach(ObjC.classes.RLMRealmConfiguration['- setEncryptionKey:'].implementation, {
    onEnter: function(args){
        console.log("Called!")
        console.log(args[2])
        var key = new ObjC.Object(ptr(args[2]))

        console.log("Key: ")
        console.log(hexdump(ptr(key.bytes()), {
            length: 64,
            header: true,
            ansi: true
        }))
        

     
        
  
        
    }, 
    onLeave: function(args){
        var key = args[2]
       

    }
});

