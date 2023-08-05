import json
import sys

from py_loans.cli import parser
from py_loans.loan import IllustrativeMortgage


if __name__ == "__main__":
    args = parser.parse_args()
    if args.string == "-":
        string = sys.stdin.read()
    else:
        string = args.string

    kwargs = json.loads(string)

    print(IllustrativeMortgage(**kwargs).calculate().model_dump_json())
