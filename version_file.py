import sys

project = sys.argv[1]

file = "C:\\Users\\Jenkins\\AppData\\Local\\Jenkins\\.jenkins\\versions\\{}_current_version.txt".format(project)

try:
    f = open(file, "r")

    versions = f.read().split(".")
    
    try:
        match sys.argv[2]:
            case 'main':
                versions[1] = int(versions[1]) + 1
                versions[2] = 0
            case 'major':
                versions[0] = int(versions[0]) + 1
                versions[1] = 0
                versions[2] = 0
            case _:
                versions[2] = int(versions[2]) + 1
    except:
        versions[2] = int(versions[2]) + 1
    
    f = open(file, "w")
    f.write("{}.{}.{}".format(versions[0], versions[1], versions[2]))
    f.close()
except IOError:
    f = open(file, 'x')
    f.write("0.0.0")
    f.close()