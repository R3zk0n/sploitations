
#include <stdio.h>
#include <stdlib.h>
#include <xpc/xpc.h>
#include <stdio.h>
#include <stdlib.h>
#include <xpc/xpc.h>
#include <CoreFoundation/CoreFoundation.h>

/// Small XPC fuzzer..
//I wrote this because i want to test various XPC commands trivally while doing RE on mach services..
// Code is subjectable to segfaults, trap, int3 and random trap’s, its not stable.. <(0.0<)
// Greets to Pepper, Wireghoul, Jefahaha, and everyone else.. <3 - S

#define    BOOTSTRAP_MAX_NAME_LEN            128
#define    BOOTSTRAP_MAX_CMD_LEN            512
typedef char name_t[BOOTSTRAP_MAX_NAME_LEN];
extern mach_port_t bootstrap_port;
kern_return_t bootstrap_look_up(
        mach_port_t bp,
        const name_t service_name,
        mach_port_t *sp);
kern_return_t bootstrap_check_in(
        mach_port_t bp,
        const name_t service_name,
        mach_port_t *sp);


static void
connection_handler(xpc_connection_t peer)
{
    xpc_connection_set_event_handler(peer, ^(xpc_object_t event) {
        printf(“Message received: %p\n”, event);
    });
    xpc_connection_resume(peer);
}
int check_mach_service(char *ServiceName){
    mach_port_t service_port;
    service_port = MACH_PORT_NULL;
    kern_return_t kr;
    kr = 0;
    kr = bootstrap_look_up(bootstrap_port, ServiceName, &service_port);
    printf(“Service Port: %d (%x)\n”, service_port, kr);
    if(service_port != 0){
        printf(“Mach Service is Accessible:%s\n\n”, ServiceName);
        printf(“Allowing to continue request..\n\n”);
        return 1;
    } else {
        printf(“Unaccessible mach service..“);
        exit(0);
        return 0;
    }
}
void send_xpc_msg(char *Servicename, char *first_msg, char *second_msg){
    xpc_connection_t conn;
    xpc_object_t msg;

    printf(“%s”, Servicename);
    msg = xpc_dictionary_create(NULL, NULL, 0);
    xpc_dictionary_set_string(msg, first_msg, second_msg);
    conn = xpc_connection_create_mach_service(Servicename, NULL, 0);
    conn = xpc_connection_create_mach_service(Servicename, NULL, 0);
    if (conn == NULL) {
        perror(“xpc_connection_create_mach_service”);
        exit(1);
    }
    xpc_connection_set_event_handler(conn, ^(xpc_object_t obj) {
        printf(“Received message in generic event handler: %p\n”, obj);
        printf(“%s\n”, xpc_copy_description(obj));
    });
    xpc_connection_resume(conn);
    xpc_connection_send_message(conn, msg);
    xpc_connection_send_message_with_reply(conn, msg, NULL, ^(xpc_object_t resp) {
        printf(“Received second message: %p\n”, resp);
        printf(“%s\n”, xpc_copy_description(resp));
    });
    xpc_connection_send_message_with_reply(conn, msg, NULL, ^(xpc_object_t resp) {
        printf(“Received third message: %p\n”, resp);
        printf(“%s\n”, xpc_copy_description(resp));
    });
    dispatch_main();
}
int main(int argc, char *argv[]){;
    int active;
    if (argc < 3) {
        fprintf(stderr, “Usage: %s <mach service name> %s <service_string> %s <command_string>“, argv[0], argv[1], argv[2]);
        return (1);
        }
    active = check_mach_service(argv[1]);
    if(active = 1){
        send_xpc_msg(argv[1], argv[2], argv[3]);
    }
}
