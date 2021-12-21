import pathlib
import pathlib
import re

from strongarm.cli.utils import disassemble_method, disassemble_function
from strongarm.macho import MachoParser, MachoAnalyzer, VirtualMemoryPointer
from strongarm.objc import *

#Todo: Implement Denises bugs in this.
#

# Provide a directory..
#for objc_cls in analyzer.objc_classes():
 #   for objc_sel in objc_cls.selectors:
  #      list_search = re.search('listener:([a-zA-Z0-9+/]+)', objc_sel.name)
   #     if list_search:
    #        clean = list_search.group(1)
     #       print("FOUND XPC_Should_Accept:, File: {}\n".format(macho_bin))
      #      # dis_str = disassemble_method(binary, objc_sel.name)
       #     print(f'\tmethod: {objc_sel.name} @ {hex(objc_sel.implementation)}')
        #    for x in analyzer.get_objc_methods():
         #       if x.objc_sel.name == "listener:shouldAcceptNewConnection:":
          #          print("Found: {}".format(x.objc_sel.name))
           #         dis = disassemble_method(binary, x)
            #        print(dis)
#for x in analyzer.get_objc_methods()



def function_use(macho_bin):
    analyzer = MachoAnalyzer.get_analyzer(binary)




def xpc_get_string_basic(macho_bin):
    sel_name = []
    try:
        parser = MachoParser(pathlib.Path(macho_bin))
        binary = parser.get_arm64_slice();
        analyzer = MachoAnalyzer.get_analyzer(binary)
        get_string_symbol = f'_xpc_dictionary_get_string'
        xpc_symbol = analyzer.callable_symbol_for_symbol_name(get_string_symbol)
        if not xpc_symbol:
            raise ValueError("Appears to not used!")
        for xref in analyzer.calls_to(xpc_symbol.address):
            print('Found call to _xpc_dictionary_get_string: {} at 0x{}'.format(xpc_symbol.address, xref.caller_addr))

            function_anaylzer = ObjcFunctionAnalyzer.get_function_analyzer(binary, xref.caller_func_start_address)
            call_instr = ObjcInstruction.parse_instruction(
                function_anaylzer,
                function_anaylzer.get_instruction_at_address(xref.caller_addr)
            )
          #  print(f"Binary: {macho_bin.name}")
          #  print(function_anaylzer)
          #  print(f"Function Start Address: {function_anaylzer.start_address} - End Address: {function_anaylzer.end_address}")
          #  print(function_anaylzer)
          #  disassemble = disassemble_function(binary, function_anaylzer.start_address)
          #  print(disassemble)






    except Exception as macho_err:
        print(macho_err)




def xpc_get_string(macho_bin):
    sel_name = []
    try:
        parser = MachoParser(pathlib.Path(macho_bin))
        binary = parser.get_arm64_slice();
        analyzer = MachoAnalyzer.get_analyzer(binary)
      # test = analyzer.string_xrefs_to('command')
      # print(test)

        imported_symbols = analyzer.imported_symbols_to_symbol_names
        for symbol_ptr, symbol_name in imported_symbols.items():
            mach_strings = re.search('xpc.dictionary_get_string*\w+', symbol_name)
            if mach_strings:
                print("{}:xpc.dictionary_get_string".format(symbol_ptr))
                get_string_calls = analyzer.callable_symbol_for_address(symbol_ptr)
                print(get_string_calls)




    except Exception as macho_err:
        print(macho_err)



#def xpc_get_string(macho_bin):
#    sel_name = []
#    try:
#        parser = MachoParser(pathlib.Path(macho_bin))
#        binary = parser.get_arm64_slice();
#        analyzer = MachoAnalyzer.get_analyzer(binary)
#        for imp_sym in analyzer.imported_symbols:
#            mach_strings = re.search('xpc.dictionary_get_string*\w+', imp_sym)
#            if mach_strings:
#               print("Found XPC Function: {}".format(mach_strings.group(0)))
#                print("Import Symbols: {}".format(analyzer.imported_symbols_to_symbol_names))





def xpc_construct(macho_bin):
    sel_name = []
    try:
        parser = MachoParser(pathlib.Path(macho_bin))
        binary = parser.get_arm64_slice();
        analyzer = MachoAnalyzer.get_analyzer(binary)
        for imp_sym in analyzer.imported_symbols:
            mach_strings = re.search('_xpc.*\w+', imp_sym)
            if mach_strings:
                print("Found XPC Function: {}".format(mach_strings.group(0)))
    except Exception as macho_err:
        print(macho_err)



def xpc_should_accept(macho_bin):
    sel_name = []
    try:
        parser = MachoParser(pathlib.Path(macho_bin))
        binary = parser.get_arm64_slice();
        analyzer = MachoAnalyzer.get_analyzer(binary)
        for objc_cls in analyzer.objc_classes():
            for objc_sel in objc_cls.selectors:
                list_search = re.search('listener:([a-zA-Z0-9+/]+)', objc_sel.name)
                if list_search:
                    clean = list_search.group(1)
                    print("FOUND XPC_Should_Accept:, File: {}\n".format(macho_bin))
                    #dis_str = disassemble_method(binary, objc_sel.name)
                    print(f'\tmethod: {objc_sel.name} @ {hex(objc_sel.implementation)}')
                    for x in analyzer.get_objc_methods():
                        if x.objc_sel.name == "listener:shouldAcceptNewConnection:":
                            print("Found: {}".format(x.objc_sel.name))
                            dis = disassemble_method(binary, x)
                            print(dis)
                        if x.objc_sel.name == 'xpc_connection_create_mach_service':
                            print("Mach: {}".format(x.objc_sel.name))

                    #disassemble_function(binary, hex(objc_sel.name))
                    for objc_ivar in objc_cls.ivars:
                        print(f'\tivar: {objc_ivar.name}{objc_ivar.class_name}')

        protocols = analyzer.get_conformed_protocols()
        for proto in protocols:
            print("[+]Protocol:{}".format(proto.name))

    except Exception as macho_err:
        print(macho_err)

                # if protocol:
                 #   print("Found Protocol")
                 #   print(f'\tmethod: {objc_sel.name} @ {hex(objc_sel.implementation)}')

                #print(f'\tmethod: {objc_sel.name} @ {hex(objc_sel.implementation)}')





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pathlist = pathlib.Path('/Volumes/SSD-TB1/iPhone/nehelper_iOS').glob('*')
    for file in pathlist:
        print("Parsing: {}\n".format(file))
        xpc_get_string_basic(file)

