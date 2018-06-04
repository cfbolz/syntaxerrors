import os
import sys
import shutil
import subprocess

FILELIST = [
    ("astconsts.py", "../astcompiler/consts.py"),
    "error.py",
    ("parsefuture.py", "future.py"),
    "pygram.py",
    "pytokenize.py",
    "pytoken.py",
    "automata.py",
    "gendfa.py",
    "pylexer.py",
    "metaparser.py",
    "parser.py",
    "pyparse.py",
    "pytokenizer.py",
]

TESTLIST = [
    "test_automata.py",
    "test_future.py",
    "test_gendfa.py",
    "test_metaparser.py",
    "test_pytokenizer.py",
    "test_parser.py",
    "test_pyparse.py",
]


TARGET = os.path.join(os.path.dirname(__file__), "src", "syntaxerrors")
TARGETTEST = os.path.join(os.path.dirname(__file__), "tests")


def main():
    pypydir = sys.argv[1]
    assert os.path.isdir(pypydir)

    # check that no local changes
    subprocess.check_output("git diff --exit-code", shell=True)
    subprocess.check_output("git checkout pypy-import", shell=True)

    addfiles = ["PYPYREV"]

    for t in FILELIST:
        if isinstance(t, tuple):
            target, source = t
        else:
            target = source = t
        source = os.path.join(pypydir, "pypy", "interpreter", "pyparser", source)
        target = os.path.join(TARGET, target)
        shutil.copy(source, target)
        addfiles.append(target)

    for filename in TESTLIST:
        source = os.path.join(pypydir, "pypy", "interpreter", "pyparser", "test", filename)
        target = os.path.join(TARGETTEST, filename)
        shutil.copy(source, target)
        addfiles.append(target)

    rev = subprocess.check_output("hg id -i", shell=True, cwd=pypydir)
    print rev
    with open("PYPYREV", "w") as f:
        f.write(rev)
    subprocess.check_output("git add " + " ".join(addfiles), shell=True)
    subprocess.check_output('git commit -m "updated PyPy files to %s"' % rev.strip(), shell=True)

if __name__ == '__main__':
    main()
