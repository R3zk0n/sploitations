from os import name
import sark
import idaapi
# Please wait till ida has finished anaysis...
def read_functions():
    with open("C:\\Users\\student\\my_idas\\vulns.txt") as vulns:
        content = vulns.readlines();
    content = [x.strip() for x in content]
    return content
def get_function(vuln):
    func = sark.Line(name=vuln)
    for xref in sark.Line().xrefs_from:
        print(xref)
        sark.Line(xref.to).color = 0x8833EE
    for xref in sark.Line().xrefs_to:
        print(xref)
        sark.Line(xref.frm).color = 0x8833FF
# Get A list of known vulnerable functions..
#vulnerable_functions =
# Get the current function
#strcpy = sark.Function()
#strcpy.name = "strcpy";
#for xref in sark.Line().xrefs_from:
#    print(xref)
#    sark.Line(xref.frm).color = 0x8833FF
if __name__ == "__main__":
    test = read_functions();
    for i in test:
        print(i)
        get_function(i)
