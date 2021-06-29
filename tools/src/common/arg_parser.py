import sys


class ArgParser:

    def __init__(self):
        self.args = sys.argv[1:]        

    def is_arg_present(self, a: str) -> bool:
        return a in self.args

    def get_arg_value(self, a: str) -> str:
        if a in self.args:
            idx = self.args.index(a)
            if idx + 1 < len(self.args):
                return self.args[idx+1]
            else:
                print("{} is the last argument, value not found.".format(a), file=sys.stderr)
        else:
            print("{} is not in the arguments list.".format(a), file=sys.stderr)
            
        return None
