import pathlib
import pathlib
import re

from strongarm.cli.utils import disassemble_method
from strongarm.macho import MachoParser, MachoAnalyzer


# Provide a directory..


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
    pathlist = pathlib.Path('').glob('*')
    for file in pathlist:
        print("Parsing: {}\n".format(file))
        xpc_construct(file)
        xpc_should_accept(file)
